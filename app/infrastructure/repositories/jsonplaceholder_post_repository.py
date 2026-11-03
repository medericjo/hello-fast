"""Adapter: implements PostRepository using JSONPlaceholder."""
from typing import Any, Dict, List, Optional

from app.domain.entities.post import Post
from app.domain.repositories.post_repository import PostRepository
from app.infrastructure.http.jsonplaceholder_client import JsonPlaceholderClient


def _to_post(raw: Dict[str, Any]) -> Post:
    # JSONPlaceholder uses camelCase ("userId"); the domain uses snake_case.
    return Post(id=raw["id"], user_id=raw["userId"], title=raw["title"], body=raw["body"])


class JsonPlaceholderPostRepository(PostRepository):
    def __init__(self, client: JsonPlaceholderClient) -> None:
        self._client = client

    async def list(self, user_id: Optional[int] = None) -> List[Post]:
        params = {"userId": user_id} if user_id is not None else None
        data = await self._client.get_json("/posts", params=params) or []
        return [_to_post(item) for item in data]

    async def get(self, post_id: int) -> Optional[Post]:
        data = await self._client.get_json(f"/posts/{post_id}")
        return _to_post(data) if data else None
