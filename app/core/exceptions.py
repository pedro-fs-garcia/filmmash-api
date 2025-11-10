from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .logger import get_logger


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        get_logger().warning(f"HTTP error: {exc.detail}", extra={"path": str(request.url)})

        error_response: dict[str, dict[str, Any]] = {
            "error": {
                "type": "HTTPException",
                "status_code": exc.status_code,
                "message": exc.detail or "HTTP error occurred.",
                "path": request.url.path,
                "method": request.method,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        }

        return JSONResponse(status_code=exc.status_code, content=error_response)

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        get_logger().error(f"Unhandled exception: {exc}", extra={"path": str(request.url)})

        error_response = {
            "error": {
                "type": exc.__class__.__name__,
                "message": "An unexpected error occurred when processing your request.",
                "path": request.url.path,
                "method": request.method,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        }

        return JSONResponse(status_code=500, content=error_response)
