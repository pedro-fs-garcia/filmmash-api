from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.dependencies import ResponseFactoryDep
from app.core.exceptions import AppHTTPException
from app.db.exceptions import ResourceAlreadyExistsError

from ..dependencies import PermissionServiceDep
from ..schemas import (
    AddRolePermissionsDTO,
    CreatePermissionDTO,
    ReplacePermissionDTO,
    UpdatePermissionDTO,
)

permission_router = APIRouter()


permission_router.post("/", tags=["Permissions"])


async def create_permission(
    dto: CreatePermissionDTO, service: PermissionServiceDep, response: ResponseFactoryDep
) -> JSONResponse:
    try:
        permission = await service.create(dto)
        return response.success(data=permission.__dict__, status_code=status.HTTP_201_CREATED)
    except ResourceAlreadyExistsError as e:
        raise AppHTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Prmission with name '{dto.name}' already exists",
        ) from e


permission_router.get("/", tags=["Permissions"])


async def get_permissions(
    service: PermissionServiceDep, response: ResponseFactoryDep
) -> JSONResponse:
    permissions = await service.get_all()
    return response.success(data=[p.__dict__ for p in permissions], status_code=status.HTTP_200_OK)


permission_router.get("/{id}", tags=["Permissions"])


async def get_permission_by_id(
    id: int, service: PermissionServiceDep, response: ResponseFactoryDep
) -> JSONResponse:
    permission = await service.get_one(id)
    if not permission:
        raise AppHTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Permission with id '{id}' not found"
        )
    return response.success(data=permission.__dict__, status_code=status.HTTP_200_OK)


permission_router.put("/{id}", tags=["Permissions"])


async def replace_permission(
    id: int, dto: ReplacePermissionDTO, service: PermissionServiceDep, response: ResponseFactoryDep
) -> JSONResponse:
    permission = await service.update(id, dto)
    if permission is None:
        raise AppHTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Permission wit id '{id}' was not found."
        )
    return response.success(data=permission.__dict__, status_code=status.HTTP_200_OK)


permission_router.patch("/{id}", tags=["Permissions"])


async def update_role(
    id: int, dto: UpdatePermissionDTO, service: PermissionServiceDep, response: ResponseFactoryDep
) -> JSONResponse:
    permission = await service.update(id, dto)
    if permission is None:
        raise AppHTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Permission wit id '{id}' was not found."
        )
    return response.success(data=permission.__dict__, status_code=status.HTTP_200_OK)


permission_router.delete("/{id}", tags=["Permissions"])


async def delete_permission(
    id: int, service: PermissionServiceDep, response: ResponseFactoryDep
) -> JSONResponse:
    permission = await service.delete(id)
    if permission is None:
        raise AppHTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Role with id '{id}' was not found."
        )
    return response.success(
        data=permission.__dict__,
        status_code=status.HTTP_200_OK,
    )


permission_router.get("/{id}/roles", tags=["Permissions", "Roles"])


async def get_permission_roles(
    id: int, service: PermissionServiceDep, response: ResponseFactoryDep
) -> JSONResponse:
    permission = await service.get_with_roles(id)
    if permission is None:
        raise AppHTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Permission with id '{id}' not found"
        )
    return response.success(data=permission.__dict__, status_code=status.HTTP_200_OK)


permission_router.post("/{id}/roles", tags=["Permisisons", "Roles"])


async def add_permission_to_roles(
    id: int, dto: AddRolePermissionsDTO, service: PermissionServiceDep, response: ResponseFactoryDep
) -> JSONResponse:
    permission = await service.add_to_roles(id, dto.ids)
    return response.success(data=permission.__dict__, status_code=status.HTTP_200_OK)
