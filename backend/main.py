from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router as api_router
from backend.errors.handlers import register_exception_handlers
from backend.core.config import settings


def _get_allowed_origins() -> list[str]:
    """Get allowed origins from environment or defaults."""
    # Allow environment variable to override (comma-separated)
    if hasattr(settings, "allowed_cors_origins"):
        origins = settings.allowed_cors_origins
        if isinstance(origins, str):
            return [o.strip() for o in origins.split(",")]
        return origins
    # Fallback to common development/production origins
    return [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://shivvayos.vercel.app",
        "https://shivvayos-production.up.railway.app",
    ]


def create_app() -> FastAPI:
    app = FastAPI(
        title="ShivvayOS Backend",
        version="0.1.0",
        description="Minimal multi-agent orchestration backend skeleton.",
    )
    
    # Add CORS middleware FIRST (order matters!)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_get_allowed_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    register_exception_handlers(app)
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
