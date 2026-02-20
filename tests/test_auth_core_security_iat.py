"""Tests for JWT IAT (Issued At) validation."""

import time
from unittest.mock import AsyncMock, Mock, patch

import pytest
from jose import jwt

from mitlist.core.auth.zitadel import ZitadelTokenError, verify_access_token


@pytest.mark.asyncio
async def test_verify_access_token_future_iat():
    """Test that a token with a future IAT is rejected."""
    future_time = time.time() + 3600  # 1 hour in the future

    # Mock dependencies
    with patch("mitlist.core.auth.zitadel.jwt.get_unverified_header") as mock_header, \
         patch("mitlist.core.auth.zitadel._get_public_key_for_kid", new_callable=AsyncMock) as mock_get_key, \
         patch("mitlist.core.auth.zitadel.jwt.decode") as mock_decode, \
         patch("mitlist.core.auth.zitadel.settings") as mock_settings:

        mock_header.return_value = {"kid": "test-kid"}
        mock_get_key.return_value = "public-key-pem"
        mock_settings.ZITADEL_CLOCK_SKEW_SECONDS = 10
        mock_settings.ZITADEL_AUDIENCE = "aud"
        mock_settings.zitadel_issuer = "iss"

        # Mock decode to return a payload with future iat
        mock_decode.return_value = {
            "sub": "user123",
            "iat": future_time,
            "exp": future_time + 3600,
        }

        # Verify it raises ZitadelTokenError
        with pytest.raises(ZitadelTokenError) as exc:
            await verify_access_token("test-token")

        assert "Token issued in the future" in str(exc.value)


@pytest.mark.asyncio
async def test_verify_access_token_valid_iat():
    """Test that a token with a valid IAT is accepted."""
    past_time = time.time() - 3600  # 1 hour in the past

    # Mock dependencies
    with patch("mitlist.core.auth.zitadel.jwt.get_unverified_header") as mock_header, \
         patch("mitlist.core.auth.zitadel._get_public_key_for_kid", new_callable=AsyncMock) as mock_get_key, \
         patch("mitlist.core.auth.zitadel.jwt.decode") as mock_decode, \
         patch("mitlist.core.auth.zitadel.settings") as mock_settings:

        mock_header.return_value = {"kid": "test-kid"}
        mock_get_key.return_value = "public-key-pem"
        mock_settings.ZITADEL_CLOCK_SKEW_SECONDS = 10
        mock_settings.ZITADEL_AUDIENCE = "aud"
        mock_settings.zitadel_issuer = "iss"

        # Mock decode to return a payload with valid iat
        mock_decode.return_value = {
            "sub": "user123",
            "iat": past_time,
            "exp": past_time + 7200,
        }

        # Verify it succeeds
        verified = await verify_access_token("test-token")
        assert verified.claims["iat"] == past_time
