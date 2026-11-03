"""Port (interface) the domain expects for reading posts."""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.post import Post


class PostRepository(ABC):
    @abstractmethod
    async def list(self, user_id: Optional[int] = None) -> List[Post]: ...

    @abstractmethod
    async def get(self, post_id: int) -> Optional[Post]: ...
