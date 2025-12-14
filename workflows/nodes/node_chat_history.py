# workflows/nodes/node_chat_history.py
import os
import sys
import httpx
from typing import TypedDict, List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from connect_model import (
    get_model_client,
    MODEL,
    MAX_CONTEXT_TOKENS,
    estimate_tokens as _estimate_tokens
)

BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8010")

class ChatMessage(TypedDict):
    role: str
    message: str
    created_at: str


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
                f"{BACKEND_API_URL}/api/v1/sessions/list/{content_id}"
            )
            response.raise_for_status()
            data = response.json()
            print(f"Fetched chat history: {data}")
            return data.get("history", [])
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

        # Format chat history for summarization
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
                    "content": prompt
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


def format_chat_context(history: List[ChatMessage], max_tokens: int = MAX_CONTEXT_TOKENS) -> str:
    """
    Format chat history into context string, summarizing if necessary

    Args:
        history: List of chat messages
        max_tokens: Maximum tokens allowed for context

    Returns:
        Formatted chat context
    """
    if not history:
        return ""

    # Format full history
    formatted = "\n".join([
        f"{msg['role']} ({msg['created_at']}): {msg['message']}"
        for msg in history
    ])

    # Check if it exceeds token limit
    estimated_tokens = _estimate_tokens(formatted)

    if estimated_tokens > max_tokens:
        print(f"Chat history exceeds token limit ({estimated_tokens} > {max_tokens}), summarizing...")
        summary = summarize_chat_history(history)
        return f"Previous conversation summary:\n{summary}"

    return f"Previous conversation:\n{formatted}"


def get_chat_history(state: Dict[str, Any], model: str = MODEL) -> Dict[str, Any]:
    """
    Node function to fetch and process chat history

    Args:
        state: Current workflow state containing content_id
        model: AI model being used (for token limit calculation)

    Returns:
        Updated state with chat_context
    """
    content_id = state.get("content_id")

    if not content_id:
        print("No content_id provided, skipping chat history")
        state["chat_context"] = ""
        return state

    # Try to fetch chat history from backend
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        history = loop.run_until_complete(fetch_chat_history(content_id))
        loop.close()

        # Reserve 50% of tokens for chat context
        max_context_tokens = MAX_CONTEXT_TOKENS // 2

        # Format and add to state
        chat_context = format_chat_context(history, max_context_tokens)
        state["chat_context"] = chat_context

        print(f"Chat history processed: {len(history)} messages, {estimate_tokens(chat_context)} tokens")
    except Exception as e:
        print(f"Failed to fetch chat history: {e}. Continuing without history context.")
        state["chat_context"] = ""

    return state
