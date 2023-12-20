from io import BytesIO
from typing import Annotated
from auth_utils import get_user
from fastapi import APIRouter, Depends
from micro_media.models import get_session, Media

from micro_media.schemas import JWTUser, v1 as schemas
from micro_media.media import MEDIA_CONTEXT as MC
from micro_media.storage import STORAGE_CONTEXT as SC
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()


@router.post("/upload", response_model=schemas.MediaRead)
async def save_media(
    user: Annotated[JWTUser, Depends(get_user)],
    data: Annotated[schemas.MediaCreate, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    storage_manager = SC.default_manager
    media_manager = MC.get_manager(data.media_type.value)

    filename, file = media_manager.validate_media(
        filename=data.file.filename or "",
        file=BytesIO(await data.file.read()),
    )

    file_identifier = await storage_manager.save_media(
        owner_id=user.identity,
        media_type=data.media_type,
        filename=filename,
        file=file,
        content_type=data.file.content_type,
    )

    media = Media(
        **data.model_dump(exclude={"file"}),
        file_identifier=file_identifier,
        storage_id=storage_manager.storage_id,
        owner_id=user.identity,
    )

    session.add(media)
    await session.commit()

    return media
