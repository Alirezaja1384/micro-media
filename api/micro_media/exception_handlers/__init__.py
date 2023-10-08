from fastapi import FastAPI
from . import sqlalchemy, media


def register_exception_handlers(app: FastAPI):
    sqlalchemy.register_exception_handlers(app=app)
    media.register_exception_handlers(app=app)
