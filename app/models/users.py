"""
Define The User model with FastAPI Users.
"""

import re
import uuid
from typing import Annotated

from app.models.base import Base
from app.core.db import get_async_session
from app.core.config import settings
from app.schemas.users import UserRead, UserCreate, UserUpdate

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends, Request, Response
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from fastapi_users import BaseUserManager, UUIDIDMixin, InvalidPasswordException

SECRET = str(settings.SECRET_KEY)


class User(SQLAlchemyBaseUserTableUUID, Base):
    pass


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def validate_password(
        self, password: str, user: Union[UserCreate, User]
    ) -> None:

        if len(password) < 10:
            raise InvalidPasswordException(
                reason="Password too short, at least 10 charaters"
            )

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise InvalidPasswordException(
                reason="Password must contain at least one symbol."
            )

        if not re.search(r"[A-Z]", password):
            raise InvalidPasswordException(
                reason="Password must contain at least one capital letter."
            )

        if not re.search(r"[a-z]", password):
            raise InvalidPasswordException(
                reason="Password must contain at least one lowercase letter."
            )

        return None

    async def on_after_register(self, user: User, request: Request | None = None):
        print(f"User {user.id} has registered.")

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def on_after_verify(self, user: User, request: Request | None = None):
        print(f"User {user.id} has been verified")

    async def on_after_login(
        self,
        user: User,
        request: Request | None = None,
        response: Response | None = None,
    ):
        print(f"User {user.id} logged in.")

    async def on_after_update(
        self,
        user: User,
        update_dict: UserUpdate,
        request: Request | None = None,
    ):
        print(f"User {user.id} has been updated with {update_dict}.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_reset_password(self, user: User, request: Request | None = None):
        print(f"User {user.id} has reset their password.")

    async def on_before_delete(self, user: User, request: Request | None = None):
        print(f"User {user.id} is going to be deleted")

    async def on_after_delete(self, user: User, request: Request | None = None):
        print(f"User {user.id} is successfully deleted")


async def get_user_db(session: Annotated[AsyncSession, Depends(get_async_session)]):
    yield SQLAlchemyUserDatabase(session, User)
