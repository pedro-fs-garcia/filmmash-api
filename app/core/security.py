from datetime import UTC, datetime
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

    def generate_token_hash(self, token: str) -> str:
        hashed_token: str = self.pwd_context.hash(token)
        return hashed_token


class JWTService:
    def __init__(self) -> None:
        self.pwd_context = CryptContext(schemes=["argon2"], default="argon2", deprecated="auto")
        self.secret_key: str = settings.JWT_SECRET_KEY
        self.algorithm: str = settings.JWT_ALGORITHM
        self.expiration_time: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_expiration_time: int = settings.REFRESH_TOKEN_EXPIRE_DAYS

    class TokenType(Enum):
        ACCESS = "access"
        REFRESH = "refresh"

    def calculates_expiration_date(self, token_type: TokenType) -> datetime:
        match token_type:
            case self.TokenType.ACCESS:
                return datetime.now(UTC) + settings.access_token_timedelta
            case self.TokenType.REFRESH:
                return datetime.now(UTC) + settings.refresh_token_timedelta
            case _:
                raise ValueError("Invalid token type")

    def create_token(self, user_id: UUID, session_id: UUID, token_type: TokenType) -> str:
        token_payload: dict[str, Any] = {
            "sub": str(user_id),
            "exp": self.calculates_expiration_date(token_type),
            "iat": datetime.now(UTC),
            "iss": settings.project_identifier,
            "aud": settings.project_client_identifier,
            "type": token_type.value,
            "sid": str(session_id),
        }
        token: str = jwt.encode(token_payload, self.secret_key, algorithm=self.algorithm)
        return token

    def decode_token(self, token: str) -> dict[str, Any]:
        try:
            token_payload: dict[str, Any] = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            return token_payload
        except jwt.ExpiredSignatureError as err:
            raise ValueError("Token has expired") from err
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token") from None
        except Exception:
            raise ValueError("Invalid token") from None

    def create_access_token(self, user_id: UUID, session_id: UUID) -> str:
        return self.create_token(user_id, session_id, self.TokenType.ACCESS)

    def create_refresh_token(self, user_id: UUID, session_id: UUID) -> str:
        return self.create_token(user_id, session_id, self.TokenType.REFRESH)

    def decode_access_token(self, token: str) -> dict[str, Any]:
        token_payload = self.decode_token(token)
        if token_payload.get("type") != self.TokenType.ACCESS.value:
            raise ValueError("Invalid token type")
        return token_payload

    def decode_refresh_token(self, token: str) -> dict[str, Any]:
        token_payload = self.decode_token(token)
        if token_payload.get("type") != self.TokenType.REFRESH.value:
            raise ValueError("Invalid token type")
        return token_payload

    def hash_token(self, token: str) -> str:
        hashed_token: str = self.pwd_context.hash(token)
        return hashed_token
