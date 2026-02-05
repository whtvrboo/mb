"""Tests for security headers."""

from fastapi.testclient import TestClient

from mitlist.main import app

client = TestClient(app)


def test_security_headers():
    """Verify that security headers are present in the response."""
    response = client.get("/health/live")
    assert response.status_code == 200

    headers = response.headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["X-XSS-Protection"] == "1; mode=block"
    assert headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
