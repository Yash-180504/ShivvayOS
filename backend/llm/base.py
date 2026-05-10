from abc import ABC, abstractmethod

from backend.llm.schemas import LLMGenerationParams, LLMGenerationResult


class BaseLLMProvider(ABC):
    """Provider-agnostic LLM interface. Implementations must not block the event loop."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def generate(self, prompt: str, *, params: LLMGenerationParams | None = None) -> LLMGenerationResult:
        """Run a single completion and return normalized text + metadata."""
