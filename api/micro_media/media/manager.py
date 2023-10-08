from io import BytesIO
from typing import Callable, Generic, TypeVar

from PIL import Image

from .exceptions import InvalidFileExtensionError, FileTooLargeError
from .config import BaseMediaTypeConfig, ImageMediaConfig
from .utils import change_file_extension, get_file_extension


T = TypeVar("T", bound=BaseMediaTypeConfig)


class BaseMediaManager(Generic[T]):
    media_type: str
    config: T

    def __init__(self, config: T, media_type: str = ""):
        self.media_type = media_type
        self.config = config

    def validate_media(
        self, filename: str, file: BytesIO
    ) -> tuple[str, BytesIO]:
        """Validates the filename and file.

        Args:
            filename (str): The file's filename.
            file (BinaryIO): The file's content.

        Returns:
            tuple[str, BytesIO]: Validated filename and file.
        """
        # Run UploadFile validators one by one
        for validator in self.get_validators():
            filename, file = validator(filename, file)

        return filename, file

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
