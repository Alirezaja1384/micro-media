import enum
from uuid import uuid4

import sqlalchemy as sa
from .base import Base


class MediaType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"


class Media(Base):
    __tablename__ = "media"

    id = sa.Column(sa.UUID, primary_key=True, default=uuid4)

    title = sa.Column(sa.String, nullable=True)
    description = sa.Column(sa.String, nullable=True)

    media_type = sa.Column(
        sa.Enum(*[choice.value for choice in MediaType], name="media_type"),
        nullable=False,
        index=True,
    )

    ack = sa.Column(sa.Boolean, nullable=False, default=False, index=True)

    owner_id = sa.Column(sa.UUID, nullable=False, index=True)
    storage_id = sa.Column(sa.UUID, nullable=False, index=True)
    file_identifier = sa.Column(sa.String, nullable=False, index=True)

    __table_args__ = (
        sa.UniqueConstraint(
            "storage_id", "file_identifier", name="unique_identifier"
        ),
    )
