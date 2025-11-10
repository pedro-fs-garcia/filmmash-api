from fastapi import APIRouter

from app.core import get_settings

api_v1_router = APIRouter()


@api_v1_router.get("/", tags=["v1"])
async def root() -> dict[str, str]:
    return {"status": "API - version 1", "environment": get_settings().ENVIRONMENT}
