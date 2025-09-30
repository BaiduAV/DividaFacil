from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.schemas.error import ErrorResponse


async def api_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions for API routes with JSON error responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTP Error", detail=exc.detail, status_code=exc.status_code
        ).dict(),
    )


async def api_validation_exception_handler(request: Request, exc: Exception):
    """Handle validation errors for API routes with JSON error responses."""
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(error="Validation Error", detail=str(exc), status_code=400).dict(),
    )
