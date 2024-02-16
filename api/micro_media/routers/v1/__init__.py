from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from fastapi.security.api_key import APIKeyHeader

from micro_media.settings import DEBUG
from . import user, public, internal

auth_deps = [Depends(HTTPBearer(auto_error=False))]
if DEBUG:
    auth_deps.append(Depends(APIKeyHeader(name="X-API-KEY", auto_error=False)))

router = APIRouter(
    dependencies=auth_deps  # Enables swagger's authorize button
)

router.include_router(user.router, prefix="/user", tags=["User"])
router.include_router(public.router, prefix="/public", tags=["Public"])
router.include_router(
    internal.router,
    prefix="/internal",
    tags=["Internal"],
    include_in_schema=DEBUG,
)
