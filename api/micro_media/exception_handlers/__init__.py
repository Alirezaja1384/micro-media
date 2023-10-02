from fastapi import FastAPI
from . import sqlalchemy


def register_exception_handlers(app: FastAPI):
    sqlalchemy.register_exception_handlers(app=app)
