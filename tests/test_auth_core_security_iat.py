import pytest
import time
from unittest.mock import AsyncMock, patch
from jose import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from mitlist.core.auth.zitadel import verify_access_token, ZitadelTokenError

# Generate RSA Key Pair for testing
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
public_key = private_key.public_key()

# Convert keys to PEM format
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
)
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode('utf-8')

@pytest.mark.asyncio
async def test_verify_access_token_rejects_future_iat():
    """Test that a token issued in the future (iat > now + skew) is rejected."""

    # Future timestamp (1 hour ahead)
    future_time = int(time.time()) + 3600

    claims = {
        "sub": "test-user",
        "iss": "https://zitadel.example.com",
        "aud": "mitlist-api",
        "exp": future_time + 3600,  # Expires in 2 hours
        "iat": future_time,         # Issued in 1 hour (FUTURE)
        "nbf": int(time.time()) - 60 # Valid nbf
    }

    token = jwt.encode(claims, private_pem, algorithm="RS256", headers={"kid": "test-key-id"})

    # Mock dependencies
    with patch("mitlist.core.auth.zitadel._get_public_key_for_kid", new_callable=AsyncMock) as mock_get_key, \
         patch("mitlist.core.config.settings.ZITADEL_AUDIENCE", "mitlist-api"), \
         patch("mitlist.core.config.settings.ZITADEL_ISSUER", "https://zitadel.example.com"):

        mock_get_key.return_value = public_pem

        try:
            await verify_access_token(token)
            # If we reach here, the token was accepted (BAD - Vulnerability exists)
            pytest.fail("Security vulnerability: Future iat token was accepted")
        except ZitadelTokenError as e:
            # If we catch the error, verify it's related to iat
            # This path is expected ONLY after the fix
            if "future" not in str(e) and "iat" not in str(e):
                raise e # Re-raise if it's some other error
            pass
