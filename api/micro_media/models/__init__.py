from typing import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from micro_media.settings.base import SQLALCHEMY_CONN_STR, SQLALCHEMY_ECHO
from .base import Base


@lru_cache(maxsize=None)
def get_engine():
    return create_async_engine(SQLALCHEMY_CONN_STR, echo=SQLALCHEMY_ECHO)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(get_engine(), expire_on_commit=False)

    async with async_session() as session:
        yield session


__all__ = [
    "Base",
    "get_engine",
    "get_session",
]
