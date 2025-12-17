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


def enum_values(enum_class: type[Enum]) -> list[str]:
    """Return enum values for a given Enum class."""
    return [member.value for member in enum_class]
