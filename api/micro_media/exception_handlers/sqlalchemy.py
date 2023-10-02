import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, NoResultFound


logger = logging.getLogger(__name__)


async def no_result_found_exception_handler(
    request: Request, exc: NoResultFound
):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def integrityerror_exception_handler(
    request: Request, exc: IntegrityError
):
    logging.exception(exc)

    return JSONResponse(
        status_code=422,
        content={
            "detail": [
                {
                    "loc": [],
                    "msg": "خطای پایگاه داده",
                    "type": "IntegrityError",
                }
            ]
        },
    )


def register_exception_handlers(app: FastAPI):
    app.exception_handler(IntegrityError)(integrityerror_exception_handler)
    app.exception_handler(NoResultFound)(no_result_found_exception_handler)
