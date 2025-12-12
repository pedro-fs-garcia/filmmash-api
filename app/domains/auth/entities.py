from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from .enums import OAuthProvider, SessionStatus


@dataclass
class Permission:
    id: int
    name: str
    description: str | None = None

    def __repr__(self) -> str:
        return f"<Permission {self.name}>"


@dataclass
class Role:
    id: int
    name: str
    description: str | None = None

    def __repr__(self) -> str:
        return f"<Role {self.name}>"


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
    auth_provider: OAuthProvider
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


@dataclass
class User:
    id: UUID
    email: str
    password_hash: str | None = None
    username: str | None = None
    name: str | None = None
    oauth_provider: OAuthProvider | None = None
    oauth_provider_id: str | None = None
    is_active: bool = True
    is_verified: bool = False

    def __repr__(self) -> str:
        return f"<User (id={self.id}, email={self.email})>"

    def validate_email(self) -> None:
        if "@" not in self.email:
            raise ValueError("Invalid email")
        if " " in self.email:
            raise ValueError("Email cannot contain spaces")
        if not self.email:
            raise ValueError("Email required")

    def validate_username(self) -> None:
        if self.username is None:
            return
        if not self.username.isidentifier():
            raise ValueError("Invalid username")
        if len(self.username) < 3:
            raise ValueError("Username too short")

    def has_oauth(self) -> bool:
        return self.oauth_provider is not None and self.oauth_provider_id is not None

    def has_password(self) -> bool:
        return self.password_hash is not None

    def can_oauth_login(self) -> bool:
        has_provider = self.oauth_provider is not None
        has_id = self.oauth_provider_id is not None
        return has_provider and has_id and self.is_active

    def can_local_login(self) -> bool:
        has_password = self.password_hash is not None
        has_username = self.username is not None
        return has_password and has_username and self.is_active

    def is_oauth_user(self) -> bool:
        return self.has_oauth()

    def is_local_user(self) -> bool:
        return self.password_hash is not None

    def can_login(self) -> bool:
        if not self.is_active:
            return False
        return self.can_local_login() or self.can_oauth_login()


@dataclass
class UserWithRoles(User):
    roles: list[Role] | None = None
