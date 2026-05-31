from __future__ import annotations
import os
from typing import List
from openai import OpenAI

OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://api.openrouter.ai/v1")
OPENROUTER_EMBEDDING_MODEL = os.getenv("OPENROUTER_EMBEDDING_MODEL", "text-embedding-3-small")

def embed_texts(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []

    client = OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=OPEN_ROUTER_API_KEY or None,
    )

    response = client.embeddings.create(
        model=OPENROUTER_EMBEDDING_MODEL,
        input=texts,
        dimensions=1536,
    )
    return [item.embedding for item in response.data]
