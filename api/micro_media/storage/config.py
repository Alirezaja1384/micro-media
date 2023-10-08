from uuid import UUID
from typing import Literal

from pydantic import BaseModel

StorageProvider = Literal["s3"]


class S3Config(BaseModel):
    endpoint_url: str | None = None
    access_key_id: str
    secret_access_key: str
    bucket_name: str


class Storage(BaseModel):
    id: UUID
    provider: StorageProvider = "s3"
    random_filenames: bool = True

    s3: S3Config


class StoragesConfig(BaseModel):
    default_storage: UUID | None = None
    storages: list[Storage]
