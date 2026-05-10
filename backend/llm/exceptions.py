class LLMProviderError(Exception):
    """Base class for LLM provider failures (mapped from vendor APIs)."""

    def __init__(self, message: str, *, provider: str, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.provider = provider
        self.cause = cause


class LLMTimeoutError(LLMProviderError):
    """Raised when a generation call exceeds the configured timeout."""

    def __init__(self, message: str, *, provider: str, cause: Exception | None = None) -> None:
        super().__init__(message, provider=provider, cause=cause)


class LLMInvalidResponseError(LLMProviderError):
    """Raised when the provider returns an empty or unusable response."""

    def __init__(self, message: str, *, provider: str, cause: Exception | None = None) -> None:
        super().__init__(message, provider=provider, cause=cause)
