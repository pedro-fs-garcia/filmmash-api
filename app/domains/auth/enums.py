from enum import Enum


class SessionStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    INVALID = "invalid"
    REVOKED = "revoked"


class DeviceType(Enum):
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"


class OAuthProvider(Enum):
    LOCAL = "local"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
