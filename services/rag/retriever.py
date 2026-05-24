from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional

from connect_model import get_request_model_config
from .embeddings import embed_texts
from .supabase_client import get_supabase_client

def extract_storage_paths_from_text(text: str) -> List[str]:
    if not text:
        return []
    matches = re.findall(r"[\"']((?!https?://)[^\"']+/[^\"']+)[\"']", text)
    if not matches:
        matches = re.findall(r"(?!https?://)\b[\w\-./]+/[\w\-./]+\b", text)
    return sorted(set(matches))


def retrieve_rag_context(
    *,
    query: str,
    storage_paths: List[str],
    top_k: int = 5,
) -> str:
    storage_paths = [p for p in storage_paths if p]
    if not query or not storage_paths:
        return ""

    embedding = embed_texts([query])[0]
    supabase = get_supabase_client()

    result = supabase.rpc(
        "match_rag_chunks",
        {
            "query_embedding": embedding,
            "match_count": top_k,
            "min_similarity": 0.0,
        },
    ).execute()

    rows: List[Dict[str, Any]] = result.data or []
    if not rows:
        return ""

    collected: List[str] = []

    for row in rows:
        content = row.get("content", "")
        if not content:
            continue

        source = row.get("document_type") or row.get("file_id") or "unknown"
        chunk_index = row.get("chunk_index", 0)
        snippet = f"### Source: {source} (chunk {chunk_index})\n{content}".strip()

        collected.append(snippet)

    return "\n\n".join(collected).strip()
