from __future__ import annotations
import os
from typing import List
from openai import OpenAI

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_API_BASE = os.getenv("OPENROUTER_API_BASE", "https://api.openrouter.ai/v1")
OPENROUTER_EMBEDDING_MODEL = os.getenv("OPENROUTER_EMBEDDING_MODEL", "text-embedding-3-large")

def embed_texts(texts: List[str]) -> List[List[float]]:
    if not (OPENAI_API_KEY or OPENROUTER_API_KEY):
        raise ValueError("Missing OPENAI_API_KEY or OPENROUTER_API_KEY for embeddings")

    # Note: Create a new client instance for OpenAI embeddings
    client = OpenAI(api_key=OPENROUTER_API_KEY, api_base=OPENROUTER_API_BASE)

    response = client.embeddings.create(model=OPENROUTER_EMBEDDING_MODEL, input=texts)
    return [item.embedding for item in response.data]
