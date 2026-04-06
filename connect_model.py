# connect_model.py
"""
Centralized AI Model Connection Module

This module provides a unified interface for connecting to AI models.
All workflow files import from here, so request-scoped BYOK can be applied globally.
"""

import os
from contextvars import ContextVar, Token
from types import SimpleNamespace
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from factory import create_chat_model

# Load environment variables
load_dotenv()

# Load API configuration from environment
MODEL = os.getenv("MODEL", "gemini-2.5-flash-lite")
MAX_CONTEXT_TOKENS = int(os.getenv("MAX_CONTEXT_TOKENS", "4096"))

# Request-scoped model settings (BYOK + provider/model selection).
_request_model_config: ContextVar[Dict[str, str]] = ContextVar("request_model_config", default={})


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = value.strip()
    return normalized if normalized else None


def set_request_model_config(
    provider: Optional[str] = None,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Token:
    cfg: Dict[str, str] = {}
    cleaned_provider = _clean(provider)
    cleaned_model_name = _clean(model_name)
    cleaned_api_key = _clean(api_key)

    if cleaned_provider:
        cfg["provider"] = cleaned_provider
    if cleaned_model_name:
        cfg["model_name"] = cleaned_model_name
    if cleaned_api_key:
        cfg["api_key"] = cleaned_api_key

    return _request_model_config.set(cfg)


def reset_request_model_config(token: Token) -> None:
    _request_model_config.reset(token)


def get_request_model_config() -> Dict[str, str]:
    return dict(_request_model_config.get())


class ModelClient:
    """
    Singleton-like model client for managing AI model calls.

    The instance itself is shared, but model/key selection stays request-scoped via
    ContextVar, so concurrent requests do not leak credentials.
    """

    _instance: Optional["ModelClient"] = None

    def __new__(cls) -> "ModelClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def _resolve_config(
        self,
        default_provider: str,
        default_model: str,
        explicit_model: Optional[str] = None,
    ) -> Dict[str, str]:
        cfg = get_request_model_config()

        provider = _clean(cfg.get("provider")) or default_provider
        model_name = _clean(cfg.get("model_name")) or _clean(explicit_model) or default_model
        api_key = _clean(cfg.get("api_key"))

        return {
            "provider": provider,
            "model_name": model_name,
            "api_key": api_key or "",
        }

    @staticmethod
    def _to_langchain_messages(messages: List[Dict[str, str]]) -> List[Any]:
        converted: List[Any] = []
        for message in messages:
            role = (message.get("role") or "").strip().lower()
            content = message.get("content", "")

            if role == "system":
                converted.append(SystemMessage(content=content))
            elif role == "assistant":
                converted.append(AIMessage(content=content))
            else:
                converted.append(HumanMessage(content=content))

        return converted

    @staticmethod
    def _extract_text(response: Any) -> str:
        content = getattr(response, "content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            chunks: List[str] = []
            for item in content:
                if isinstance(item, str):
                    chunks.append(item)
                elif isinstance(item, dict):
                    text = item.get("text")
                    if isinstance(text, str):
                        chunks.append(text)
            return "\n".join(chunk for chunk in chunks if chunk)
        return str(content) if content is not None else ""

    @staticmethod
    def _to_openai_compatible_response(text: str) -> Any:
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=text)
                )
            ]
        )

    def _build_llm(
        self,
        provider: str,
        model_name: str,
        api_key: Optional[str],
        **kwargs: Any,
    ) -> Any:
        """Build LangChain chat model using centralized factory.
        
        Delegates to factory.create_chat_model() which handles all provider-specific
        configuration including OpenRouter headers from environment variables.
        """
        return create_chat_model(
            provider=provider,
            model_name=model_name,
            api_key=api_key,
            **kwargs,
        )

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
        resolved = self._resolve_config(
            default_provider="google",
            default_model=model,
            explicit_model=model,
        )
        llm = self._build_llm(
            provider=resolved["provider"],
            model_name=resolved["model_name"],
            api_key=resolved.get("api_key"),
            **kwargs,
        )
        lc_messages = self._to_langchain_messages(messages)
        response = llm.invoke(lc_messages)
        text = self._extract_text(response)
        return self._to_openai_compatible_response(text)

    def gemini_completion(self, prompt: str, model: str = "gemini-2.5-flash-lite") -> str:
        resolved = self._resolve_config(
            default_provider="google",
            default_model=model,
            explicit_model=model,
        )
        llm = self._build_llm(
            provider=resolved["provider"],
            model_name=resolved["model_name"],
            api_key=resolved.get("api_key"),
        )
        response = llm.invoke(prompt)
        return self._extract_text(response)


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
    return bool(
        _clean(os.getenv("GOOGLE_GEMINI_API_KEY"))
        or _clean(os.getenv("GOOGLE_AI_API_KEY"))
        or _clean(os.getenv("OPEN_ROUTER_API_KEY"))
        or _clean(os.getenv("OPENROUTER_API_KEY"))
        or _clean(os.getenv("OPENAI_API_KEY"))
        or _clean(os.getenv("ANTHROPIC_API_KEY"))
    )
