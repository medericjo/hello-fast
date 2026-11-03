"""User use cases: application logic orchestrating repositories."""
from typing import List

from app.domain.entities.post import Post
from app.domain.entities.user import User
from app.domain.exceptions import NotFoundError
from app.domain.repositories.post_repository import PostRepository
from app.domain.repositories.user_repository import UserRepository


class ListUsers:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    async def execute(self) -> List[User]:
        return await self._users.list()


class GetUser:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    async def execute(self, user_id: int) -> User:
        user = await self._users.get(user_id)
        if user is None:
            raise NotFoundError("User", user_id)
        return user


class ListUserPosts:
    """Combines two repositories: checks the user exists, then fetches their posts."""

    def __init__(self, users: UserRepository, posts: PostRepository) -> None:
        self._users = users
        self._posts = posts

    async def execute(self, user_id: int) -> List[Post]:
        if await self._users.get(user_id) is None:
            raise NotFoundError("User", user_id)
        return await self._posts.list(user_id=user_id)
