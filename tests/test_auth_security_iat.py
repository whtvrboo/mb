
import time
import pytest
from unittest.mock import patch, AsyncMock
from jose import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from mitlist.core.auth.zitadel import verify_access_token, ZitadelTokenError

# Generate a key pair for testing
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
public_key = private_key.public_key()

# Serialize to PEM
pem_private = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)
pem_public = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

@pytest.mark.asyncio
async def test_verify_iat_enforcement():
    """Test that tokens with future iat (Issued At) are rejected."""

    # 1. Create a token issued 1 hour in the future
    # We use a large future time to be sure
    future_time = int(time.time()) + 3600
    payload = {
        "sub": "test-user",
        "iat": future_time,
        "exp": future_time + 7200,
        "aud": "mitlist-api",
        "iss": "https://zitadel.example.com"
    }

    # Sign with our private key
    token = jwt.encode(
        payload,
        pem_private.decode(),
        algorithm="RS256",
        headers={"kid": "test-key"}
    )

    # 2. Patch the public key retrieval to return our test key
    with patch("mitlist.core.auth.zitadel._get_public_key_for_kid", new_callable=AsyncMock) as mock_get_key:
        mock_get_key.return_value = pem_public.decode()

        # 3. Verify - THIS SHOULD FAIL if iat verification is enabled
        # Currently verify_iat=False, so this will pass.
        # We assert that it raises ZitadelTokenError.

        with pytest.raises(ZitadelTokenError, match="Token issued in the future"):
             await verify_access_token(token)
