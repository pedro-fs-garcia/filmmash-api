from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas import ErrorResponse

from .logger import get_logger


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        get_logger().warning(f"HTTP error: {exc.detail}", extra={"path": str(request.url)})

        error_response = ErrorResponse(
            type=f"https://httpstatuses.io/{exc.status_code}",
            title=exc.detail or "HTTP Error",
            status=exc.status_code,
            detail=exc.detail or "HTTP error occurred.",
            instance=str(request.url.path),
        ).model_dump(exclude_none=True)

        return JSONResponse(status_code=exc.status_code, content=error_response)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        get_logger().warning(f"Validation error: {exc.errors()}", extra={"path": str(request.url)})

        payload = ErrorResponse(
            type="https://httpstatuses.io/422",
            title="Validation Error",
            status=422,
            detail="Request validation failed.",
            instance=request.url.path,
            errors=exc.errors(),
        ).model_dump(exclude_none=True)

        return JSONResponse(status_code=422, content=payload)

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        get_logger().error(f"Unhandled exception: {exc}", extra={"path": str(request.url)})

        error_response = ErrorResponse(
            type=exc.__class__.__name__,
            title="Internal Server Error",
            status=500,
            detail="An unexpected error occurred when processing your request.",
            instance=str(request.url.path),
        )

        return JSONResponse(status_code=500, content=error_response)
