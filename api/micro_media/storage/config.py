from uuid import UUID
from typing import Literal

from pydantic import BaseModel, model_validator

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

    @model_validator(mode="after")
    def validate_default_storage(self):
        valid_storage_ids = list(
            map(lambda storage: storage.id, self.storages)
        )

        # Take first thumbnail as default if it's not manually set
        if not self.default_storage and valid_storage_ids:
            self.default_storage = valid_storage_ids[0]

        # Check if default_size is valid
        if (
            self.default_storage
            and self.default_storage not in valid_storage_ids
        ):
            raise ValueError("`default_storage` must be present in `storages`")

        return self
