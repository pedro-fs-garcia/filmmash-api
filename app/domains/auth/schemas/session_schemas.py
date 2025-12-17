from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, model_validator

from ..enums import DeviceType, SessionStatus


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
