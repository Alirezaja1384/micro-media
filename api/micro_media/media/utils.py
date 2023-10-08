from typing import cast
from .exceptions import InvalidFileExtensionError, InvalidFileNameError


def split_filename(filename: str) -> tuple[str, str]:
    if not filename or "." not in filename:
        raise InvalidFileNameError("Invalid file name.")

    name, extension = cast(tuple[str, str], filename.rsplit(".", maxsplit=1))

    if not extension.isalnum():
        raise InvalidFileExtensionError(
            "Invalid File extension", extension=extension
        )

    return name, extension


def get_file_extension(filename: str) -> str:
    return split_filename(filename=filename)[1]


def change_file_extension(filename: str, new_extension: str) -> str:
    return split_filename(filename=filename)[0] + "." + new_extension.lower()
