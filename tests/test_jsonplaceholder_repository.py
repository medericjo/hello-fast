import httpx
import pytest

from app.domain.exceptions import ExternalServiceError
from app.infrastructure.http.jsonplaceholder_client import JsonPlaceholderClient
from app.infrastructure.repositories.jsonplaceholder_post_repository import (
    JsonPlaceholderPostRepository,
)


def make_repo(handler) -> JsonPlaceholderPostRepository:
    http = httpx.AsyncClient(base_url="https://example.test", transport=httpx.MockTransport(handler))
    return JsonPlaceholderPostRepository(JsonPlaceholderClient(http))


async def test_maps_camel_case_payload_to_entity():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/posts/1"
        return httpx.Response(200, json={"id": 1, "userId": 7, "title": "t", "body": "b"})

    post = await make_repo(handler).get(1)
    assert post is not None and post.user_id == 7


async def test_returns_none_on_404():
    assert await make_repo(lambda r: httpx.Response(404, json={})).get(1) is None


async def test_raises_on_upstream_error():
    with pytest.raises(ExternalServiceError):
        await make_repo(lambda r: httpx.Response(500)).list()
