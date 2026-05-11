from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


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
    allowed_cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000,https://shivvayos.vercel.app,https://shivvayos-production.up.railway.app",
        description="Comma-separated list of allowed CORS origins",
    )

    @property
    def async_database_url(self) -> str:
        """Normalize PostgreSQL URLs for async SQLAlchemy/asyncpg, including Neon URLs."""
        url = make_url(self.database_url)
        if url.drivername == "postgresql":
            url = url.set(drivername="postgresql+asyncpg")
        if url.drivername == "postgres":
            url = url.set(drivername="postgresql+asyncpg")
        return url.difference_update_query(["sslmode", "channel_binding"]).render_as_string(hide_password=False)

    @property
    def async_database_connect_args(self) -> dict[str, object]:
        url = make_url(self.database_url)
        sslmode = url.query.get("sslmode")
        if sslmode in {"require", "verify-ca", "verify-full"}:
            import ssl

            return {"ssl": ssl.create_default_context()}
        return {}

    model_config = SettingsConfigDict(env_file=(".env", ".env.local"), env_file_encoding="utf-8", extra="ignore")


settings = Settings()
