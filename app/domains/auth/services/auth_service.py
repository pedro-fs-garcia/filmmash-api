from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from app.core.security import JWTService, PasswordSecurity
from app.domains.auth.enums import SessionStatus

from ..exceptions import InvalidPasswordError, UserNotFoundError, UserPasswordNotConfiguredError
from ..schemas import CreateSessionDTO, CreateUserDTO, RegisterUserRequest, UserLoginRequest
from ..services.session_service import SessionService
from .user_service import UserService


class AuthService:
    def __init__(
        self,
        user_service: UserService,
        session_service: SessionService,
        jwt_service: JWTService,
        password_security: PasswordSecurity,
    ):
        self.user_service = user_service
        self.session_service = session_service
        self.jwt_service = jwt_service
        self.passwordSecurity = password_security

    async def register(self, dto: RegisterUserRequest) -> dict[str, Any]:
        password_hash = self.passwordSecurity.generate_password_hash(dto.password)
        create_user_dto = CreateUserDTO(
            email=dto.email, password_hash=password_hash, username=dto.username
        )
        new_user = await self.user_service.create(create_user_dto)
        access_token = self.jwt_service.create_access_token(new_user.id, [])
        refresh_token = self.jwt_service.create_refresh_token(new_user.id, [])
        refresh_token_hash = self.passwordSecurity.generate_token_hash(refresh_token)

        await self.init_session(new_user.id, refresh_token_hash)

        return {
            "id": str(new_user.id),
            "email": new_user.email,
            "username": new_user.username,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    async def login(self, dto: UserLoginRequest) -> tuple[str, str]:
        user = await self.user_service.get_by_email(email=dto.email)
        if user is None:
            raise UserNotFoundError()

        password_hash = user.password_hash
        if password_hash is None:
            raise UserPasswordNotConfiguredError()

        is_authenticated = self.passwordSecurity.verify_password(dto.password, password_hash)
        if not is_authenticated:
            raise InvalidPasswordError(user.email)

        access_token = self.jwt_service.create_access_token(user.id, [])
        refresh_token = self.jwt_service.create_refresh_token(user.id, [])
        refresh_token_hash = self.passwordSecurity.generate_token_hash(refresh_token)

        await self.init_session(user.id, refresh_token_hash)

        return (access_token, refresh_token)

    async def init_session(self, user_id: UUID, refresh_token_hash: str) -> None:
        session_dto = CreateSessionDTO(
            user_id=user_id,
            refresh_token_hash=refresh_token_hash,
            status=SessionStatus.ACTIVE,
            expires_at=datetime.now() + timedelta(days=7),
            device_info=None,
            user_agent=None,
            ip_address=None,
            last_used_at=datetime.now(),
        )
        await self.session_service.create(session_dto)
