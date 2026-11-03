"""User entity: pure business object, no framework dependency."""
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    name: str
    username: str
    email: str
    phone: str
    website: str
