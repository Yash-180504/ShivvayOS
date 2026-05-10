from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.errors.exceptions import AppError
from backend.errors.schemas import ErrorResponse


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        payload = ErrorResponse(
            error_code=exc.error_code,
            error_message=exc.error_message,
            failed_at=exc.failed_at,
        )
        return JSONResponse(status_code=exc.status_code, content=payload.model_dump(mode="json"))

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
        payload = ErrorResponse(
            error_code="INTERNAL_SERVER_ERROR",
            error_message=str(exc),
            failed_at=datetime.now(timezone.utc),
        )
        return JSONResponse(status_code=500, content=payload.model_dump(mode="json"))
