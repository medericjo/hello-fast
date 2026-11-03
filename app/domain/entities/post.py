"""Post entity: pure business object, no framework dependency."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Post:
    id: int
    user_id: int
    title: str
    body: str
