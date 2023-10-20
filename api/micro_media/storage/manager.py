from abc import ABCMeta, abstractmethod
from io import BytesIO
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import aioboto3

from .config import S3Config, Storage

if TYPE_CHECKING:
    from types_aiobotocore_s3.client import S3Client


class AbstractStorageManager(metaclass=ABCMeta):
    storage: Storage

    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    @property
    def storage_id(self) -> UUID:
        return self.storage.id

    @abstractmethod
    async def save_media(
        self,
        media_type: str,
        owner_id: UUID,
        filename: str,
        file: BytesIO,
        **kwargs,
    ) -> str:
        """Saves given file to the storage.

        Args:
            media_type (str): The media's types. Can be used for splitting
                different media files.

            owner_id (UUID): The file owner's id. Can be used for splitting
                each user's media files.

            filename (str): The file's filename.

            file (BytesIO): File content.

        Returns:
            str: File's identifier.
        """

    @abstractmethod
    async def generate_file_link(self, file_identifier: str, **kwargs) -> str:
        """Generates a link for given file identifier.

        Args:
            file_identifier (str): Media's file identifier.

        Returns:
            str: The file's link.
        """


class S3StorageManager(AbstractStorageManager):
    storage: Storage
    session: aioboto3.Session

    def __init__(self, storage: Storage) -> None:
        super().__init__(storage)
        self.session = aioboto3.Session(
            aws_access_key_id=self.storage_conf.access_key_id,
            aws_secret_access_key=self.storage_conf.secret_access_key,
        )

    @property
    def storage_conf(self) -> S3Config:
        return self.storage.s3

    @property
    def client(self) -> "S3Client":
        return self.session.client(
            "s3", endpoint_url=self.storage_conf.endpoint_url
        )

    def _generate_object_key(
        self, media_type: str, owner_id: UUID, filename: str
    ) -> str:
        """
        Generates an s3 object key with the following formats:
            - random_filename enabled:
                {media_type}/{owner_id[:8]}/{random}.{original_extension}
            - random_filename disabled:
                {media_type}/{owner_id[:8]}/{filename}

        Args:
            media_type (str): The media type (image/video/...).

            owner_id (UUID): Media owner's id.

            filename (str): Original filename. Might be overridden when
                storage's random_filename is enabled.

        Raises:
            ValueError: When filename has not extension

        Returns:
            str: Generated object key.
        """
        if "." not in filename:
            raise ValueError("Invalid filename.")

        if self.storage.random_filenames:
            ext = filename.rsplit(".", maxsplit=1)[1]
            filename = f"{uuid4()}.{ext}"

        return "/".join((media_type, str(owner_id)[:8], filename))

    async def save_media(
        self,
        media_type: str,
        owner_id: UUID,
        filename: str,
        file: BytesIO,
        **kwargs,
    ) -> str:
        """
        Uploads given file to S3.

        Args:
            media_type (str): The media type (image/video/...).

            owner_id (UUID): Media owner's id.

            filename (str): Original filename. Might be overridden when
                storage's random_filename is enabled.

            file (BytesIO): The file content.

        Returns:
            str: The object key as file identifier.
        """
        async with self.client as s3_client:
            key = self._generate_object_key(
                media_type=media_type, owner_id=owner_id, filename=filename
            )

            await s3_client.put_object(
                Key=key,
                Body=file.getvalue(),
                Bucket=self.storage_conf.bucket_name,
            )

            return key

    async def generate_file_link(
        self, file_identifier: str, expires_in: int = 3600, **kwargs
    ) -> str:
        """
        Generate a file link for given file_identifier.

        Args:
            file_identifier (str): The object key returned from save_media().
            expires_in (int, optional): The amount of time in seconds which
                the desired link will bed valid. Defaults to 3600.

        Returns:
            str: The object's link.
        """
        async with self.client as s3_client:
            return await s3_client.generate_presigned_url(
                "get_object",
                ExpiresIn=expires_in,
                Params={
                    "Bucket": self.storage_conf.bucket_name,
                    "Key": file_identifier,
                },
            )
