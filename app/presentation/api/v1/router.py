from fastapi import APIRouter

from app.presentation.api.v1.routes import posts, users

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(posts.router)
api_router.include_router(users.router)
