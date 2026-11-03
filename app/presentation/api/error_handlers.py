"""Translate domain exceptions into HTTP responses."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import ExternalServiceError, NotFoundError


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found(_: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ExternalServiceError)
    async def upstream_failed(_: Request, exc: ExternalServiceError) -> JSONResponse:
        return JSONResponse(status_code=502, content={"detail": str(exc)})
