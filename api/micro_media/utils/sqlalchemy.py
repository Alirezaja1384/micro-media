from typing import TypeVar
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


async def get_one(session: AsyncSession, query: Select[tuple[T]]) -> T:
    return (await session.execute(query.limit(2))).scalar_one()
