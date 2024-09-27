from uuid import UUID
from typing import Annotated, TypeVar

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import conlist
from fastapi import APIRouter, Body, Depends
from auth_utils import auth_required

from micro_media.models import get_session, Media
from micro_media.schemas import APIKeyUser, APIKeyPermission
from micro_media.schemas.v1 import internal as schemas


router = APIRouter()

T = TypeVar("T", bound=sa.Select | sa.Update)


def apply_filters(qs: T, filters: schemas.BulkMediaAckFilters) -> T:
    if filters.owner_id:
        qs = qs.where(Media.owner_id == filters.owner_id)

    if filters.media_type:
        qs = qs.where(Media.media_type == filters.media_type)

    if filters.first_ack:
        qs = qs.where(sa.not_(Media.ack))

    return qs


@router.post(
    "/bulk_ack",
    dependencies=[
        Depends(
            auth_required(
                permissions=[APIKeyPermission(scopes=["media:ack"])],
                user_class=APIKeyUser,
            ),
        )
    ],
    response_model=list[schemas.InternalMediaRead],
)
async def bulk_ack(
    session: Annotated[AsyncSession, Depends(get_session)],
    ids: Annotated[conlist(UUID, min_length=1, max_length=100), Body()],
    filters: Annotated[schemas.BulkMediaAckFilters, Depends()],
):
    ids = list(
        await session.scalars(
            apply_filters(sa.select(Media.id), filters).where(
                Media.id.in_(ids)
            )
        )
    )

    if not ids:
        return []

    await session.execute(
        sa.Update(Media)
        .where(Media.id.in_(ids))
        .values(ack=True, ack_at=sa.func.now())
    )
    await session.commit()

    return (
        await session.execute(sa.select(Media).where(Media.id.in_(ids)))
    ).scalars()
