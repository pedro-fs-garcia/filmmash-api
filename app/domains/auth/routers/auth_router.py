from typing import Any

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.dependencies import ResponseFactoryDep
from app.core.exceptions import AppHTTPException
from app.schemas.response import GenericSuccessContent

from ..dependencies import AuthServiceDep
from ..exceptions import InvalidPasswordError, UserNotFoundError, UserPasswordNotConfiguredError
from ..schemas import LoginResponse, UserCreatedResponse, UserLoginRequest

auth_router = APIRouter()


register_responses: dict[int | str, dict[str, Any]] = {
    status.HTTP_201_CREATED: {
        "model": UserCreatedResponse,
        "description": "User created successfully.",
    }
}


login_responses: dict[str | int, dict[str, Any]] = {
    status.HTTP_200_OK: {"description": "Login successful"},
    status.HTTP_404_NOT_FOUND: {"description": "User not found"},
    status.HTTP_400_BAD_REQUEST: {"description": "Password not configured"},
    status.HTTP_401_UNAUTHORIZED: {"description": "Invalid password"},
}

login_response_model = GenericSuccessContent[LoginResponse]


@auth_router.post(
    "/login", tags=["Login"], response_model=login_response_model, responses=login_responses
)
async def login(
    dto: UserLoginRequest, service: AuthServiceDep, response: ResponseFactoryDep
) -> JSONResponse:
    try:
        access_token, refresh_token = await service.login(dto)
        return response.success(
            data={"access_token": access_token, "refresh_token": refresh_token},
            status_code=status.HTTP_200_OK,
        )
    except (UserNotFoundError, InvalidPasswordError) as e:
        raise AppHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        ) from e
    except UserPasswordNotConfiguredError as e:
        raise AppHTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


# @auth_router.post("/register", tags=["Register"], responses=register_responses)
# async def register(
#     dto: RegisterUserRequest, service: AuthServiceDep, response: ResponseFactoryDep
# ) -> JSONResponse: ...
