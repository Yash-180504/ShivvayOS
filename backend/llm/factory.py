from __future__ import annotations

import logging

from backend.core.config import Settings
from backend.llm.base import BaseLLMProvider
from backend.llm.mock_provider import MockLLMProvider

logger = logging.getLogger("shivvayos.llm.factory")


def create_llm_provider(settings: Settings) -> BaseLLMProvider:
    """Resolve the configured provider with mock fallback when keys or config are missing."""

    provider = settings.default_llm_provider.lower().strip()

    if provider == "mock":
        return MockLLMProvider()

    if provider == "openai":
        if not settings.openai_api_key:
            logger.warning("DEFAULT_LLM_PROVIDER=openai but OPENAI_API_KEY is unset; using mock provider.")
            return MockLLMProvider()
        from backend.llm.openai_provider import OpenAILLMProvider

        return OpenAILLMProvider(
            api_key=settings.openai_api_key,
            default_model=settings.default_openai_model,
            default_timeout_seconds=settings.llm_request_timeout_seconds,
        )

    if provider == "anthropic":
        if not settings.anthropic_api_key:
            logger.warning("DEFAULT_LLM_PROVIDER=anthropic but ANTHROPIC_API_KEY is unset; using mock provider.")
            return MockLLMProvider()
        from backend.llm.anthropic_provider import AnthropicLLMProvider

        return AnthropicLLMProvider(
            api_key=settings.anthropic_api_key,
            default_model=settings.default_anthropic_model,
            default_timeout_seconds=settings.llm_request_timeout_seconds,
        )

    logger.warning("Unknown DEFAULT_LLM_PROVIDER=%s; using mock.", provider)
    return MockLLMProvider()
