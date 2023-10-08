from enum import Enum
from uuid import UUID
from fastapi import UploadFile
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


class MediaRead(MediaBase):
    id: UUID
