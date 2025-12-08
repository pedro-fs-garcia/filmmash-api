from enum import Enum


class SessionStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    INVALID = "invalid"
    REVOKED = "revoked"


class AuthProvider(Enum):
    LOCAL = "local"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
