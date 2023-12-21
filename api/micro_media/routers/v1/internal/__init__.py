from fastapi import APIRouter, Depends
from auth_utils import auth_required
from micro_media.schemas import APIKeyUser

from . import media

router = APIRouter(
    dependencies=[Depends(auth_required(user_class=APIKeyUser))]
)
router.include_router(media.router, prefix="/media")
