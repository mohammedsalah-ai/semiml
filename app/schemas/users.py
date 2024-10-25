"""
Defines user API schemas

schemas to be used to interact with users table in the database
"""

import uuid

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    """utilizes FastAPI Users internel base user GET schema with UUID"""

    pass


class UserCreate(schemas.BaseUserCreate):
    """utilizes FastAPI Users internel base user POST schema"""

    pass


class UserUpdate(schemas.BaseUserUpdate):
    """utilizes FastAPI Users internel base user PATCH schema"""

    pass
