"""Application settings, loaded from environment variables / .env file."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "hello-fast"
    jsonplaceholder_base_url: str = "https://jsonplaceholder.typicode.com"
    http_timeout_seconds: float = 10.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
