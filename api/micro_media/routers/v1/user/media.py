from uuid import UUID
from typing import Annotated

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from auth_utils import get_user
from fastapi import APIRouter, Depends
from micro_media.models import get_session, Media

from micro_media.schemas import JWTUser, v1 as schemas
from micro_media.media import MEDIA_CONTEXT as MC
from micro_media.storage import STORAGE_CONTEXT as SC
from micro_media.utils.sqlalchemy import get_one


router = APIRouter()


@router.post("/upload", response_model=schemas.MediaRead)
async def save_media(
    user: Annotated[JWTUser, Depends(get_user)],
    data: Annotated[schemas.MediaCreate, Depends(schemas.MediaCreate.as_form)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    storage_manager = SC.default_manager
    media_manager = MC.get_manager(data.media_type.value)

    file_data = await data.file.read()
    await data.file.close()
    filename, file = await media_manager.avalidate_media(
        filename=data.file.filename or "",
        data=file_data,
    )

    file_identifier = await storage_manager.save_media(
        owner_id=user.identity,
        media_type=data.media_type,
        filename=filename,
        file=file,
        content_type=data.file.content_type,
    )

    file.close()

    media = Media(
        **data.model_dump(exclude={"file"}),
        file_identifier=file_identifier,
        storage_id=storage_manager.storage_id,
        owner_id=user.identity,
    )

    session.add(media)
    await session.commit()

    return media


@router.delete("/{media_id}", status_code=204)
async def delete_media(
    media_id: UUID,
    user: Annotated[JWTUser, Depends(get_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    storage_manager = SC.default_manager
    media = await get_one(
        session=session,
        query=sa.select(Media).where(
            Media.owner_id == user.identity,
            Media.id == media_id,
            sa.not_(Media.ack),
        ),
    )

    await storage_manager.delete_file(media.file_identifier)

    await session.delete(media)
    await session.commit()
