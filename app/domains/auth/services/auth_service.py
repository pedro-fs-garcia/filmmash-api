from typing import Any
from uuid import UUID

from app.core.config import get_settings
from app.core.security import JWTService, PasswordSecurity
from app.domains.auth.entities import Session, User

from ..exceptions import (
    InvalidCredentialsError,
    InvalidPasswordError,
    InvalidSessionError,
    SessionNotFoundError,
    UserNotFoundError,
    UserPasswordNotConfiguredError,
)
from ..schemas import (
    CreateUserDTO,
    RefreshSessionRequest,
    RegisterUserRequest,
    SessionDeviceInfo,
    UserLoginRequest,
)
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

    async def register(
        self, dto: RegisterUserRequest, device_info: SessionDeviceInfo | None = None
    ) -> dict[str, Any]:
        password_hash = self.passwordSecurity.generate_password_hash(dto.password)
        create_user_dto = CreateUserDTO(
            email=dto.email, password_hash=password_hash, username=dto.username
        )
        user = await self.user_service.create(create_user_dto)
        access_token, refresh_token = await self.session_service.init_session(user.id, device_info)
        return {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    async def login(
        self, dto: UserLoginRequest, device_info: SessionDeviceInfo | None = None
    ) -> tuple[str, str]:
        user = await self.user_service.get_by_email(email=dto.email)
        if user is None:
            raise UserNotFoundError()

        password_hash = user.password_hash
        if password_hash is None:
            raise UserPasswordNotConfiguredError()

        is_authenticated = self.passwordSecurity.verify_password(dto.password, password_hash)
        if not is_authenticated:
            raise InvalidPasswordError(user.email)

        return await self.session_service.init_session(user.id, device_info)

    async def _validate_refresh_request(
        self,
        session: Session,
        current_user_id: UUID,
        dto: RefreshSessionRequest,
        device_info: SessionDeviceInfo | None,
    ) -> bool:
        current_token_hash = self.passwordSecurity.generate_token_hash(dto.refresh_token)

        if session.refresh_token_hash != current_token_hash:
            return False

        # TODO: Implement log to track ip changes.
        if not session.matches_device_fingerprint(device_info):
            # TODO: send email "Active session tried to be acessed from a different source."
            return False

        token_user_id = UUID(self.jwt_service.decode_refresh_token(dto.refresh_token)["user_id"])
        return token_user_id == current_user_id

    async def refresh_session(
        self,
        current_user: User,
        current_session: Session,
        dto: RefreshSessionRequest,
        device_info: SessionDeviceInfo | None,
    ) -> dict[str, str]:
        valid_refresh = await self._validate_refresh_request(
            current_session, current_user.id, dto, device_info
        )
        if not valid_refresh:
            await self.session_service.revoke(current_session.id)
            raise InvalidSessionError("New login required.")

        access_token = self.jwt_service.create_access_token(
            current_session.user_id, current_session.id
        )
        new_refresh_token = self.jwt_service.create_refresh_token(
            current_session.user_id, current_session.id
        )
        new_refresh_token_hash = self.passwordSecurity.generate_token_hash(new_refresh_token)

        time_delta = get_settings().refresh_token_timedelta
        await self.session_service.refresh(current_session, new_refresh_token_hash, time_delta)

        return {"access_token": access_token, "refresh_token": new_refresh_token}

    async def load_current_user_session(self, access_token: str) -> tuple[User, Session]:
        try:
            payload = self.jwt_service.decode_access_token(access_token)
        except Exception as e:
            raise InvalidCredentialsError() from e

        try:
            user_id = UUID(payload["user_id"])
            session_id = UUID(payload["session_id"])
        except ValueError as e:
            raise InvalidCredentialsError() from e

        user = await self.user_service.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()
        if not user.can_login():
            raise InvalidCredentialsError("User is not active or does not have a login method.")

        session = await self.session_service.get_by_id(session_id)
        if session is None:
            raise SessionNotFoundError()
        if not session.is_valid():
            raise InvalidSessionError()

        if user_id != session.user_id:
            raise InvalidCredentialsError()

        return user, session

    async def logout(self, user: User, session: Session) -> None:
        await self.session_service.revoke(session.id)
