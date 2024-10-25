"""
Configure the user model with FastAPI Users

with JWT authentication and Bearer header transport
"""

import re
import uuid
from typing import Annotated

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.files import File
from app.models.experiments import Experiment
from app.core.db import get_async_session
from app.core.config import settings
from app.schemas.users import UserRead, UserCreate, UserUpdate

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends, Request, Response
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from fastapi_users import (
    BaseUserManager,
    UUIDIDMixin,
    InvalidPasswordException,
    FastAPIUsers,
)
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

SECRET = str(settings.SECRET_KEY)


class User(SQLAlchemyBaseUserTableUUID, Base):
    """sqlalchemy users model"""

    files: Mapped[list[File]] = relationship(
        "File", cascade="all, delete", lazy="selectin"
    )

    experiments: Mapped[list[Experiment]] = relationship(
        "Experiment", cascade="all, delete", lazy="selectin"
    )


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """manager for users models, handles defining logic for signals trigger when interacting the users model"""

    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def validate_password(self, password: str, user: UserCreate | User) -> None:
        """validates password on user creation, specifies the rules for writing passwords"""

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
        """triggers on user registration"""
        print(f"User {user.id} has registered.")

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        """generates verification token secret"""
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def on_after_verify(self, user: User, request: Request | None = None):
        """triggers on user verification"""
        print(f"User {user.id} has been verified")

    async def on_after_login(
        self,
        user: User,
        request: Request | None = None,
        response: Response | None = None,
    ):
        """triggers on user login"""
        print(f"User {user.id} logged in.")

    async def on_after_update(
        self,
        user: User,
        update_dict: UserUpdate,
        request: Request | None = None,
    ):
        """triggers on user update"""
        print(f"User {user.id} has been updated with {update_dict}.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ):
        """triggers on user forgot password, generates reset token"""
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_reset_password(self, user: User, request: Request | None = None):
        """triggers on user reset password"""
        print(f"User {user.id} has reset their password.")

    async def on_before_delete(self, user: User, request: Request | None = None):
        """triggers on user delete"""
        print(f"User {user.id} is going to be deleted")

    async def on_after_delete(self, user: User, request: Request | None = None):
        """triggers after user delete"""
        print(f"User {user.id} is successfully deleted")


async def get_user_db(session: Annotated[AsyncSession, Depends(get_async_session)]):
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    """JWT strategy for authentication"""
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
