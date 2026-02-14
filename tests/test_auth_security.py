import time
from unittest.mock import AsyncMock, patch

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jose import jwt

from mitlist.core.auth.zitadel import ZitadelTokenError, verify_access_token

# Generate RSA key for testing
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# Convert public key to PEM format
pem_public_key = public_key.public_bytes(
    encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode("utf-8")

# Convert private key to PEM for signing (jose needs PEM or JWK)
pem_private_key = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
).decode("utf-8")


@pytest.mark.asyncio
async def test_token_issued_in_future_rejected():
    """Verify that a token with 'iat' in the future is rejected."""

    future_iat = int(time.time()) + 3600  # 1 hour in the future
    payload = {
        "sub": "test-user",
        "iss": "https://zitadel.example.com",
        "aud": "mitlist-api",
        "exp": future_iat + 3600,
        "iat": future_iat,
        "nbf": future_iat,  # usually nbf <= iat, but let's make sure nbf is also future
    }

    # We must ensure nbf is also checked, but verify_iat is independent.
    # If we set nbf to now, and iat to future, verify_iat should still catch it if enabled.
    # However, verify_nbf=True by default. If nbf is in future, it fails regardless of iat.
    # So to test verify_iat specifically, we should set nbf to now (or missing) and iat to future.

    payload["nbf"] = int(time.time()) - 10  # valid nbf

    token = jwt.encode(payload, pem_private_key, algorithm="RS256", headers={"kid": "test-key"})

    # Mock _get_public_key_for_kid to return our public key
    with patch(
        "mitlist.core.auth.zitadel._get_public_key_for_kid",
        new=AsyncMock(return_value=pem_public_key),
    ):
        # Also mock settings if needed, but defaults might be fine.
        # We need to make sure audience/issuer validation doesn't fail first if configured.
        # Let's patch settings to be lenient or match our payload.
        with patch("mitlist.core.auth.zitadel.settings") as mock_settings:
            mock_settings.ZitadelTokenError = ZitadelTokenError  # needed? No, imported
            mock_settings.ZITADEL_AUDIENCE = "mitlist-api"
            mock_settings.zitadel_issuer = "https://zitadel.example.com"
            mock_settings.ZITADEL_CLOCK_SKEW_SECONDS = 0  # strict

            # Expectation: Currently this should PASS (because verify_iat=False),
            # but we want it to FAIL.
            # So for reproduction, we assert it DOES NOT raise.
            # AFTER FIX, we assert it RAISES.

            # Since I am writing the test to be permanent, I will write it expecting the fix.
            with pytest.raises(ZitadelTokenError) as excinfo:
                await verify_access_token(token)

            assert "iat" in str(excinfo.value) or "Issued At" in str(excinfo.value)


@pytest.mark.asyncio
async def test_token_missing_iat_rejected():
    """Verify that a token missing 'iat' is rejected."""

    payload = {
        "sub": "test-user",
        "iss": "https://zitadel.example.com",
        "aud": "mitlist-api",
        "exp": int(time.time()) + 3600,
        # iat missing
    }

    token = jwt.encode(payload, pem_private_key, algorithm="RS256", headers={"kid": "test-key"})

    with patch(
        "mitlist.core.auth.zitadel._get_public_key_for_kid",
        new=AsyncMock(return_value=pem_public_key),
    ):
        with patch("mitlist.core.auth.zitadel.settings") as mock_settings:
            mock_settings.ZITADEL_AUDIENCE = "mitlist-api"
            mock_settings.zitadel_issuer = "https://zitadel.example.com"
            mock_settings.ZITADEL_CLOCK_SKEW_SECONDS = 0

            with pytest.raises(ZitadelTokenError) as excinfo:
                await verify_access_token(token)

            assert "iat" in str(excinfo.value) or "Issued At" in str(excinfo.value)
