from typing import Annotated

from fastapi import Depends

from app.db.postgres.dependencies import PgSessionDep
from app.domains.auth.repositories.permission_repository import PermissionRepository
from app.domains.auth.repositories.user_repository import UserRepository
from app.domains.auth.services.permission_service import PermissionService
from app.domains.auth.services.user_service import UserService

from .repositories.role_repository import RoleRepository
from .services.role_service import RoleService


# ============================================================
# Repositories
# ============================================================
def get_role_repository(db: PgSessionDep) -> RoleRepository:
    return RoleRepository(db)


def get_permission_repository(db: PgSessionDep) -> PermissionRepository:
    return PermissionRepository(db)


def get_user_repository(db: PgSessionDep) -> UserRepository:
    return UserRepository(db)


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


# ============================================================
# Type Aliases for Router Use
# ============================================================
RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]
RoleRepoDep = Annotated[RoleRepository, Depends(get_role_repository)]

PermissionServiceDep = Annotated[PermissionService, Depends(get_permission_service)]
PermissionRepoDep = Annotated[PermissionRepository, Depends(get_permission_repository)]

UserServiceDep = Annotated[UserService, Depends(get_user_service)]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
