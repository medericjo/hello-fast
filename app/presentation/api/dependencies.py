"""Dependency injection wiring: builds concrete adapters and use cases per request."""
from fastapi import Depends, Request

from app.application.use_cases.posts import GetPost, ListPosts
from app.application.use_cases.users import GetUser, ListUserPosts, ListUsers
from app.domain.repositories.post_repository import PostRepository
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.http.jsonplaceholder_client import JsonPlaceholderClient
from app.infrastructure.repositories.jsonplaceholder_post_repository import (
    JsonPlaceholderPostRepository,
)
from app.infrastructure.repositories.jsonplaceholder_user_repository import (
    JsonPlaceholderUserRepository,
)


def get_client(request: Request) -> JsonPlaceholderClient:
    # The shared httpx.AsyncClient is created once in main.py's lifespan.
    return JsonPlaceholderClient(request.app.state.http_client)


def get_post_repository(client: JsonPlaceholderClient = Depends(get_client)) -> PostRepository:
    return JsonPlaceholderPostRepository(client)


def get_user_repository(client: JsonPlaceholderClient = Depends(get_client)) -> UserRepository:
    return JsonPlaceholderUserRepository(client)


def get_list_posts(posts: PostRepository = Depends(get_post_repository)) -> ListPosts:
    return ListPosts(posts)


def get_get_post(posts: PostRepository = Depends(get_post_repository)) -> GetPost:
    return GetPost(posts)


def get_list_users(users: UserRepository = Depends(get_user_repository)) -> ListUsers:
    return ListUsers(users)


def get_get_user(users: UserRepository = Depends(get_user_repository)) -> GetUser:
    return GetUser(users)


def get_list_user_posts(
    users: UserRepository = Depends(get_user_repository),
    posts: PostRepository = Depends(get_post_repository),
) -> ListUserPosts:
    return ListUserPosts(users, posts)
