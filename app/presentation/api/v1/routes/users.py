from typing import List

from fastapi import APIRouter, Depends

from app.application.use_cases.users import GetUser, ListUserPosts, ListUsers
from app.presentation.api.dependencies import get_get_user, get_list_user_posts, get_list_users
from app.presentation.schemas.post import PostOut
from app.presentation.schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[UserOut])
async def list_users(use_case: ListUsers = Depends(get_list_users)):
    return await use_case.execute()


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int, use_case: GetUser = Depends(get_get_user)):
    return await use_case.execute(user_id)


@router.get("/{user_id}/posts", response_model=List[PostOut])
async def list_user_posts(user_id: int, use_case: ListUserPosts = Depends(get_list_user_posts)):
    return await use_case.execute(user_id)
