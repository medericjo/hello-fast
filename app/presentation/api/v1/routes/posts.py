from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from app.application.use_cases.posts import GetPost, ListPosts
from app.presentation.api.dependencies import get_get_post, get_list_posts
from app.presentation.schemas.post import PostOut

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=List[PostOut])
async def list_posts(
    user_id: Optional[int] = Query(None, description="Filter posts by author id"),
    use_case: ListPosts = Depends(get_list_posts),
):
    return await use_case.execute(user_id=user_id)


@router.get("/{post_id}", response_model=PostOut)
async def get_post(post_id: int, use_case: GetPost = Depends(get_get_post)):
    return await use_case.execute(post_id)
