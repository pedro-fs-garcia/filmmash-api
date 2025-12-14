from typing import Annotated

from fastapi import Depends

from app.core.dependencies import JWTServiceDep, PasswordSecurityDep
from app.db.postgres.dependencies import PgSessionDep

from .entities import Session, User
from .repositories.permission_repository import PermissionRepository
from .repositories.role_repository import RoleRepository
from .repositories.session_repository import SessionRepository
from .repositories.user_repository import UserRepository
from .services.auth_service import AuthService
from .services.permission_service import PermissionService
from .services.role_service import RoleService
from .services.session_service import SessionService
from .services.user_service import UserService


# ============================================================
# Repositories
# ============================================================
def get_role_repository(db: PgSessionDep) -> RoleRepository:
    return RoleRepository(db)


def get_permission_repository(db: PgSessionDep) -> PermissionRepository:
    return PermissionRepository(db)


def get_user_repository(db: PgSessionDep) -> UserRepository:
    return UserRepository(db)


def get_session_repository(db: PgSessionDep) -> SessionRepository:
    return SessionRepository(db)


# ============================================================
# Services
# ============================================================
def get_role_service(
    role_repo: Annotated[RoleRepository, Depends(get_role_repository)],
) -> RoleService:
    return RoleService(role_repo)


def get_permission_service(
    permission_repo: Annotated[PermissionRepository, Depends(get_permission_repository)],
) -> PermissionService:
    return PermissionService(permission_repo)


def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(user_repo)


def get_session_service(
    db: PgSessionDep,
    session_repo: Annotated[SessionRepository, Depends(get_session_repository)],
    jwt_service: JWTServiceDep,
) -> SessionService:
    return SessionService(db, session_repo, jwt_service)


def get_auth_service(
    user_service: Annotated[UserService, Depends(get_user_service)],
    session_service: Annotated[SessionService, Depends(get_session_service)],
    jwt_service: JWTServiceDep,
    password_security: PasswordSecurityDep,
) -> AuthService:
    return AuthService(
        user_service=user_service,
        session_service=session_service,
        jwt_service=jwt_service,
        password_security=password_security,
    )


async def get_current_user_session(
    service: Annotated[AuthService, Depends(get_auth_service)],
    access_token: str,
) -> tuple[User, Session]:
    return await service.load_current_user_session(access_token)


# ============================================================
# Type Aliases for Router Use
# ============================================================
RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]
RoleRepoDep = Annotated[RoleRepository, Depends(get_role_repository)]

PermissionServiceDep = Annotated[PermissionService, Depends(get_permission_service)]
PermissionRepoDep = Annotated[PermissionRepository, Depends(get_permission_repository)]

UserServiceDep = Annotated[UserService, Depends(get_user_service)]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]

SessionServiceDep = Annotated[SessionService, Depends(get_session_service)]
SessionRepoDep = Annotated[SessionRepository, Depends(get_session_repository)]

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

CurrentUserSessionDep = Annotated[tuple[User, Session], Depends(get_current_user_session)]
