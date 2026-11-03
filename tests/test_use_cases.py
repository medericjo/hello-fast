import pytest

from app.application.use_cases.posts import GetPost, ListPosts
from app.application.use_cases.users import ListUserPosts
from app.domain.exceptions import NotFoundError
from tests.fakes import FakePostRepository, FakeUserRepository


async def test_list_posts_filters_by_user():
    posts = await ListPosts(FakePostRepository()).execute(user_id=1)
    assert [p.id for p in posts] == [1, 2]


async def test_get_post_raises_when_missing():
    with pytest.raises(NotFoundError):
        await GetPost(FakePostRepository()).execute(999)


async def test_list_user_posts_requires_existing_user():
    with pytest.raises(NotFoundError):
        await ListUserPosts(FakeUserRepository(), FakePostRepository()).execute(42)
