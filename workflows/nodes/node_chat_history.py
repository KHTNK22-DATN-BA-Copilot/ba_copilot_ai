# workflows/nodes/node_chat_history.py
import os
import httpx
from openai import OpenAI
from typing import TypedDict, List, Dict, Any

# Load API key from environment
OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY", "")
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8010")

# Model token limits
MODEL_TOKEN_LIMITS = {
    "tngtech/deepseek-r1t2-chimera:free": 8000,
    "default": 4000
}

class ChatMessage(TypedDict):
    role: str
    message: str
    created_at: str


async def fetch_chat_history(document_id: str) -> List[ChatMessage]:
    """
    Fetch chat history from backend API

    Args:
        document_id: The document ID to fetch history for

    Returns:
        List of chat messages
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{BACKEND_API_URL}/api/v1/srs/history/{document_id}"
            )
            response.raise_for_status()
            data = response.json()
            return data.get("history", [])
    except Exception as e:
        print(f"Error fetching chat history: {e}")
        return []


def estimate_tokens(text: str) -> int:
    """
    Estimate token count (rough approximation: 1 token ≈ 4 characters)

    Args:
        text: The text to estimate tokens for

    Returns:
        Estimated token count
    """
    return len(text) // 4


def summarize_chat_history(history: List[ChatMessage], model: str = "tngtech/deepseek-r1t2-chimera:free") -> str:
    """
    Summarize chat history using AI model

    Args:
        history: List of chat messages
        model: AI model to use for summarization

    Returns:
        Summarized chat history
    """
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )

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

        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "BA-Copilot",
            },
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return completion.choices[0].message.content

    except Exception as e:
        print(f"Error summarizing chat history: {e}")
        # Return truncated history as fallback
        return "\n".join([
            f"{msg['role']}: {msg['message'][:100]}..."
            for msg in history[-5:]  # Last 5 messages
        ])


def format_chat_context(history: List[ChatMessage], max_tokens: int = 2000) -> str:
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
    estimated_tokens = estimate_tokens(formatted)

    if estimated_tokens > max_tokens:
        print(f"Chat history exceeds token limit ({estimated_tokens} > {max_tokens}), summarizing...")
        summary = summarize_chat_history(history)
        return f"Previous conversation summary:\n{summary}"

    return f"Previous conversation:\n{formatted}"


def get_chat_history(state: Dict[str, Any], model: str = "tngtech/deepseek-r1t2-chimera:free") -> Dict[str, Any]:
    """
    Node function to fetch and process chat history

    Args:
        state: Current workflow state containing document_id
        model: AI model being used (for token limit calculation)

    Returns:
        Updated state with chat_context
    """
    document_id = state.get("document_id")

    if not document_id:
        print("No document_id provided, skipping chat history")
        state["chat_context"] = ""
        return state

    # Try to fetch chat history from backend
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        history = loop.run_until_complete(fetch_chat_history(document_id))
        loop.close()

        # Get token limit for model
        token_limit = MODEL_TOKEN_LIMITS.get(model, MODEL_TOKEN_LIMITS["default"])

        # Reserve 50% of tokens for chat context
        max_context_tokens = token_limit // 2

        # Format and add to state
        chat_context = format_chat_context(history, max_context_tokens)
        state["chat_context"] = chat_context

        print(f"Chat history processed: {len(history)} messages, {estimate_tokens(chat_context)} tokens")
    except Exception as e:
        print(f"Failed to fetch chat history: {e}. Continuing without history context.")
        state["chat_context"] = ""

    return state
