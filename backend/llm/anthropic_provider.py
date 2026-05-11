from __future__ import annotations

import asyncio
import logging

from backend.llm.base import BaseLLMProvider
from backend.llm.exceptions import LLMInvalidResponseError, LLMProviderError, LLMTimeoutError
from backend.llm.schemas import LLMGenerationParams, LLMGenerationResult

logger = logging.getLogger("shivvayos.llm.anthropic")

try:
    from anthropic import AsyncAnthropic
except ImportError:  # pragma: no cover
    AsyncAnthropic = None  # type: ignore[assignment]


class AnthropicLLMProvider(BaseLLMProvider):
    def __init__(
        self,
        *,
        api_key: str,
        default_model: str,
        default_timeout_seconds: float,
        max_tokens_default: int = 1024,
    ) -> None:
        if AsyncAnthropic is None:  # pragma: no cover
            raise ImportError(
                "Anthropic provider requires the 'anthropic' package. Install: pip install anthropic"
            )

        self._default_model = default_model
        self._default_timeout_seconds = default_timeout_seconds
        self._max_tokens_default = max_tokens_default
        self._client = AsyncAnthropic(api_key=api_key, timeout=default_timeout_seconds)

    @property
    def provider_name(self) -> str:
        return "anthropic"

    async def generate(self, prompt: str, *, params: LLMGenerationParams | None = None) -> LLMGenerationResult:
        from anthropic import APIStatusError, AnthropicError

        try:
            from anthropic import APITimeoutError as AnthropicAPITimeoutError
        except ImportError:  # pragma: no cover
            AnthropicAPITimeoutError = None  # type: ignore[misc, assignment]

        model = (params.model if params and params.model else None) or self._default_model
        timeout = (params.timeout_seconds if params and params.timeout_seconds else None) or self._default_timeout_seconds
        max_tokens = (params.max_tokens if params and params.max_tokens else None) or self._max_tokens_default

        logger.debug("anthropic.generate model=%s timeout=%s", model, timeout)

        async def _call() -> str:
            message = await self._client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            parts: list[str] = []
            for block in message.content:
                btype = getattr(block, "type", None)
                if btype == "text":
                    parts.append(getattr(block, "text", ""))
                elif hasattr(block, "text"):
                    parts.append(str(getattr(block, "text", "")))
            text = "".join(parts).strip()
            if not text:
                raise LLMInvalidResponseError(
                    "Anthropic returned empty message content.",
                    provider=self.provider_name,
                )
            return text

        try:
            text = await asyncio.wait_for(_call(), timeout=timeout)
        except asyncio.TimeoutError as exc:
            logger.warning("Anthropic generation timed out model=%s", model)
            raise LLMTimeoutError(
                f"Anthropic request exceeded {timeout}s timeout.",
                provider=self.provider_name,
                cause=exc,
            ) from exc
        except APIStatusError as exc:
            logger.exception("Anthropic API status error: %s", exc)
            raise LLMProviderError(
                f"Anthropic API error: {exc}",
                provider=self.provider_name,
                cause=exc,
            ) from exc
        except AnthropicError as exc:
            logger.exception("Anthropic error: %s", exc)
            if AnthropicAPITimeoutError is not None and isinstance(exc, AnthropicAPITimeoutError):
                raise LLMTimeoutError(str(exc), provider=self.provider_name, cause=exc) from exc
            msg = str(exc).lower()
            if "timeout" in msg or "timed out" in msg:
                raise LLMTimeoutError(str(exc), provider=self.provider_name, cause=exc) from exc
            raise LLMProviderError(str(exc), provider=self.provider_name, cause=exc) from exc

        return LLMGenerationResult(text=text, model_used=model, provider=self.provider_name)
