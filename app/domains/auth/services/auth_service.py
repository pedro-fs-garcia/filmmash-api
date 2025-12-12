from typing import Any

from app.core.security import JWTService, PasswordSecurity

from ..schemas import CreateUserDTO, CreateUserRequest, UserLoginRequest
from .user_service import UserService


class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service
        self.passwordSecurity = PasswordSecurity()
        self.jwtService = JWTService()

    async def register(self, dto: CreateUserRequest) -> dict[str, Any]:
        password_hash = self.passwordSecurity.generate_password_hash(dto.password)
        create_user_dto = CreateUserDTO(
            email=dto.email, password_hash=password_hash, username=dto.username
        )
        new_user = await self.user_service.create(create_user_dto)
        access_token = self.jwtService.create_access_token(new_user.id, [])
        refresh_token = self.jwtService.create_refresh_token(new_user.id, [])

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
            raise Exception("User not found")

        password_hash = user.password_hash
        if password_hash is None:
            raise Exception("Password not configured for user")

        is_authenticated = self.passwordSecurity.verify_password(dto.password, password_hash)

        if not is_authenticated:
            raise Exception("Invalid password")

        access_token = self.jwtService.create_access_token(user.id, [])
        refresh_token = self.jwtService.create_refresh_token(user.id, [])

        return (access_token, refresh_token)
