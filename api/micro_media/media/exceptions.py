from typing import Sequence


class InvalidFileNameError(ValueError):
    pass


class InvalidFileExtensionError(ValueError):
    extension: str
    valid_extensions: Sequence[str] | None
    media_type: str

    def __init__(
        self,
        *args: object,
        extension: str = "",
        valid_extensions: Sequence[str] | None = None,
        media_type: str = ""
    ) -> None:
        super().__init__(*args)
        self.extension = extension
        self.valid_extensions = valid_extensions
        self.media_type = media_type


class FileTooLargeError(ValueError):
    file_size: int
    max_file_size: int
    media_type: str

    def __init__(
        self,
        *args: object,
        file_size: int,
        max_file_size: int,
        media_type: str = ""
    ) -> None:
        super().__init__(*args)
        self.file_size = file_size
        self.max_file_size = max_file_size
        self.media_type = media_type
