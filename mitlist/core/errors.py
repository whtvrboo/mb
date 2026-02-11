"""Application error handling with RFC 7807 Problem Details."""


from fastapi import Request, status
from fastapi.responses import JSONResponse

from mitlist.core.request_context import get_trace_id


class AppError(Exception):
    """Base application error with RFC 7807 Problem Details structure."""

    def __init__(
        self,
        code: str,
        detail: str,
        status_code: int = 400,
        error_type: str = "error:business-logic",
    ):
        self.code = code
        self.detail = detail
        self.status_code = status_code
        self.error_type = error_type
        super().__init__(self.detail)


class NotFoundError(AppError):
    """Resource not found error."""

    def __init__(self, code: str = "NOT_FOUND", detail: str = "Resource not found"):
        super().__init__(
            code=code,
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND,
            error_type="error:not-found",
        )


class ConflictError(AppError):
    """Conflict error (e.g., stale write, duplicate)."""

    def __init__(self, code: str = "CONFLICT", detail: str = "Conflict occurred"):
        super().__init__(
            code=code,
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
            error_type="error:conflict",
        )


class StaleDataError(ConflictError):
    """Stale data error for optimistic locking failures."""

    def __init__(self, detail: str = "Resource was modified by another request"):
        super().__init__(code="STALE_WRITE", detail=detail)


class ValidationError(AppError):
    """Validation error."""

    def __init__(self, code: str = "VALIDATION_ERROR", detail: str = "Validation failed"):
        super().__init__(
            code=code,
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_type="error:validation",
        )


class UnauthorizedError(AppError):
    """Authentication/authorization failure (401)."""

    def __init__(
        self,
        code: str = "UNAUTHORIZED",
        detail: str = "Not authenticated",
    ):
        super().__init__(
            code=code,
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_type="error:unauthorized",
        )


class ForbiddenError(AppError):
    """Authenticated but not allowed (403)."""

    def __init__(
        self,
        code: str = "FORBIDDEN",
        detail: str = "You do not have permission to perform this action",
    ):
        super().__init__(
            code=code,
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
            error_type="error:forbidden",
        )


class GoneError(AppError):
    """Endpoint removed/deprecated (410)."""

    def __init__(
        self,
        code: str = "GONE",
        detail: str = "This endpoint is no longer available",
    ):
        super().__init__(
            code=code,
            detail=detail,
            status_code=status.HTTP_410_GONE,
            error_type="error:gone",
        )


class NotImplementedAppError(AppError):
    """Endpoint or feature not yet implemented (501)."""

    def __init__(
        self,
        code: str = "NOT_IMPLEMENTED",
        detail: str = "This endpoint is not yet implemented",
    ):
        super().__init__(
            code=code,
            detail=detail,
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            error_type="error:not-implemented",
        )


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Global exception handler for AppError returning RFC 7807 Problem Details."""
    trace_id = get_trace_id()
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": exc.error_type,
            "code": exc.code,
            "detail": exc.detail,
            "instance": str(request.url.path),
            "trace_id": trace_id,
        },
    )
