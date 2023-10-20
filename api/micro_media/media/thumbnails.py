import hmac
import base64
import hashlib
from urllib.parse import urljoin

from micro_media.settings import (
    IMGPROXY_HOST,
    IMGPROXY_SALT,
    IMGPROXY_KEY,
    IMGPROXY_RESIZE_ENLARGE,
)
from .config import ImageMediaThumbnailSizeConfig


class IMGProxyThumbnailManager:
    @staticmethod
    def _get_processing_options(thumbnail_size: ImageMediaThumbnailSizeConfig):
        enlarge = 1 if IMGPROXY_RESIZE_ENLARGE else 0

        return (
            f"rs:fit:{thumbnail_size.width}:{thumbnail_size.height}:{enlarge}"
        )

    @staticmethod
    def _get_encoded_path_signature(unsigned_path: str) -> bytes:
        if not unsigned_path.startswith("/"):
            raise ValueError("`unsigned_path` must start with `/`.")

        signature = hmac.new(
            key=bytes.fromhex(IMGPROXY_KEY),
            msg=bytes.fromhex(IMGPROXY_SALT) + unsigned_path.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()

        return base64.urlsafe_b64encode(signature).rstrip(b"=")

    def get_thumbnail_link(
        self,
        original_file_link: str,
        thumbnail_size: ImageMediaThumbnailSizeConfig,
    ) -> str:
        processing_options = self._get_processing_options(
            thumbnail_size=thumbnail_size
        )

        encoded_file_link = base64.urlsafe_b64encode(
            original_file_link.encode("utf-8")
        ).decode("utf-8")

        unsigned_path = f"/{processing_options}/{encoded_file_link}"

        encoded_signature = self._get_encoded_path_signature(
            unsigned_path=unsigned_path
        ).decode("utf-8")

        return urljoin(IMGPROXY_HOST, f"/{encoded_signature}{unsigned_path}")
