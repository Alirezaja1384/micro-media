from enum import Enum
from typing import Annotated, Literal

from uuid import UUID
from pydantic import Field, computed_field, create_model
from fastapi import File, Form, UploadFile

from micro_media.media.manager import ImageMediaManager
from micro_media.utils import APIModel
from micro_media.media import MEDIA_CONTEXT as MC


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
        media_type: Annotated[
            MediaType, Form(alias="mediaType", validation_alias="mediaType")
        ],
        title: Annotated[str | None, Form()] = None,
        description: Annotated[str | None, Form()] = None,
    ) -> "MediaCreate":
        return cls(
            title=title,
            description=description,
            media_type=media_type,
            file=file,
        )


THUMBNAIL_SIZES = MC.get_manager("image").get_thumbnail_sizes()

ThumbnailSizesModel = create_model(
    "ThumbnailSizesModel",
    **{size: (str, Field(...)) for size in THUMBNAIL_SIZES},
)


class MediaRead(MediaBase):
    id: UUID

    @computed_field
    def original_path(self) -> str:
        return f"/v1/public/media/original/{self.id}"

    @computed_field
    def thumbnail_paths(self) -> ThumbnailSizesModel | None:
        if self.media_type != MediaType.IMAGE:
            return None

        return ThumbnailSizesModel.model_validate(
            {
                size: f"/v1/public/media/thumbnail/{self.id}?size={size}"
                for size in THUMBNAIL_SIZES
            }
        )
