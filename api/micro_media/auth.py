import json
import hashlib
from functools import lru_cache
from auth_utils.backends import logging

from micro_media.schemas import APIKeyUser
from micro_media.settings import API_KEYS_FILE

logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def get_api_key_users() -> list[APIKeyUser]:
    if not API_KEYS_FILE:
        return []

    with open(API_KEYS_FILE, "r", encoding="utf-8") as keys_file:
        return [APIKeyUser(**key_dict) for key_dict in json.load(keys_file)]


async def get_api_key_user(api_key: str) -> APIKeyUser | None:
    api_key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()

    try:
        return next(
            key_user
            for key_user in get_api_key_users()
            if key_user.sha256 == api_key_hash
        )
    except StopIteration:
        return None


def validate_api_keys() -> None:
    api_keys = get_api_key_users()

    if not api_keys:
        logger.warning("No API key found!")
    else:
        logger.info("%s API keys registered successfully.", len(api_keys))
