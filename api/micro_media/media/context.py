from typing import Literal, Self, Type

import yaml

from micro_media.settings import MEDIA_CONFIG_FILE
from .config import MediaConfig
from .manager import BaseMediaManager, ImageMediaManager

MediaType = Literal["image", "video", "document"]
MEDIA_TYPE_MANAGERS: dict[MediaType, Type[BaseMediaManager]] = {
    "image": ImageMediaManager,
    "video": BaseMediaManager,
    "document": BaseMediaManager,
}


class MediaContext:
    config: MediaConfig
    _managers: dict[MediaType, BaseMediaManager]

    def __init__(self, config: MediaConfig):
        self.config = config

        # Generate media manager for configured media types.
        self._managers = {
            media_type: media_manager(
                config=getattr(self.config, media_type),
                media_type=media_type,
            )
            for (media_type, media_manager) in MEDIA_TYPE_MANAGERS.items()
        }

    @classmethod
    def from_yaml_file(cls, config_path: str) -> Self:
        """
        Initiates the context using the given yaml file.

        Args:
            config_path (str): YAML config file path.

        Returns:
            Self: The context instance.
        """
        with open(config_path, "r", encoding="utf-8") as config_file:
            return cls(
                config=MediaConfig.model_validate(yaml.safe_load(config_file))
            )

    def get_manager(self, media_type: MediaType) -> BaseMediaManager:
        """
        Returns the media_type's manager.

        Args:
            media_type (MediaType): The media type(image/video/document).

        Returns:
            BaseMediaManager: The media manager instance.
        """
        return self._managers[media_type]


MEDIA_CONTEXT = MediaContext.from_yaml_file(MEDIA_CONFIG_FILE)
