
import time
from unittest.mock import AsyncMock, patch

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jose import jwt

from mitlist.core.auth.zitadel import ZitadelTokenError, verify_access_token

# Generate RSA key pair for testing
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
public_key = private_key.public_key()

# Serialize keys to PEM/JWK format
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
).decode("utf-8")

public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode("utf-8")

kid = "test-kid"

def create_token(claims: dict, kid: str = kid) -> str:
    return jwt.encode(claims, private_pem, algorithm="RS256", headers={"kid": kid})

@pytest.mark.asyncio
async def test_verify_access_token_valid_iat():
    """Test valid token with past iat."""
    now = time.time()
    claims = {
        "sub": "user123",
        "iat": now - 100,
        "exp": now + 3600,
        "aud": "mitlist-api",
        "iss": "https://zitadel.example.com",
    }
    token = create_token(claims)

    with patch(
        "mitlist.core.auth.zitadel._get_public_key_for_kid", new_callable=AsyncMock
    ) as mock_get_key:
        mock_get_key.return_value = public_pem

        # Should succeed
        verified = await verify_access_token(token)
        assert verified.claims["sub"] == "user123"

@pytest.mark.asyncio
async def test_verify_access_token_future_iat():
    """Test token with future iat (should fail)."""
    now = time.time()
    claims = {
        "sub": "user123",
        "iat": now + 3600, # 1 hour in future
        "exp": now + 7200,
        "aud": "mitlist-api",
        "iss": "https://zitadel.example.com",
    }
    token = create_token(claims)

    with patch(
        "mitlist.core.auth.zitadel._get_public_key_for_kid", new_callable=AsyncMock
    ) as mock_get_key:
        mock_get_key.return_value = public_pem

        # Should fail with ZitadelTokenError due to future iat
        with pytest.raises(ZitadelTokenError, match="Token issued in the future"):
            await verify_access_token(token)

@pytest.mark.asyncio
async def test_verify_access_token_missing_iat():
    """Test token without iat (should succeed if optional)."""
    now = time.time()
    claims = {
        "sub": "user123",
        # No iat
        "exp": now + 3600,
        "aud": "mitlist-api",
        "iss": "https://zitadel.example.com",
    }
    token = create_token(claims)

    with patch(
        "mitlist.core.auth.zitadel._get_public_key_for_kid", new_callable=AsyncMock
    ) as mock_get_key:
        mock_get_key.return_value = public_pem

        verified = await verify_access_token(token)
        assert verified.claims["sub"] == "user123"
