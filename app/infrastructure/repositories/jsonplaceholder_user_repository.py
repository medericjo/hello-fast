"""Adapter: implements UserRepository using JSONPlaceholder."""
from typing import Any, Dict, List, Optional

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.http.jsonplaceholder_client import JsonPlaceholderClient


def _to_user(raw: Dict[str, Any]) -> User:
    return User(
        id=raw["id"],
        name=raw["name"],
        username=raw["username"],
        email=raw["email"],
        phone=raw["phone"],
        website=raw["website"],
    )


class JsonPlaceholderUserRepository(UserRepository):
    def __init__(self, client: JsonPlaceholderClient) -> None:
        self._client = client

    async def list(self) -> List[User]:
        data = await self._client.get_json("/users") or []
        return [_to_user(item) for item in data]

    async def get(self, user_id: int) -> Optional[User]:
        data = await self._client.get_json(f"/users/{user_id}")
        return _to_user(data) if data else None
