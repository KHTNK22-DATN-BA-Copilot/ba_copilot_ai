from typing import Optional
import tiktoken

def estimate_tokens(text: str, model: Optional[str] = None) -> int:
    if not text:
        return 0

    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        # Fallback approximation: 4 chars per token
        return max(1, len(text) // 4)
