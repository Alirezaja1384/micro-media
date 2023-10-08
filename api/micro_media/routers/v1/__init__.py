from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from . import user, public

router = APIRouter(
    dependencies=[
        Depends(
            HTTPBearer(auto_error=False)
        )  # Enables swagger's authorize button
    ]
)

router.include_router(user.router, prefix="/user", tags=["User"])
router.include_router(public.router, prefix="/public", tags=["Public"])
