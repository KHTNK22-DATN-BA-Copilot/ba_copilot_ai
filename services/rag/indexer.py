from __future__ import annotations

import hashlib
from typing import Dict, List, Optional

from .chunker import chunk_text
from .embeddings import embed_texts
from .supabase_client import get_supabase_client
from .tokenizer import estimate_tokens


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _build_rows(
    *,
    chunks: List[str],
    embeddings: List[List[float]],
    storage_key: str,
    storage_path: Optional[str],
    storage_md_path: Optional[str],
    file_id: Optional[str],
    project_id: Optional[int],
    created_by: Optional[int],
) -> List[Dict]:
    rows: List[Dict] = []

    for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        rows.append(
            {
                "storage_key": storage_key,
                "storage_path": storage_path,
                "storage_md_path": storage_md_path,
                "file_id": file_id,
                "project_id": project_id,
                "created_by": created_by,
                "chunk_index": index,
                "content": chunk,
                "token_count": estimate_tokens(chunk),
                "content_hash": _hash_text(chunk),
                "embedding": embedding,
            }
        )

    return rows


def index_rag_content(
    *,
    content: str,
    storage_path: Optional[str],
    storage_md_path: Optional[str],
    file_id: Optional[str],
    project_id: Optional[int],
    created_by: Optional[int],
    max_tokens: int = 700,
    overlap_tokens: int = 120,
) -> Dict[str, int]:
    if not content:
        return {"chunks": 0}

    storage_key = storage_md_path or storage_path
    if not storage_key:
        raise ValueError("Missing storage path for RAG indexing")

    supabase = get_supabase_client()

    chunks = chunk_text(content, max_tokens=max_tokens, overlap_tokens=overlap_tokens)
    chunk_texts = [chunk.text for chunk in chunks]
    if not chunk_texts:
        return {"chunks": 0}

    embeddings = embed_texts(chunk_texts)
    rows = _build_rows(
        chunks=chunk_texts,
        embeddings=embeddings,
        storage_key=storage_key,
        storage_path=storage_path,
        storage_md_path=storage_md_path,
        file_id=file_id,
        project_id=project_id,
        created_by=created_by,
    )

    # Clear existing chunks for this file before inserting new content
    supabase.table("rag_chunks").delete().eq("storage_key", storage_key).execute()

    batch_size = 100
    for i in range(0, len(rows), batch_size):
        supabase.table("rag_chunks").insert(rows[i : i + batch_size]).execute()

    return {"chunks": len(rows)}
