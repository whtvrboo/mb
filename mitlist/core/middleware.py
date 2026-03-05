"""Security middleware."""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from mitlist.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds standard security headers to every response."""

    async def dispatch(self, request: Request, call_next):
        """Process request and inject security headers into response."""
        response = await call_next(request)

        # Prevent browsers from MIME-sniffing a response away from the declared content-type
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking by ensuring the content is not embedded in frames
        response.headers["X-Frame-Options"] = "DENY"

        # Enable XSS filtering in browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Enforce HTTPS and prevent downgrade attacks
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Control how much referrer information is included with requests
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Basic CSP: allow self, restrict framing, allow inline scripts/styles for Swagger UI
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "frame-ancestors 'none';"
        )

        return response
