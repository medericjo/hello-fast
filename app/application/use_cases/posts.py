"""Post use cases: application logic orchestrating repositories."""
from typing import List, Optional

from app.domain.entities.post import Post
from app.domain.exceptions import NotFoundError
from app.domain.repositories.post_repository import PostRepository


class ListPosts:
    def __init__(self, posts: PostRepository) -> None:
        self._posts = posts

    async def execute(self, user_id: Optional[int] = None) -> List[Post]:
        return await self._posts.list(user_id=user_id)


class GetPost:
    def __init__(self, posts: PostRepository) -> None:
        self._posts = posts

    async def execute(self, post_id: int) -> Post:
        post = await self._posts.get(post_id)
        if post is None:
            raise NotFoundError("Post", post_id)
        return post
