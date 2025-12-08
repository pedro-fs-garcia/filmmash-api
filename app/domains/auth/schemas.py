from typing import Literal

from pydantic import BaseModel


class UserCreatedResponse(BaseModel):
    id: str
    email: str
    name: str
    token: str


class CreateUserRequest(BaseModel):
    email: str
    name: str
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
