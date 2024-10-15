"""
Creates a database connection and establishes a session maker.
"""

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


CONNECTION_STRING = str(settings.SQLALCHEMY_DATABASE_URI)

engine = create_async_engine(CONNECTION_STRING)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
