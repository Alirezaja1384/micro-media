from typing import Any
from uuid import UUID
from auth_utils import BaseUser
from pydantic import BaseModel, Field


class JWTUser(BaseUser, BaseModel):
    sub: UUID

    def has_perm(self, perm: Any):
        return False

    @property
    def identity(self) -> UUID:
        return self.sub

    @property
    def display_name(self) -> str:
        return f"User {self.identity}"


class APIKeyPermission(BaseModel):
    scopes: list[str]


class APIKeyUser(BaseUser, BaseModel):
    sha256: str = Field(min_length=64, max_length=64)
    scopes: list[str]

    def has_perm(self, perm: APIKeyPermission) -> bool:
        if not isinstance(perm, APIKeyPermission):
            raise TypeError(
                f"Incompatible permission type `{perm.__class__.__name__}`"
            )

        def validate_scopes() -> bool:
            # If user has all the given scopes
            return all(map(lambda scope: scope in self.scopes, perm.scopes))

        validators = [validate_scopes]
        return all(map(lambda validator: validator(), validators))

    @property
    def identity(self) -> str:
        return self.sha256

    @property
    def display_name(self) -> str:
        masked_hash = self.identity.replace(self.identity[8:-8], "*****")
        return f"API key: {masked_hash}"
