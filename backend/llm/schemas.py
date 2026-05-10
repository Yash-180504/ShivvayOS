from pydantic import BaseModel, Field


class LLMGenerationParams(BaseModel):
    """Optional per-call overrides for LLM generation."""

    model: str | None = None
    max_tokens: int | None = Field(default=None, ge=1, le=128_000)
    timeout_seconds: float | None = Field(default=None, gt=0, le=600)


class LLMGenerationResult(BaseModel):
    """Typed wrapper for provider output (extensible for metadata)."""

    text: str
    model_used: str
    provider: str
