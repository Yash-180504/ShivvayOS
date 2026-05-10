from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ShivvayOS Backend"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/shivvayos"

    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    anthropic_api_key: str | None = Field(default=None, description="Anthropic API key")
    default_llm_provider: str = Field(
        default="mock",
        description="One of: mock, openai, anthropic",
    )
    default_openai_model: str = Field(default="gpt-4o-mini")
    default_anthropic_model: str = Field(default="claude-3-5-sonnet-20240620")
    llm_request_timeout_seconds: float = Field(default=60.0, ge=5.0, le=600.0)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
