from typing import Any

from fastapi import APIRouter, status

from ..schemas import UserCreatedResponse

auth_router = APIRouter()


register_responses: dict[int | str, dict[str, Any]] = {
    status.HTTP_201_CREATED: {
        "model": UserCreatedResponse,
        "description": "User created successfully.",
    }
}
