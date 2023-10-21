from uuid import UUID
from typing import Annotated, Literal, cast

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from starlette.responses import RedirectResponse

from micro_media.utils import truthy_or_404
from micro_media.utils.sqlalchemy import get_one
from micro_media.models import get_session, Media, MediaType
from micro_media.storage import STORAGE_CONTEXT as SC
from micro_media.media import MEDIA_CONTEXT as MC, IMGProxyThumbnailManager
from micro_media.media.manager import ImageMediaManager


router = APIRouter()


IMAGE_MEDIA_MANAGER: ImageMediaManager = cast(
    ImageMediaManager, MC.get_manager("image")
)


@router.get("/original/{media_id}", status_code=302)
async def get_original_file(
    media_id: UUID, session: Annotated[AsyncSession, Depends(get_session)]
):
    media = await get_one(
        session=session, query=sa.select(Media).filter(Media.id == media_id)
    )

    storage_manager = SC.get_manager(storage_id=media.storage_id)

    file_link = await storage_manager.generate_file_link(
        file_identifier=media.file_identifier, expires_in=3600
    )

    return RedirectResponse(
        url=file_link, status_code=302, headers={"max-age": "3600"}
    )


@router.get("/thumbnail/{media_id}", status_code=302)
async def get_thumbnail(
    media_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    size: Literal[
        "default", *IMAGE_MEDIA_MANAGER.get_thumbnail_sizes()
    ] = "default",
):
    media = await get_one(
        session=session,
        query=sa.select(Media).filter(
            Media.media_type == MediaType.IMAGE, Media.id == media_id
        ),
    )

    original_file_link = await SC.get_manager(
        storage_id=media.storage_id
    ).generate_file_link(
        file_identifier=media.file_identifier, expires_in=3600
    )

    thumbnail_link = IMGProxyThumbnailManager().get_thumbnail_link(
        original_file_link=original_file_link,
        thumbnail_size=truthy_or_404(
            IMAGE_MEDIA_MANAGER.get_thumbnail_size_conf(
                size_name=None if size == "default" else size
            ),
            message="Invalid thumbnail size.",
        ),
    )

    return RedirectResponse(
        url=thumbnail_link, status_code=302, headers={"max-age": "3600"}
    )
