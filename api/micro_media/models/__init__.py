from typing import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from micro_media.settings import SQLALCHEMY_CONN_STR, SQLALCHEMY_ECHO

from .base import Base
from .media import Media, MediaType


# create the engine only once
_engine = create_async_engine(
    SQLALCHEMY_CONN_STR,
    echo=SQLALCHEMY_ECHO,
    pool_size=10,
    max_overflow=10,
    pool_pre_ping=True,
)

# create the sessionmaker only once
AsyncSessionLocal = async_sessionmaker(
    bind=_engine,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


__all__ = [
    "Base",
    "get_engine",
    "get_session",
    "Media",
    "MediaType",
]
