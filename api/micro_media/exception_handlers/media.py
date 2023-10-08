import logging
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from micro_media.media import (
    InvalidFileNameError,
    InvalidFileExtensionError,
    FileTooLargeError,
)


logger = logging.getLogger(__name__)


async def invalid_filename_exception_handler(
    request: Request, exc: InvalidFileNameError
):
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content={"detail": "نام فایل نامعتبر است."},
    )


async def invalid_file_extension_exception_handler(
    request: Request, exc: InvalidFileExtensionError
):
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content={
            "detail": (
                f"پسوند {exc.extension} برای محتوای نوع "
                f"{exc.media_type} نامعتبر است."
            ),
            "extension": exc.extension,
            "validExtensions": exc.valid_extensions,
            "mediaType": exc.media_type,
        },
    )


async def file_too_large_error_exception_handler(
    request: Request, exc: FileTooLargeError
):
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content={
            "detail": (
                "حجم فایل از حداکثر مقدار مجاز برای محتوای نوع "
                f"{exc.media_type} بیشتر است."
            ),
            "fileSize": exc.file_size,
            "maxFileSize": exc.max_file_size,
        },
    )


def register_exception_handlers(app: FastAPI):
    app.exception_handler(InvalidFileNameError)(
        invalid_filename_exception_handler
    )
    app.exception_handler(InvalidFileExtensionError)(
        invalid_file_extension_exception_handler
    )
    app.exception_handler(FileTooLargeError)(
        file_too_large_error_exception_handler
    )
