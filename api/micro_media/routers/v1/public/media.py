from uuid import UUID
from typing import Annotated, Literal, cast

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from starlette.responses import RedirectResponse

from micro_media.utils import truthy_or_404
from micro_media.utils.sqlalchemy import get_one
from micro_media.utils.cache import AsyncRedisCache
from micro_media.models import get_session, Media, MediaType
from micro_media.storage import STORAGE_CONTEXT as SC
from micro_media.media import MEDIA_CONTEXT as MC, IMGProxyThumbnailManager
from micro_media.media.manager import ImageMediaManager


router = APIRouter()

THUMBNAIL_MANAGER = IMGProxyThumbnailManager()
IMAGE_MEDIA_MANAGER: ImageMediaManager = cast(
    ImageMediaManager, MC.get_manager("image")
)

CACHE_TTL = 60 * 60  # 1 hour


@AsyncRedisCache.aredis_cache(
    key_generator=lambda media, expires_in: f"original_link:{media.id}",
    cache_deserializer=str,
    cache_serializer=str,
    ttl=max(CACHE_TTL - 30, 30),
)
async def _get_original_link(media: Media, expires_in: int) -> str:
    storage_manager = SC.get_manager(storage_id=media.storage_id)

    file_link = await storage_manager.generate_file_link(
        file_identifier=media.file_identifier, expires_in=expires_in
    )

    return file_link


@router.get("/original/{media_id}", status_code=302)
async def get_original_file(
    media_id: UUID, session: Annotated[AsyncSession, Depends(get_session)]
):
    media = await get_one(
        session=session, query=sa.select(Media).filter(Media.id == media_id)
    )

    return RedirectResponse(
        url=await _get_original_link(media=media, expires_in=3600),
        status_code=302,
        headers={"max-age": f"{CACHE_TTL}"},
    )


@router.get("/thumbnail/{media_id}", status_code=302)
async def get_thumbnail(
    media_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    size: Literal[
        "default", *IMAGE_MEDIA_MANAGER.get_thumbnail_sizes()
    ] = "default",
):
    size_conf = truthy_or_404(
        IMAGE_MEDIA_MANAGER.get_thumbnail_size_conf(
            size_name=None if size == "default" else size
        ),
        message="Invalid thumbnail size.",
    )

    media = await get_one(
        session=session,
        query=sa.select(Media).filter(
            Media.media_type == MediaType.IMAGE, Media.id == media_id
        ),
    )

    thumbnail_link = THUMBNAIL_MANAGER.get_thumbnail_link(
        original_file_link=await _get_original_link(
            media=media, expires_in=3600
        ),
        thumbnail_size=size_conf,
    )

    return RedirectResponse(
        url=thumbnail_link, status_code=302, headers={"max-age": "3600"}
    )
