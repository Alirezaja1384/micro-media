from uuid import UUID
from pydantic import BaseModel
from micro_media.utils import APIModel

from ..media import MediaType


class InternalMediaRead(APIModel):
    id: UUID
    title: str | None = None
    description: str | None = None
    media_type: MediaType
    owner_id: UUID
    ack: bool


class BulkMediaAckFilters(BaseModel):
    owner_id: UUID | None = None
    media_type: MediaType | None = None
    first_ack: bool = False
