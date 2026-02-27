"""Security middleware for adding HTTP security headers."""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from mitlist.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware that adds security headers to all responses."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        # Content Security Policy (CSP)
        # Allow 'unsafe-inline' and 'unsafe-eval' for Swagger UI compatibility
        # In a strict production environment for a pure API, this should be tighter.
        csp = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;"
        response.headers["Content-Security-Policy"] = csp

        # X-Content-Type-Options
        # Prevents MIME-sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Referrer-Policy
        # Control referrer information sent to other sites
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Strict-Transport-Security (HSTS)
        # Enforce HTTPS in production
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
