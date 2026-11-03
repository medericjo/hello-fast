"""Port (interface) the domain expects for reading users."""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    async def list(self) -> List[User]: ...

    @abstractmethod
    async def get(self, user_id: int) -> Optional[User]: ...
