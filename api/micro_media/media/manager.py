import asyncio
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Generic, TypeVar

from PIL import Image

from .exceptions import InvalidFileExtensionError, FileTooLargeError
from .config import (
    BaseMediaTypeConfig,
    ImageMediaConfig,
    ImageMediaThumbnailSizeConfig,
)
from .utils import change_file_extension, get_file_extension


T = TypeVar("T", bound=BaseMediaTypeConfig)


thread_pool = ThreadPoolExecutor()


class BaseMediaManager(Generic[T]):
    media_type: str
    config: T

    def __init__(self, config: T, media_type: str = ""):
        self.media_type = media_type
        self.config = config

    def validate_media(
        self, filename: str, data: bytes
    ) -> tuple[str, BytesIO]:
        """Validates the filename and file.

        Args:
            filename (str): The file's filename.
            file (BinaryIO): The file's content.

        Returns:
            tuple[str, BytesIO]: Validated filename and file.
        """
        file = BytesIO(data)

        # Run UploadFile validators one by one
        for validator in self.get_validators():
            filename, file = validator(filename, file)
            file.seek(0)

        return filename, file

    async def avalidate_media(
        self, filename: str, data: bytes
    ) -> tuple[str, BytesIO]:
        """Validates the filename and file asynchronously.

        Args:
            filename (str): The file's filename.
            file (BinaryIO): The file's content.

        Returns:
            tuple[str, BytesIO]: Validated filename and file.
        """
        return await asyncio.get_event_loop().run_in_executor(
            thread_pool, self.validate_media, filename, data
        )

    def get_validators(
        self,
    ) -> list[Callable[[str, BytesIO], tuple[str, BytesIO]]]:
        """
        Returns the validator methods.

        Returns:
            list[Callable[[str, BytesIO], tuple[str, BytesIO]]]: Validator
                methods which take filename and file content and return
                the validated filename and file content.
        """
        return [self.validate_file_size, self.validate_allowed_formats]

    def validate_allowed_formats(
        self, filename: str, file: BytesIO
    ) -> tuple[str, BytesIO]:
        """
        Checks if the file extension is valid.

        Args:
            filename (str): The file's filename.
            file (BytesIO): The file's content.

        Raises:
            InvalidFileExtensionError: When given filename's is not
                present in the config's `allowed_formats`.

        Returns:
            tuple[str, BytesIO]: Validated filename and file content.
        """
        extension = get_file_extension(filename)

        if self.config.allowed_formats:
            if extension not in self.config.allowed_formats:
                raise InvalidFileExtensionError(
                    f"Extension `{extension}` is not allowed.",
                    extension=extension,
                    valid_extensions=self.config.allowed_formats,
                    media_type=self.media_type,
                )

        return filename, file

    def validate_file_size(
        self, filename: str, file: BytesIO
    ) -> tuple[str, BytesIO]:
        """
        Checks if file size does not exceed the media_type's size limit.

        Args:
            filename (str): The file's filename.
            file (BytesIO): The file's content.

        Raises:
            FileTooLargeError: When file size exceeds the `max_file_size`.

        Returns:
            tuple[str, BytesIO]: Validated filename and file content.
        """
        max_file_size = self.config.max_file_size

        if max_file_size:
            file_size = file.getbuffer().nbytes

            if file_size > max_file_size:
                raise FileTooLargeError(
                    "Maximum file size exceeded.",
                    file_size=file_size,
                    max_file_size=max_file_size,
                    media_type=self.media_type,
                )

        return filename, file


class ImageMediaManager(BaseMediaManager[ImageMediaConfig]):
    def get_validators(
        self,
    ) -> list[Callable[[str, BytesIO], tuple[str, BytesIO]]]:
        """
        Returns the base and additional validator methods.

        Returns:
            list[Callable[[str, BytesIO], tuple[str, BytesIO]]]: validator
                methods.
        """
        return [
            *super().get_validators(),
            self.resize_and_set_format,
        ]

    def resize_and_set_format(
        self, filename: str, file: BytesIO
    ) -> tuple[str, BytesIO]:
        """
        Resizes and changes the format of the image if needed.

        Args:
            filename (str): The file's filename.
            file (BytesIO): The file's content.

        Returns:
            tuple[str, BytesIO]: Validated filename and file content.
        """
        result = BytesIO()
        with Image.open(file) as img:
            img_format = img.format

            if resize := self.config.resize:
                img.thumbnail(
                    (resize.max_width, resize.max_height),
                    resample=Image.Resampling.LANCZOS,
                )

            if force_format := self.config.force_format:
                img_format = force_format.pil_format
                filename = change_file_extension(
                    filename, new_extension=force_format.file_extension
                )

                if img.mode != force_format.convert_mode:
                    img = img.convert(force_format.convert_mode)

            img.save(result, format=img_format)

        return filename, result

    def get_thumbnail_sizes(self) -> list[str]:
        """Returns list of available thumbnail sizes.

        Returns:
            list[str]: Available thumbnail sizes.
        """
        if self.config.thumbnails:
            return list(self.config.thumbnails.sizes.keys())

        return []

    def get_thumbnail_size_conf(
        self, size_name: str | None
    ) -> ImageMediaThumbnailSizeConfig | None:
        """
        Finds the thumbnail size config for the given size name.

        Args:
            size_name (str | None): Thumbnail size name or None.
                Use None to get the default thumbnail size config.

        Returns:
            ImageMediaThumbnailSizeConfig | None: The thumbnail size config.
        """
        thumbnails_conf = self.config.thumbnails

        try:
            if not thumbnails_conf or not (
                size_name or thumbnails_conf.default_size
            ):
                return None

            if not size_name:
                size_name = thumbnails_conf.default_size

            return next(
                thumb_conf
                for thumb_size, thumb_conf in thumbnails_conf.sizes.items()
                if thumb_size == size_name
            )
        except StopIteration:
            return None
