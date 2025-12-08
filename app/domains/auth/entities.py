from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from .enums import AuthProvider, SessionStatus


@dataclass
class Permission:
    id: int
    name: str
    description: str | None = None


@dataclass
class Role:
    id: int
    name: str
    description: str | None = None


@dataclass
class RoleWithPermissions(Role):
    permissions: list[Permission] | None = None


@dataclass
class PermissionWithRoles(Permission):
    roles: list[Role] | None = None


@dataclass
class Session:
    id: UUID
    user_id: UUID
    refresh_token_hash: str
    status: SessionStatus
    device_info: dict[str, str | None]
    auth_provider: AuthProvider
    expires_at: datetime
    created_at: datetime
    user_agent: str | None = None
    ip_address: str | None = None
    provider_account_id: str | None = None
    last_used_at: datetime | None = None

    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.now(UTC) > self.expires_at

    def is_active(self) -> bool:
        return self.status == SessionStatus.ACTIVE

    def is_valid(self) -> bool:
        """Session is valid if active and not expired."""
        return self.is_active() and not self.is_expired()

    def is_revoked(self) -> bool:
        """Check if session was explicitly revoked."""
        return self.status == SessionStatus.REVOKED

    def mark_used(self) -> None:
        """Update last used timestamp."""
        self.last_used_at = datetime.now(UTC)

    def revoke(self) -> None:
        """Revoke this session."""
        self.status = SessionStatus.REVOKED
