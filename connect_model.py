# connect_model.py
"""
Centralized AI Model Connection Module

This module provides a unified interface for connecting to AI models via OpenRouter.
All workflow files should import from this module to maintain consistency and reusability.
"""

import os
from typing import Optional, Dict, List, Any
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load API configuration from environment
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")  
OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY", "")
OPENROUTER_REFERER = os.getenv("OPENROUTER_REFERER", "http://localhost:8000")
OPENROUTER_TITLE = os.getenv("OPENROUTER_TITLE", "BA-Copilot")
MODEL = os.getenv("MODEL", "tngtech/deepseek-r1t2-chimera:free")
MAX_CONTEXT_TOKENS = int(os.getenv("MAX_CONTEXT_TOKENS", "4096"))

class ModelClient:
    """
    Singleton-like model client for managing OpenRouter AI connections.

    This class provides a centralized way to create and manage AI model connections,
    ensuring consistent configuration across all workflows.
    """

    _instance: Optional["ModelClient"] = None
    _client: Optional[OpenAI] = None

    def __new__(cls) -> "ModelClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._client = self._create_client()

    def _create_client(self) -> OpenAI:
        """Create and return an OpenAI client configured for OpenRouter."""
        if not OPENROUTER_API_KEY:
            raise ValueError(
                "OPEN_ROUTER_API_KEY environment variable is not set. "
                "Please set it in your .env file."
            )

        return OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY,
        )

    @property
    def client(self) -> OpenAI:
        """Get the OpenAI client instance."""
        if self._client is None:
            self._client = self._create_client()
        return self._client

    def get_extra_headers(self) -> Dict[str, str]:
        """Get the extra headers required for OpenRouter API calls."""
        return {
            "HTTP-Referer": OPENROUTER_REFERER,
            "X-Title": OPENROUTER_TITLE,
        }

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = MODEL,
        **kwargs: Any
    ) -> Any:
        """
        Create a chat completion using the configured client.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys.
            model: The model to use for completion. Defaults to DEFAULT_MODEL.
            **kwargs: Additional arguments to pass to the API.

        Returns:
            The completion response from the API.
        """
        return self.client.chat.completions.create(
            extra_headers=self.get_extra_headers(),
            model=model,
            messages=messages,
            **kwargs
        )


# Global instance for easy access
_model_client: Optional[ModelClient] = None


def get_model_client() -> ModelClient:
    """
    Get the global ModelClient instance.

    Returns:
        The singleton ModelClient instance.
    """
    global _model_client
    if _model_client is None:
        _model_client = ModelClient()
    return _model_client


def create_chat_completion(
    prompt: str,
    model: str = MODEL,
    system_message: Optional[str] = None
) -> str:
    """
    Convenience function to create a chat completion with a single prompt.

    Args:
        prompt: The user prompt/message.
        model: The model to use. Defaults to DEFAULT_MODEL.
        system_message: Optional system message to prepend.

    Returns:
        The content of the completion response.
    """
    client = get_model_client()

    messages: List[Dict[str, str]] = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})

    completion = client.chat_completion(messages=messages, model=model)
    return completion.choices[0].message.content or ""


def get_token_limit(model: str = MODEL) -> int:
    """
    Get the token limit for a specific model.

    Args:
        model: The model identifier.

    Returns:
        The token limit for the model.
    """
    return MAX_CONTEXT_TOKENS


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for a given text.

    Rough approximation: 1 token ~ 4 characters.

    Args:
        text: The text to estimate tokens for.

    Returns:
        Estimated token count.
    """
    return len(text) // 4


def is_configured() -> bool:
    """
    Check if the model client 
    is properly configured.

    Returns:
        True if the API key is set, False otherwise.
    """
    return bool(OPENROUTER_API_KEY)
