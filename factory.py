"""Factory helpers for building request-scoped LangChain chat models.

Priority logic (BYOK + fallback):
1) Use ``api_key`` from request/config when provided.
2) Otherwise, use system key from environment variables.

This module is stateless and does not mutate process-wide environment variables,
so concurrent requests cannot leak keys across tenants.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

DEFAULT_PROVIDER = "google"
DEFAULT_MODEL_BY_PROVIDER = {
    "google": "gemini-2.5-flash-lite",
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-sonnet-latest",
    "openrouter": "anthropic/claude-3.5-sonnet",
    
}


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = value.strip()
    return normalized if normalized else None


def _resolve_api_key(provider: str, user_api_key: Optional[str]) -> str:
    cleaned_user_key = _clean(user_api_key)
    if cleaned_user_key:
        return cleaned_user_key

    if provider == "google":
        # Support both names for compatibility with existing environments.
        key = _clean(os.getenv("GOOGLE_GEMINI_API_KEY")) or _clean(os.getenv("GOOGLE_AI_API_KEY"))
        if key:
            return key
        raise ValueError("Missing API key for Google provider. Set GOOGLE_GEMINI_API_KEY or GOOGLE_AI_API_KEY.")

    if provider == "openai":
        key = _clean(os.getenv("OPENAI_API_KEY"))
        if key:
            return key
        raise ValueError("Missing API key for OpenAI provider. Set OPENAI_API_KEY.")

    if provider == "anthropic":
        key = _clean(os.getenv("ANTHROPIC_API_KEY"))
        if key:
            return key
        raise ValueError("Missing API key for Anthropic provider. Set ANTHROPIC_API_KEY.")

    if provider == "openrouter":
        key = (
            _clean(os.getenv("OPEN_ROUTER_API_KEY"))
            or _clean(os.getenv("OPENROUTER_API_KEY"))
        )
        if key:
            return key
        raise ValueError("Missing API key for OpenRouter provider. Set OPEN_ROUTER_API_KEY or OPENROUTER_API_KEY.")

    raise ValueError(f"Unsupported provider: {provider}")


def create_chat_model(
    provider: Optional[str] = None,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs: Any,
) -> BaseChatModel:
    """Create a provider-specific LangChain chat model.

    Args:
        provider: "google", "openai", "anthropic", or "openrouter". Defaults to Google.
        model_name: Optional model name. Defaults by provider.
        api_key: Optional BYOK key from user request. Falls back to .env.
        **kwargs: Additional provider-specific model arguments.

    Returns:
        A configured LangChain chat model instance.
    """
    resolved_provider = _clean(provider) or DEFAULT_PROVIDER
    resolved_provider = resolved_provider.lower()

    if resolved_provider not in DEFAULT_MODEL_BY_PROVIDER:
        raise ValueError(
            f"Unsupported provider '{resolved_provider}'. "
            f"Supported providers: {', '.join(DEFAULT_MODEL_BY_PROVIDER.keys())}."
        )

    resolved_model_name = _clean(model_name) or DEFAULT_MODEL_BY_PROVIDER[resolved_provider]
    resolved_api_key = _resolve_api_key(resolved_provider, api_key)

    if resolved_provider == "google":
        return ChatGoogleGenerativeAI(
            model=resolved_model_name,
            google_api_key=resolved_api_key,
            **kwargs,
        )

    if resolved_provider == "openai":
        return ChatOpenAI(
            model=resolved_model_name,
            api_key=resolved_api_key,
            **kwargs,
        )

    if resolved_provider == "anthropic":
        return ChatAnthropic(
            model=resolved_model_name,
            api_key=resolved_api_key,
            **kwargs,
        )

    openrouter_base_url = _clean(os.getenv("OPENROUTER_BASE_URL")) or "https://openrouter.ai/api/v1"
    referer = _clean(os.getenv("OPENROUTER_REFERER"))
    title = _clean(os.getenv("OPENROUTER_TITLE"))

    default_headers = dict(kwargs.pop("default_headers", {}) or {})
    if referer:
        default_headers.setdefault("HTTP-Referer", referer)
    if title:
        default_headers.setdefault("X-Title", title)

    return ChatOpenAI(
        model=resolved_model_name,
        api_key=resolved_api_key,
        base_url=openrouter_base_url,
        default_headers=default_headers or None,
        **kwargs,
    )


def create_chat_model_from_config(configurable: Optional[Dict[str, Any]] = None, **kwargs: Any) -> BaseChatModel:
    """Create model from LangGraph configurable settings.

    Expected configurable keys:
      - provider
      - model_name
      - api_key
    """
    cfg = configurable or {}
    provider = cfg.get("provider")
    model_name = cfg.get("model_name")
    api_key = cfg.get("api_key")

    return create_chat_model(
        provider=provider,
        model_name=model_name,
        api_key=api_key,
        **kwargs,
    )
