"""
Define users router.
"""

from fastapi import APIRouter

from app.models.users import fastapi_users
from app.schemas.users import UserRead, UserUpdate


router = APIRouter()


router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
