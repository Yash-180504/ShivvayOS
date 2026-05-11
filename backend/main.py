from fastapi import FastAPI
from backend.api.routes import router as api_router
from backend.errors.handlers import register_exception_handlers
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://shivvayos.vercel.app"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Rest of your routes...

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
