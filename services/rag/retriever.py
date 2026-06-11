from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import traceback
from .embeddings import embed_texts
from .supabase_client import get_rag_db

def retrieve_rag_context(
    *,
    query: str,
    project_id: int,
    document_constraint: List[str],
    top_k: int = 5,
) -> str:
    document_constraint = [p for p in document_constraint if p]
    if not query and project_id is None and not document_constraint:
        return ""

    rag_db_gen = None
    try:
        embedding = embed_texts([query])[0]
        # print(f"Query embedding: {embedding}... (truncated)")
        rag_db_gen = get_rag_db()
        rag_db = next(rag_db_gen)
        embedding_literal = "[" + ",".join(f"{value:.6f}" for value in embedding) + "]"
        # print(f"For query: {embedding_literal}")
        document_types_literal = "{" + ",".join(document_constraint) + "}"
        sql = text(
            """
            SELECT *
            FROM match_rag_chunks(
                CAST(:query_embedding AS vector),
                :match_count,
                :project_id_filter,
                CAST(:document_types AS text[]),
                :min_similarity
            )
            """
        )

        rows = (
            rag_db.execute(
                sql,
                {
                    "query_embedding": embedding_literal,
                    "match_count": top_k,
                    "project_id_filter": project_id,
                    "document_types": document_types_literal,
                    "min_similarity": 0.0,
                },
            )
            .mappings()
            .all()
        )
        print(f"Retrieved {len(rows)} RAG chunks for query: {query}")
    finally:
        if rag_db_gen is not None:
            rag_db_gen.close()

    rows_list: List[Dict[str, Any]] = [dict(row) for row in rows]
    if not rows_list:
        return ""

    collected: List[str] = []

    for row in rows_list:
        content = row.get("content", "")
        if not content:
            continue

        source = row.get("document_type") or row.get("file_id") or "stakeholder_requirements"
        chunk_index = row.get("chunk_index", 0)
        snippet = f"### Source: {source} (chunk {chunk_index})\n{content}".strip()

        collected.append(snippet)

    return "\n\n".join(collected).strip()
