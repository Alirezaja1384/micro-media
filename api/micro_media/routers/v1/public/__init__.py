from fastapi import APIRouter
from . import media

router = APIRouter()
router.include_router(media.router, prefix="/media")
