"""In-memory repositories used to test without touching the network."""
from typing import List, Optional

from app.domain.entities.post import Post
from app.domain.entities.user import User
from app.domain.repositories.post_repository import PostRepository
from app.domain.repositories.user_repository import UserRepository

USERS = [User(1, "Leanne Graham", "Bret", "leanne@april.biz", "1-770", "hildegard.org")]
POSTS = [
    Post(1, 1, "first", "body one"),
    Post(2, 1, "second", "body two"),
    Post(3, 2, "third", "body three"),
]


class FakePostRepository(PostRepository):
    async def list(self, user_id: Optional[int] = None) -> List[Post]:
        return [p for p in POSTS if user_id is None or p.user_id == user_id]

    async def get(self, post_id: int) -> Optional[Post]:
        return next((p for p in POSTS if p.id == post_id), None)


class FakeUserRepository(UserRepository):
    async def list(self) -> List[User]:
        return list(USERS)

    async def get(self, user_id: int) -> Optional[User]:
        return next((u for u in USERS if u.id == user_id), None)
