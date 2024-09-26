from uuid import UUID
from typing import Self
from functools import cached_property, lru_cache

import yaml

from micro_media.settings import STORAGE_CONFIG_FILE
from .config import StoragesConfig, Storage
from .manager import AbstractStorageManager, S3StorageManager
from .exceptions import StorageNotFoundError


class StorageContext:
    config: StoragesConfig

    def __init__(self, config: StoragesConfig) -> None:
        self.config = config

    @cached_property
    def storages(self) -> dict[UUID, Storage]:
        """
        Returns a dictionary of storages with their ids as keys.

        Returns:
            dict[UUID, Storage]: The storages dictionary.
        """
        return {storage.id: storage for storage in self.config.storages}

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
                config=StoragesConfig.model_validate(
                    yaml.safe_load(config_file)
                )
            )

    @property
    def default_manager(self) -> AbstractStorageManager:
        """
        Returns the default manager if default storage is set.

        Raises:
            ValueError: If not default storage is set.

        Returns:
            AbstractStorageManager: The manager instance.
        """
        if not self.config.default_storage:
            raise ValueError("default_storage is not set.")

        return self.get_manager(self.config.default_storage)

    def get_storage(self, storage_id: UUID) -> Storage:
        """Finds the Storage object by its id.

        Args:
            storage_id (UUID): Storage id.

        Raises:
            StorageNotFoundError: If no matching storage found.

        Returns:
            Storage: The storage object.
        """
        try:
            return self.storages[storage_id]
        except KeyError as exc:
            raise StorageNotFoundError(
                f"Storage {storage_id} not found."
            ) from exc

    @lru_cache(maxsize=10)
    def get_manager(self, storage_id: UUID) -> AbstractStorageManager:
        """Creates a storage manager for given storage id.

        Args:
            storage_id (UUID): The storage's id.

        Raises:
            ValueError: When provider is unsupported.

        Returns:
            AbstractStorageManager: The storage manager object.
        """
        storage = self.get_storage(storage_id=storage_id)

        match storage.provider:
            case "s3":
                return S3StorageManager(storage=storage)
            case _:
                raise ValueError("Unsupported provider.")


STORAGE_CONTEXT = StorageContext.from_yaml_file(
    config_path=STORAGE_CONFIG_FILE
)
