from backend.llm.base import BaseLLMProvider
from backend.llm.schemas import LLMGenerationParams, LLMGenerationResult


class MockLLMProvider(BaseLLMProvider):
    @property
    def provider_name(self) -> str:
        return "mock"

    async def generate(self, prompt: str, *, params: LLMGenerationParams | None = None) -> LLMGenerationResult:
        text = f"mock::{prompt.strip()[:140]}"
        return LLMGenerationResult(text=text, model_used="mock", provider=self.provider_name)
