from uuid import UUID
from typing import Annotated

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from starlette.responses import RedirectResponse

from micro_media.utils.sqlalchemy import get_one
from micro_media.models import get_session, Media
from micro_media.storage import STORAGE_CONTEXT as SC


router = APIRouter()


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
