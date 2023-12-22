from enum import Enum
from typing import Annotated
from uuid import UUID
from fastapi import File, Form, UploadFile
from micro_media.utils import APIModel


class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"


class MediaBase(APIModel):
    title: str | None = None
    description: str | None = None
    media_type: MediaType


class MediaCreate(MediaBase):
    file: UploadFile

    @classmethod
    def as_form(
        cls,
        file: Annotated[UploadFile, File()],
        media_type: Annotated[MediaType, Form()],
        title: Annotated[str | None, Form()] = None,
        description: Annotated[str | None, Form()] = None,
    ) -> "MediaCreate":
        return cls(
            title=title,
            description=description,
            media_type=media_type,
            file=file,
        )


class MediaRead(MediaBase):
    id: UUID
