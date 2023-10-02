from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware

from auth_utils import APIKeyAuthBackend, AuthBackendsWrapper, JWTAuthBackend
from fastapi_pagination import add_pagination

from micro_media.schemas import JWTUser
from micro_media.routers import router as base_router
from micro_media.auth import validate_api_keys, get_api_key_user
from micro_media.exception_handlers import register_exception_handlers
from micro_media.settings import (
    DEBUG,
    APP_NAME,
    JWT_DECODE_KEY,
    JWT_DECODE_ALGORITHMS,
    JWT_AUDIENCE,
    JWT_ISSUER,
    CORS_ALLOWED_ORIGINS,
)

app = FastAPI(
    title=APP_NAME,
    docs_url="/docs",
    redoc_url="/redoc",
    debug=DEBUG,
)

app.include_router(base_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(
    AuthenticationMiddleware,
    backend=AuthBackendsWrapper(
        JWTAuthBackend(
            key=JWT_DECODE_KEY,
            decode_algorithms=JWT_DECODE_ALGORITHMS,
            user_class=JWTUser,
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER,
        ),
        APIKeyAuthBackend(get_user=get_api_key_user),
    ),
)

add_pagination(app)
register_exception_handlers(app=app)


@app.on_event("startup")
async def startup():
    validate_api_keys()
