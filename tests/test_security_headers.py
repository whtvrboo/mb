"""Test security headers."""

import pytest
from httpx import ASGITransport, AsyncClient

from mitlist.main import app


@pytest.mark.asyncio
async def test_security_headers():
    """Verify that security headers are present in the response."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health/live")

    assert response.status_code == 200
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
