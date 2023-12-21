from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from fastapi.security.api_key import APIKeyHeader

from micro_media.settings import DEBUG
from . import user, public, internal

router = APIRouter(
    # Enables swagger's authorize button
    dependencies=[
        Depends(HTTPBearer(auto_error=False)),
        Depends(APIKeyHeader(name="X-API-KEY", auto_error=False)),
    ]
)

router.include_router(user.router, prefix="/user", tags=["User"])
router.include_router(public.router, prefix="/public", tags=["Public"])
router.include_router(
    internal.router,
    prefix="/internal",
    tags=["Internal"],
    include_in_schema=DEBUG,
)
