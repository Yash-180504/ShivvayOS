from __future__ import annotations

import asyncio
import logging

from backend.llm.base import BaseLLMProvider
from backend.llm.exceptions import LLMInvalidResponseError, LLMProviderError, LLMTimeoutError
from backend.llm.schemas import LLMGenerationParams, LLMGenerationResult

logger = logging.getLogger("shivvayos.llm.openai")


class OpenAILLMProvider(BaseLLMProvider):
    def __init__(
        self,
        *,
        api_key: str,
        default_model: str,
        default_timeout_seconds: float,
        max_tokens_default: int = 1024,
    ) -> None:
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:  # pragma: no cover
            raise ImportError("OpenAI provider requires the 'openai' package. Install: pip install openai") from exc

        self._default_model = default_model
        self._default_timeout_seconds = default_timeout_seconds
        self._max_tokens_default = max_tokens_default
        self._client = AsyncOpenAI(api_key=api_key, timeout=default_timeout_seconds)

    @property
    def provider_name(self) -> str:
        return "openai"

    async def generate(self, prompt: str, *, params: LLMGenerationParams | None = None) -> LLMGenerationResult:
        from openai import APIStatusError, APITimeoutError, OpenAIError

        model = (params.model if params and params.model else None) or self._default_model
        timeout = (params.timeout_seconds if params and params.timeout_seconds else None) or self._default_timeout_seconds
        max_tokens = (params.max_tokens if params and params.max_tokens else None) or self._max_tokens_default

        logger.debug("openai.generate model=%s timeout=%s", model, timeout)

        async def _call() -> str:
            response = await self._client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
            )
            choice = response.choices[0] if response.choices else None
            content = choice.message.content if choice and choice.message else None
            if not content or not str(content).strip():
                raise LLMInvalidResponseError(
                    "OpenAI returned empty completion content.",
                    provider=self.provider_name,
                )
            return str(content).strip()

        try:
            text = await asyncio.wait_for(_call(), timeout=timeout)
        except asyncio.TimeoutError as exc:
            logger.warning("OpenAI generation timed out model=%s", model)
            raise LLMTimeoutError(
                f"OpenAI request exceeded {timeout}s timeout.",
                provider=self.provider_name,
                cause=exc,
            ) from exc
        except APITimeoutError as exc:
            logger.warning("OpenAI client timeout: %s", exc)
            raise LLMTimeoutError(str(exc), provider=self.provider_name, cause=exc) from exc
        except APIStatusError as exc:
            logger.exception("OpenAI API status error: %s", exc)
            raise LLMProviderError(
                f"OpenAI API error: {exc}",
                provider=self.provider_name,
                cause=exc,
            ) from exc
        except OpenAIError as exc:
            logger.exception("OpenAI error: %s", exc)
            raise LLMProviderError(str(exc), provider=self.provider_name, cause=exc) from exc

        return LLMGenerationResult(text=text, model_used=model, provider=self.provider_name)
