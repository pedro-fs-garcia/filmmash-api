from uuid import UUID

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.dependencies import ResponseFactoryDep
from app.core.exceptions import AppHTTPException
from app.db.exceptions import ResourceAlreadyExistsError, ResourceNotFoundError
from app.domains.auth.dependencies import UserServiceDep
from app.domains.auth.schemas import AddUserRolesDTO, CreateUserDTO, ReplaceUserDTO, UpdateUserDTO
from app.schemas.response import SuccessContent

from ..entities import User

user_router = APIRouter()


@user_router.post("/", tags=["Users"], response_model=SuccessContent[User])
async def create_user(
    dto: CreateUserDTO, service: UserServiceDep, response: ResponseFactoryDep
) -> JSONResponse:
    try:
        user = await service.create(dto)
        return response.success(data=user.__dict__, status_code=status.HTTP_201_CREATED)
    except ResourceAlreadyExistsError as e:
        raise AppHTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email {dto.email} already exists.",
        ) from e


@user_router.get("/", tags=["Users"], response_model=SuccessContent[list[User]])
async def get_users(service: UserServiceDep, response: ResponseFactoryDep) -> JSONResponse:
    users = await service.get_all()
    return response.success(data=[user.__dict__ for user in users], status_code=status.HTTP_200_OK)


@user_router.get("/{id}", tags=["Users"])
async def get_user(id: UUID, service: UserServiceDep, response: ResponseFactoryDep) -> JSONResponse:
    user = await service.get_by_id(id)
    if not user:
        raise AppHTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id '{id}' was not found."
        )
    return response.success(data=user.__dict__, status_code=status.HTTP_200_OK)


@user_router.put("/{id}", tags=["Users"])
async def replace_role(
    id: UUID, dto: ReplaceUserDTO, service: UserServiceDep, response: ResponseFactoryDep
) -> JSONResponse:
    user = await service.update(id, dto)
    if user is None:
        raise AppHTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Role with id '{id}' was not found."
        )
    return response.success(
        data=user.__dict__,
        status_code=status.HTTP_200_OK,
    )


@user_router.patch("/{id}", tags=["Users"])
async def update_role(
    id: UUID, dto: UpdateUserDTO, service: UserServiceDep, response: ResponseFactoryDep
) -> JSONResponse:
    user = await service.update(id, dto)
    if user is None:
        raise AppHTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Role with id '{id}' was not found."
        )
    return response.success(
        data=user.__dict__,
        status_code=status.HTTP_200_OK,
    )


@user_router.post("/{id}/roles", tags=["users", "Roles"])
async def add_user_roles(
    id: UUID, dto: AddUserRolesDTO, service: UserServiceDep, response: ResponseFactoryDep
) -> JSONResponse:
    if not dto.role_ids:
        raise AppHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No role ids were informed"
        )
    try:
        user = await service.add_roles(id, dto.role_ids)
        return response.success(data=user.__dict__, status_code=status.HTTP_200_OK)
    except ResourceNotFoundError as e:
        raise AppHTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id '{id}' was not found."
        ) from e
    except ValueError as e:
        raise AppHTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
