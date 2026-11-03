import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.presentation.api.dependencies import get_post_repository, get_user_repository
from tests.fakes import FakePostRepository, FakeUserRepository


@pytest.fixture
def client():
    # Swap the real JSONPlaceholder adapters for in-memory fakes.
    app.dependency_overrides[get_post_repository] = FakePostRepository
    app.dependency_overrides[get_user_repository] = FakeUserRepository
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_list_posts(client):
    response = client.get("/api/v1/posts", params={"user_id": 1})
    assert response.status_code == 200
    assert [p["id"] for p in response.json()] == [1, 2]


def test_get_post_not_found(client):
    response = client.get("/api/v1/posts/999")
    assert response.status_code == 404


def test_user_posts(client):
    response = client.get("/api/v1/users/1/posts")
    assert response.status_code == 200
    assert len(response.json()) == 2
