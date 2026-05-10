from fastapi import FastAPI

from backend.api.routes import router as api_router
from backend.errors.handlers import register_exception_handlers


def create_app() -> FastAPI:
    app = FastAPI(
        title="ShivvayOS Backend",
        version="0.1.0",
        description="Minimal multi-agent orchestration backend skeleton.",
    )
    register_exception_handlers(app)
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
