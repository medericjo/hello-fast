"""API response models (what clients see), separate from domain entities."""
from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    username: str
    email: str
    phone: str
    website: str
