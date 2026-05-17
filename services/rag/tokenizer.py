from __future__ import annotations

from typing import Optional


def estimate_tokens(text: str, model: Optional[str] = None) -> int:
    if not text:
        return 0

    try:
        import tiktoken

        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        # Fallback approximation: 4 chars per token
        return max(1, len(text) // 4)


def trim_text_to_tokens(text: str, max_tokens: int) -> str:
    if max_tokens <= 0 or not text:
        return ""

    try:
        import tiktoken

        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        trimmed = tokens[:max_tokens]
        return encoding.decode(trimmed)
    except Exception:
        approx_len = max_tokens * 4
        return text[:approx_len]
