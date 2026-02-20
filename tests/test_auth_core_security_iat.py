import time
import pytest
from unittest.mock import patch, AsyncMock
from jose import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from mitlist.core.auth.zitadel import verify_access_token, ZitadelTokenError

@pytest.mark.asyncio
async def test_future_iat_vulnerability():
    """
    Test that a token with an 'iat' (Issued At) claim in the future is rejected.
    Security: Prevents tokens from being used before they are issued (clock skew/manipulation).
    """
    # 1. Generate RSA key pair
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()

    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")

    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ).decode("utf-8")

    # 2. Create a token with iat in the future
    now = time.time()
    future_iat = int(now + 3600)  # 1 hour in future

    claims = {
        "sub": "user123",
        "iat": future_iat,
        "exp": future_iat + 3600,
        "nbf": int(now), # Valid nbf
        "iss": "https://zitadel.example.com",
        "aud": "my-app"
    }

    token = jwt.encode(claims, pem_private, algorithm="RS256", headers={"kid": "test-key-1"})

    # 3. Mock dependencies
    with patch("mitlist.core.auth.zitadel.settings") as mock_settings:
        mock_settings.ZITADEL_AUDIENCE = "my-app"
        mock_settings.zitadel_issuer = "https://zitadel.example.com"
        mock_settings.ZITADEL_CLOCK_SKEW_SECONDS = 0

        with patch("mitlist.core.auth.zitadel._get_public_key_for_kid", new_callable=AsyncMock) as mock_get_key:
            mock_get_key.return_value = pem_public

            # Verify that the token is rejected because 'iat' is in the future
            with pytest.raises(ZitadelTokenError, match="Token issued in the future"):
                await verify_access_token(token)
