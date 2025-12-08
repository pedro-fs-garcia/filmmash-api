from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any
from uuid import UUID

import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()


class PasswordSecurity:
    def __init__(self) -> None:
        self.pwd_context = CryptContext(schemes=["argon2"], default="argon2", deprecated="auto")

    def generate_password_hash(self, password: str) -> str:
        hashed_pass: str = self.pwd_context.hash(password)
        return hashed_pass

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        is_valid_password: bool = self.pwd_context.verify(plain_password, hashed_password)
        return is_valid_password

    def needs_rehash(self, hashed_password: str) -> bool:
        needs_rehash: bool = self.pwd_context.needs_update(hashed_password)
        return needs_rehash


class JWTService:
    def __init__(self) -> None:
        self.secret_key: str = settings.JWT_SECRET_KEY
        self.algorithm: str = settings.JWT_ALGORITHM
        self.expiration_time: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_expiration_time: int = settings.REFRESH_TOKEN_EXPIRE_DAYS

    class TokenType(Enum):
        ACCESS = "access"
        REFRESH = "refresh"

    def create_access_token(self, user_id: UUID, roles: list[str]) -> str:
        expire = datetime.now(UTC) + timedelta(minutes=self.expiration_time)
        token_payload: dict[str, Any] = {
            "sub": str(user_id),
            "roles": roles,
            "exp": expire,
            "iat": datetime.now(UTC),
            "type": self.TokenType.ACCESS.value,
        }
        token: str = jwt.encode(token_payload, self.secret_key, algorithm=self.algorithm)
        return token

    def decode_access_token(self, token: str) -> dict[str, Any]:
        try:
            token_payload: dict[str, Any] = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            if token_payload.get("type") != self.TokenType.ACCESS.value:
                raise ValueError("Invalid token type")

            user_id = token_payload.get("sub")
            roles = token_payload.get("roles")
            return {"user_id": user_id, "roles": roles}
        except jwt.ExpiredSignatureError as err:
            raise ValueError("Token has expired") from err
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token") from None
        except Exception:
            raise ValueError("Invalid token") from None

    def create_refresh_token(self, user_id: UUID, roles: list[str]) -> str:
        expire = datetime.now(UTC) + timedelta(days=self.refresh_expiration_time)
        token_payload: dict[str, Any] = {
            "sub": str(user_id),
            "roles": roles,
            "exp": expire,
            "iat": datetime.now(UTC),
            "type": self.TokenType.REFRESH.value,
        }
        token: str = jwt.encode(token_payload, self.secret_key, algorithm=self.algorithm)
        return token

    def validate_refresh_token(self, token: str) -> bool:
        try:
            token_payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            valid: bool = token_payload["type"] == self.TokenType.REFRESH.value
            return valid

        except Exception:
            return False
