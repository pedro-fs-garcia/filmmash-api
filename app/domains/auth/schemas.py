from typing import Literal

from pydantic import BaseModel, model_validator

from .enums import OAuthProvider


class UserCreatedResponse(BaseModel):
    id: str
    email: str
    name: str
    token: str


class CreateUserRequest(BaseModel):
    email: str
    username: str
    password: str


class UserLoginRequest(BaseModel):
    email: str
    password: str


class SessionDeviceInfo(BaseModel):
    device_type: Literal["desktop", "mobile", "tablet"] | None
    os: str | None
    browser: str | None
    app_version: str | None


class CreateRoleDTO(BaseModel):
    name: str
    description: str


class ReplaceRoleDTO(BaseModel):
    name: str
    description: str


class UpdateRoleDTO(BaseModel):
    name: str | None = None
    description: str | None = None


class AddRolePermissionsDTO(BaseModel):
    ids: list[int]


class CreatePermissionDTO(BaseModel):
    name: str
    description: str


class ReplacePermissionDTO(BaseModel):
    name: str
    description: str


class UpdatePermissionDTO(BaseModel):
    name: str | None = None
    description: str | None = None


class CreateUserDTO(BaseModel):
    email: str
    password_hash: str | None = None
    username: str | None = None
    name: str | None = None
    oauth_provider: OAuthProvider | None = None
    oauth_provider_id: str | None = None
    is_active: bool = True
    is_verified: bool = False

    @model_validator(mode="after")
    def validate_auth_method(self) -> "CreateUserDTO":
        has_password = self.password_hash is not None
        has_username = self.username is not None
        has_oauth = self.oauth_provider is not None and self.oauth_provider_id is not None

        if not has_password and not has_oauth:
            raise ValueError("User must have either password or OAuth provider.")

        if has_password and not has_username:
            raise ValueError("User must have a name.")

        return self


class UpdateUserDTO(BaseModel):
    email: str | None = None
    password_hash: str | None = None
    username: str | None = None
    name: str | None = None
    oauth_provider: OAuthProvider | None = None
    oauth_provider_id: str | None = None
    is_active: bool | None = None
    is_verified: bool | None = None


class ReplaceUserDTO(CreateUserDTO):
    pass


class AddUserRolesDTO(BaseModel):
    role_ids: list[int]
