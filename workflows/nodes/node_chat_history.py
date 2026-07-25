# workflows/nodes/node_chat_history.py
import os
import sys
import httpx
from typing import TypedDict, List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from connect_model import (
    get_model_client,
    MODEL,
    get_max_context_tokens,
)
from utils.tokenizer import estimate_tokens as _estimate_tokens

BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8010")

class ChatMessage(TypedDict):
    role: str
    message: str
    create_at: str


async def fetch_chat_history(content_id: str) -> List[ChatMessage]:
    """
    Fetch chat history from backend API

    Args:
        content_id: The content ID to fetch history for context

    Returns:
        List of chat messages
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{BACKEND_API_URL}/api/v1/sessions/list-ai/{content_id}"
            )
            response.raise_for_status()
            data = response.json()
            print(f"Fetched chat history: {data}")
            return data.get("Sessions", [])
    except Exception as e:
        print(f"Error fetching chat history: {e}")
        return []


def summarize_chat_history(history: List[ChatMessage], model: str = MODEL) -> str:
    """
    Summarize chat history using AI model

    Args:
        history: List of chat messages
        model: AI model to use for summarization

    Returns:
        Summarized chat history
    """
    try:
        model_client = get_model_client()

        formatted_history = "\n".join([
            f"{msg['role']}: {msg['message']}"
            for msg in history
        ])

        prompt = f"""
        Summarize the following conversation history concisely, preserving key information and context:

        {formatted_history}

        Provide a clear and concise summary that captures the main points and context.
        """

        completion = model_client.chat_completion(
            messages=[
                {
                    "role": "user",
                    "message": prompt
                }
            ],
            model=model
        )

        return completion.choices[0].message.content

    except Exception as e:
        print(f"Error summarizing chat history: {e}")
        # Return truncated history as fallback
        return "\n".join([
            f"{msg['role']}: {msg['message'][:100]}..."
            for msg in history[-5:]  # Last 5 messages
        ])


def _normalize_role(role: str) -> str:
    """Map backend roles to the two roles used downstream: 'ai' or 'user'."""
    normalized = (role or "").strip().lower()
    return "ai" if normalized in ("ai", "assistant") else "user"


def build_chat_messages(
    history: List[ChatMessage],
    max_tokens: int,
) -> List[Dict[str, str]]:
    """
    Turn raw chat history into a list of {"role", "message"} turns in chronological order.

    The backend `/list-ai` endpoint returns messages newest-first, so we reverse it.
    We ALWAYS take the full history first, then measure the total token count. Only if
    it exceeds ``max_tokens`` do we replace it with a single summarized turn — we never
    drop turns by breaking the loop.

    Args:
        history: List of chat messages from the backend (newest-first)
        max_tokens: Context-window budget (tokens) for the chat history

    Returns:
        List of {"role": "user"|"ai", "message": str} in chronological order
    """
    if not history:
        return []

    # Backend returns newest-first; reverse to chronological (oldest-first).
    messages: List[Dict[str, str]] = [
        {"role": _normalize_role(msg.get("role")), "message": msg.get("message", "")}
        for msg in reversed(history)
        if msg.get("message")
    ]

    if not messages:
        return []

    total_tokens = sum(_estimate_tokens(turn["message"]) for turn in messages)

    if max_tokens > 0 and total_tokens > max_tokens:
        print(f"Chat history exceeds token limit ({total_tokens} > {max_tokens}), summarizing...")
        summary = summarize_chat_history(messages)
        return [{"role": "ai", "message": f"Summary of previous conversation:\n{summary}"}]

    return messages


async def get_chat_history(state: Dict[str, Any], model: str = MODEL) -> Dict[str, Any]:
    """
    Node function to fetch and process chat history

    Args:
        state: Current workflow state containing content_id
        model: AI model being used (for token limit calculation)

    Returns:
        Updated state with chat_context as a list of {"role", "message"} turns
    """
    content_id = state.get("content_id")

    if not content_id:
        print("No content_id provided, skipping chat history")
        state["chat_context"] = []
        return state

    # Try to fetch chat history from backend
    try:
        history = await fetch_chat_history(content_id)

        # Reserve 50% of the provider's context window for chat history;
        # the rest is left for the system prompt, RAG context and the model output.
        max_context_tokens = get_max_context_tokens() // 2

        chat_context = build_chat_messages(history, max_context_tokens)
        state["chat_context"] = chat_context

        total_tokens = sum(_estimate_tokens(turn["message"]) for turn in chat_context)
        print(f"Chat history processed: {len(chat_context)} turns kept, {total_tokens} tokens")
    except Exception as e:
        print(f"Failed to fetch chat history: {e}. Continuing without history context.")
        state["chat_context"] = []

    return state