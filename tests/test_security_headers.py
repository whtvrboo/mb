"""Tests for security headers middleware."""

import pytest
from httpx import ASGITransport, AsyncClient

from mitlist.core.config import settings
from mitlist.main import app


@pytest.mark.asyncio
async def test_security_headers_local():
    """Test security headers in local environment (no HSTS)."""
    settings.ENVIRONMENT = "local"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/docs")

        assert response.status_code == 200
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
        assert "default-src 'self'" in response.headers["Content-Security-Policy"]
        assert "Strict-Transport-Security" not in response.headers


@pytest.mark.asyncio
async def test_security_headers_production():
    """Test security headers in production environment (with HSTS)."""
    settings.ENVIRONMENT = "production"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # We don't care about the status code here since we just want to verify headers
        # Use a random endpoint so it skips doc-specific checks if any
        response = await client.get("/health")

        assert "Strict-Transport-Security" in response.headers
        assert (
            response.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"
        )

    # Reset back to local for other tests
    settings.ENVIRONMENT = "local"
