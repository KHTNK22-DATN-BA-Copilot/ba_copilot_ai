from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

from .tokenizer import estimate_tokens, trim_text_to_tokens


@dataclass(frozen=True)
class RagChunk:
    text: str
    token_count: int


def _split_into_paragraphs(text: str) -> List[str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", normalized) if p.strip()]
    return paragraphs


def _split_long_paragraph(paragraph: str, max_tokens: int) -> List[str]:
    # Try sentence-based split first
    sentences = re.split(r"(?<=[.!?])\s+", paragraph)
    if len(sentences) == 1:
        # Fallback to hard trimming
        return [trim_text_to_tokens(paragraph, max_tokens)]

    chunks: List[str] = []
    current: List[str] = []
    current_tokens = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        sentence_tokens = estimate_tokens(sentence)
        if sentence_tokens > max_tokens:
            if current:
                chunks.append(" ".join(current))
                current = []
                current_tokens = 0
            chunks.append(trim_text_to_tokens(sentence, max_tokens))
            continue

        if current_tokens + sentence_tokens > max_tokens and current:
            chunks.append(" ".join(current))
            current = [sentence]
            current_tokens = sentence_tokens
        else:
            current.append(sentence)
            current_tokens += sentence_tokens

    if current:
        chunks.append(" ".join(current))

    return chunks


def chunk_text(
    text: str,
    max_tokens: int = 700,
    overlap_tokens: int = 120,
) -> List[RagChunk]:
    paragraphs = _split_into_paragraphs(text)
    if not paragraphs:
        return []

    chunks: List[RagChunk] = []
    current_parts: List[str] = []
    current_tokens = 0

    def flush_chunk() -> None:
        nonlocal current_parts, current_tokens
        if not current_parts:
            return
        chunk_text_value = "\n\n".join(current_parts).strip()
        token_count = estimate_tokens(chunk_text_value)
        chunks.append(RagChunk(text=chunk_text_value, token_count=token_count))
        current_parts = []
        current_tokens = 0

    for paragraph in paragraphs:
        paragraph_tokens = estimate_tokens(paragraph)

        if paragraph_tokens > max_tokens:
            for part in _split_long_paragraph(paragraph, max_tokens):
                part_tokens = estimate_tokens(part)
                if current_tokens + part_tokens > max_tokens and current_parts:
                    flush_chunk()
                current_parts.append(part)
                current_tokens += part_tokens
                if current_tokens >= max_tokens:
                    flush_chunk()
            continue

        if current_tokens + paragraph_tokens > max_tokens and current_parts:
            flush_chunk()

        current_parts.append(paragraph)
        current_tokens += paragraph_tokens

    flush_chunk()

    if overlap_tokens <= 0 or len(chunks) <= 1:
        return chunks

    overlapped: List[RagChunk] = []
    for index, chunk in enumerate(chunks):
        if index == 0:
            overlapped.append(chunk)
            continue
        overlap_text = trim_text_to_tokens(chunks[index - 1].text, overlap_tokens)
        merged_text = f"{overlap_text}\n\n{chunk.text}".strip()
        overlapped.append(RagChunk(text=merged_text, token_count=estimate_tokens(merged_text)))

    return overlapped
