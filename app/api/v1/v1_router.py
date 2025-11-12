from typing import Any

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core import ResponseFactory, get_response_factory
from app.core.config import get_settings
from app.schemas.response import ErrorContent, GenericSuccessContent

api_v1_router = APIRouter()

inject_response_factory = Depends(get_response_factory)


class V1RootData(BaseModel):
    status: str
    environment: str


v1_responses: dict[int | str, dict[str, Any]] = {
    status.HTTP_200_OK: {
        "model": GenericSuccessContent[V1RootData],
        "description": "API v1 status.",
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "model": ErrorContent,
        "description": "Internal Server Error.",
    },
}


@api_v1_router.get("", tags=["v1"], responses=v1_responses)
async def root(response_factory: ResponseFactory = inject_response_factory) -> JSONResponse:
    return response_factory.success(
        data={"status": "API - version 1", "environment": get_settings().ENVIRONMENT},
        status_code=status.HTTP_200_OK,
    )
