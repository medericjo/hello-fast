"""Composition root: creates the FastAPI app and shared resources."""
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.core.config import get_settings
from app.presentation.api.error_handlers import register_error_handlers
from app.presentation.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    # One pooled HTTP client for the whole app lifetime.
    app.state.http_client = httpx.AsyncClient(
        base_url=settings.jsonplaceholder_base_url,
        timeout=settings.http_timeout_seconds,
    )
    yield
    await app.state.http_client.aclose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
    register_error_handlers(app)
    app.include_router(api_router)

    @app.get("/health", tags=["health"])
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
