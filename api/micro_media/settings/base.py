from typing import cast
from decouple import config

from .utils import to_list


DEBUG = cast(bool, config("DEBUG", default=False, cast=bool))

APP_NAME = cast(str, config("APP_NAME", default="MicroMedia"))

JWT_DECODE_KEY = cast(str, config("JWT_DECODE_KEY"))
JWT_DECODE_ALGORITHMS = cast(
    list[str], config("JWT_DECODE_ALGORITHMS", cast=to_list)
)
JWT_AUDIENCE = cast(str | None, config("JWT_AUDIENCE", default=None))
JWT_ISSUER = cast(str | None, config("JWT_ISSUER", default=None))

CORS_ALLOWED_ORIGINS = cast(
    list[str], config("CORS_ALLOWED_ORIGINS", cast=to_list)
)

SQLALCHEMY_ECHO = cast(
    bool, config("SQLALCHEMY_ECHO", cast=bool, default=DEBUG)
)
SQLALCHEMY_CONN_STR = cast(str, config("SQLALCHEMY_CONN_STR"))

API_KEYS_FILE = cast(
    str | None, config("API_KEYS_FILE", default="api_keys.json")
)
