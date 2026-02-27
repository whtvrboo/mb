"""Tests for security headers middleware."""

import pytest
from httpx import ASGITransport, AsyncClient

from mitlist.main import app
from mitlist.core.config import settings


@pytest.mark.asyncio
async def test_security_headers_present():
    """Verify that security headers are present in responses."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/health/live")

        assert response.status_code == 200

        # Check for headers
        assert "Content-Security-Policy" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "Referrer-Policy" in response.headers

        # Verify values
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


@pytest.mark.asyncio
async def test_hsts_in_production(monkeypatch):
    """Verify HSTS header is present ONLY in production."""
    # Mock production environment
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/health/live")
        assert "Strict-Transport-Security" in response.headers
        assert response.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"

@pytest.mark.asyncio
async def test_no_hsts_in_development(monkeypatch):
    """Verify HSTS header is ABSENT in development."""
    # Mock development environment
    monkeypatch.setattr(settings, "ENVIRONMENT", "local")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/health/live")
        assert "Strict-Transport-Security" not in response.headers
