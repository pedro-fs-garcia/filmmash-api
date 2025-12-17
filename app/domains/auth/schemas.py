import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, model_validator

from .enums import DeviceType, OAuthProvider, SessionStatus


class UserCreatedResponse(BaseModel):
    id: str
    email: str
    username: str
    access_token: str
    refresh_token: str


class RefreshSessionRequest(BaseModel):
    refresh_token: str


class RefreshSessionResponse(BaseModel):
    access_token: str
    refresh_token: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str


class RegisterUserRequest(BaseModel):
    email: str
    username: str
    password: str


class UserLoginRequest(BaseModel):
    email: str
    password: str


class SessionDeviceInfo(BaseModel):
    user_agent: str | None = None
    ip_address: str | None = None
    device_type: DeviceType | None = None
    os: str | None = None
    browser: str | None = None
    app_version: str | None = None

    def fingerprint(self) -> str:
        f_values = [self.device_type.value if self.device_type else None, self.os, self.browser]
        return " | ".join([str(v) for v in f_values if v is not None])


class CreateRoleDTO(BaseModel):
    name: str
    description: str | None = None

    @model_validator(mode="after")
    def validate_name(self) -> "CreateRoleDTO":
        role_name_re = re.compile(r"^[A-Za-z_]{3,}$")
        if not role_name_re.match(self.name):
            raise ValueError(
                "Role name can have only letters and _ and cannot have less than 3 characters."
            )
        return self


class ReplaceRoleDTO(CreateRoleDTO):
    pass


class UpdateRoleDTO(BaseModel):
    name: str | None = None
    description: str | None = None

    @model_validator(mode="after")
    def validate_name(self) -> "UpdateRoleDTO":
        role_name_re = re.compile(r"^[A-Za-z_]{3,}$")
        if self.name and not role_name_re.match(self.name):
            raise ValueError(
                "Role name can have only letters and _ and cannot have less than 3 characters."
            )
        return self


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


class CreateSessionDTO(BaseModel):
    user_id: UUID
    refresh_token_hash: str | None = None
    status: SessionStatus | None = None
    expires_at: datetime
    device_info: SessionDeviceInfo | None = None
    last_used_at: datetime | None = None

    @model_validator(mode="after")
    def validate_expiration(self) -> "CreateSessionDTO":
        if self.expires_at <= datetime.now():
            raise ValueError("expires_at must be in the future")
        return self


class UpdateSessionDTO(BaseModel):
    refresh_token_hash: str | None = None
    status: SessionStatus | None = None
    expires_at: datetime | None = None
    last_used_at: datetime | None = None
    device_info: SessionDeviceInfo | None = None
    user_agent: str | None = None
    ip_address: str | None = None


class RefreshSessionDTO(BaseModel):
    refresh_token_hash: str
    expires_at: datetime
