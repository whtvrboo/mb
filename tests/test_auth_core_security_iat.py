
import time
from unittest.mock import patch, AsyncMock
import pytest
from jose import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from mitlist.core.auth.zitadel import verify_access_token, ZitadelTokenError

# Generate RSA key pair for testing
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
).decode("utf-8")

public_key = private_key.public_key()
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode("utf-8")

@pytest.mark.asyncio
async def test_verify_access_token_future_iat():
    """Test that a token issued in the future is rejected."""
    now = int(time.time())
    future_iat = now + 3600  # 1 hour in future

    claims = {
        "sub": "user123",
        "iat": future_iat,
        "exp": future_iat + 3600,
        "aud": "mitlist-api",
        "iss": "https://zitadel.example.com"
    }

    token = jwt.encode(claims, private_pem, algorithm="RS256", headers={"kid": "test-key"})

    # Mock _get_public_key_for_kid to return our public key
    with patch("mitlist.core.auth.zitadel._get_public_key_for_kid", new_callable=AsyncMock) as mock_get_key:
        mock_get_key.return_value = public_pem

        # Also mock settings if needed, but defaults might work.
        # However, verify_access_token uses settings.ZITADEL_AUDIENCE etc.
        # We might need to mock settings or set env vars.
        # Assuming defaults are empty/permissive or we match them.

        with patch("mitlist.core.auth.zitadel.settings") as mock_settings:
            mock_settings.ZITADEL_AUDIENCE = "mitlist-api"
            mock_settings.zitadel_issuer = "https://zitadel.example.com"
            mock_settings.ZITADEL_CLOCK_SKEW_SECONDS = 0  # Strict check

            # This should raise ZitadelTokenError because iat is in future
            # CURRENTLY: It might PASS because verify_iat=False and no manual check
            try:
                await verify_access_token(token)
                # If we are here, it means the token was accepted (BAD for security)
                pytest.fail("Token with future iat was accepted! Vulnerability exists.")
            except ZitadelTokenError as e:
                # If we are here, it means it was rejected (GOOD)
                assert "Token issued in the future" in str(e) or "iat" in str(e)

@pytest.mark.asyncio
async def test_verify_access_token_valid_iat():
    """Test that a token with valid iat is accepted."""
    now = int(time.time())
    valid_iat = now - 10  # 10 seconds ago

    claims = {
        "sub": "user123",
        "iat": valid_iat,
        "exp": now + 3600,
        "aud": "mitlist-api",
        "iss": "https://zitadel.example.com"
    }

    token = jwt.encode(claims, private_pem, algorithm="RS256", headers={"kid": "test-key"})

    with patch("mitlist.core.auth.zitadel._get_public_key_for_kid", new_callable=AsyncMock) as mock_get_key:
        mock_get_key.return_value = public_pem

        with patch("mitlist.core.auth.zitadel.settings") as mock_settings:
            mock_settings.ZITADEL_AUDIENCE = "mitlist-api"
            mock_settings.zitadel_issuer = "https://zitadel.example.com"
            mock_settings.ZITADEL_CLOCK_SKEW_SECONDS = 10

            result = await verify_access_token(token)
            assert result.sub == "user123"
