from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional

from connect_model import get_request_model_config
from .embeddings import embed_texts
from .supabase_client import get_supabase_client
from .tokenizer import estimate_tokens

MODEL_CONTEXT_LIMITS = {
    "gpt-4o-mini": 128000,
    "gemini-2.5-flash-lite": 128000,
    "claude-3.5-sonnet-latest": 200000,
    "anthropic/claude-3.5-sonnet": 200000,
}


def _resolve_model_context_limit() -> int:
    cfg = get_request_model_config()
    model_name = (cfg.get("model_name") or os.getenv("MODEL", "")).strip()
    if model_name in MODEL_CONTEXT_LIMITS:
        return MODEL_CONTEXT_LIMITS[model_name]
    return int(os.getenv("MAX_CONTEXT_TOKENS", "100000"))


def _resolve_rag_context_budget() -> int:
    env_override = os.getenv("RAG_MAX_CONTEXT_TOKENS")
    if env_override:
        try:
            return int(env_override)
        except ValueError:
            pass

    fraction = float(os.getenv("RAG_CONTEXT_FRACTION", "0.15"))
    max_tokens = _resolve_model_context_limit()
    return max(500, int(max_tokens * fraction))


def extract_storage_paths_from_text(text: str) -> List[str]:
    if not text:
        return []
    matches = re.findall(r"(?:uploads/|/)[\w\-./]+", text)
    return sorted(set(matches))


def retrieve_rag_context(
    *,
    query: str,
    storage_paths: List[str],
    top_k: int = 4,
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
            "storage_keys": storage_paths,
            "min_similarity": 0.0,
        },
    ).execute()

    rows: List[Dict[str, Any]] = result.data or []
    if not rows:
        return ""

    token_budget = _resolve_rag_context_budget()
    collected: List[str] = []
    used_tokens = 0

    for row in rows:
        content = row.get("content", "")
        if not content:
            continue

        source = row.get("storage_key") or row.get("storage_path") or "unknown"
        chunk_index = row.get("chunk_index", 0)
        snippet = f"### Source: {source} (chunk {chunk_index})\n{content}".strip()
        snippet_tokens = estimate_tokens(snippet)

        if used_tokens + snippet_tokens > token_budget:
            continue

        collected.append(snippet)
        used_tokens += snippet_tokens

    return "\n\n".join(collected).strip()
