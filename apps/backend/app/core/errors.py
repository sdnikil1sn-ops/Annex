"""Typed application errors and global exception handlers.

Every error response uses a stable envelope:
    {"error": {"code", "message", "request_id", "details"}}
so API clients can rely on the shape regardless of error origin.
"""

from typing import Any, cast

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.types import ExceptionHandler

from app.core.middleware import request_id_var

logger = structlog.get_logger(__name__)


class AppError(Exception):
    """Base class for all application-level errors."""

    status_code: int = 500
    code: str = "internal_error"
    message: str = "An unexpected error occurred."

    def __init__(self, message: str | None = None, details: Any = None) -> None:
        self.message = message or self.message
        self.details = details
        super().__init__(self.message)


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    status_code = 404
    code = "not_found"
    message = "The requested resource was not found."


class ValidationError(AppError):
    """Raised when business-level validation fails."""

    status_code = 422
    code = "validation_error"
    message = "The provided data failed validation."


class ConflictError(AppError):
    """Raised when an operation conflicts with existing state."""

    status_code = 409
    code = "conflict"
    message = "The operation conflicts with the current state."


class UnauthorizedError(AppError):
    """Raised when authentication is missing or invalid."""

    status_code = 401
    code = "unauthorized"
    message = "Authentication is required."


class ForbiddenError(AppError):
    """Raised when the caller lacks permission."""

    status_code = 403
    code = "forbidden"
    message = "You do not have permission to perform this action."


class RateLimitError(AppError):
    """Raised when a request exceeds the configured rate limit."""

    status_code = 429
    code = "rate_limited"
    message = "Too many requests. Please try again shortly."


def _error_body(
    status_code: int,
    code: str,
    message: str,
    details: Any = None,
) -> dict[str, Any]:
    """Build the canonical error envelope for an API response."""
    return {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id_var.get(),
            "details": details,
        }
    }


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Serialize a typed AppError into the canonical envelope."""
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.status_code, exc.code, exc.message, exc.details),
    )


async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Serialize Starlette/FastAPI HTTP exceptions into the envelope."""
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.status_code, "http_error", str(exc.detail)),
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Serialize request validation failures into a structured 422."""
    return JSONResponse(
        status_code=422,
        content=_error_body(
            422,
            "validation_error",
            "Request validation failed.",
            exc.errors(),
        ),
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Log unexpected exceptions and return a sanitized 500 response."""
    logger.exception(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
    )
    return JSONResponse(
        status_code=500,
        content=_error_body(
            500,
            "internal_error",
            "An unexpected error occurred. Please try again later.",
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all global exception handlers on the FastAPI application."""
    app.add_exception_handler(AppError, cast(ExceptionHandler, app_error_handler))
    app.add_exception_handler(
        StarletteHTTPException, cast(ExceptionHandler, http_error_handler)
    )
    app.add_exception_handler(
        RequestValidationError, cast(ExceptionHandler, validation_error_handler)
    )
    app.add_exception_handler(Exception, cast(ExceptionHandler, unhandled_error_handler))
