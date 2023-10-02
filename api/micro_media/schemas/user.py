from uuid import UUID
from auth_utils import BaseUser
from pydantic import BaseModel, Field


class JWTPermission(BaseModel):
    is_staff: bool = False
    claims: list[str] = []
    roles: list[str] = []


class JWTUser(BaseUser, BaseModel):
    sub: UUID
    username: str

    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")

    is_staff: bool = Field(default=False, alias="isStaff")
    is_superuser: bool = Field(default=False, alias="isSuperUser")

    roles: list[str] = []
    claims: list[str] = []

    def has_perm(self, perm: JWTPermission):
        if not isinstance(perm, JWTPermission):
            raise TypeError(
                f"Incompatible permission type `{perm.__class__.__name__}`"
            )

        def validate_is_staff() -> bool:
            # If user does not need to be staff or is an staff member
            return not perm.is_staff or self.is_staff

        def validate_roles() -> bool:
            # If user has all the given roles
            return all(map(lambda role: role in self.roles, perm.roles))

        def validate_claims() -> bool:
            # If user has all the given claims
            return all(map(lambda claim: claim in self.claims, perm.claims))

        validators = [
            validate_is_staff,
            validate_roles,
            validate_claims,
        ]

        # True if all validators return True, otherwise False.
        return self.is_superuser or all(
            map(lambda validator: validator(), validators)
        )

    @property
    def identity(self) -> UUID:
        return self.sub

    @property
    def display_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


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
