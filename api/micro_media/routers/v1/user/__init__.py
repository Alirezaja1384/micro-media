from fastapi import APIRouter, Depends
from auth_utils import auth_required
from micro_media.schemas import JWTUser

from . import media

router = APIRouter(dependencies=[Depends(auth_required(user_class=JWTUser))])
router.include_router(media.router, prefix="/media")
