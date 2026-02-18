
import pytest
import time
from unittest.mock import AsyncMock, patch
from mitlist.core.auth.zitadel import verify_access_token, ZitadelTokenError
from mitlist.core.config import settings

@pytest.mark.asyncio
async def test_verify_access_token_future_iat():
    """Test that verify_access_token raises ZitadelTokenError if iat is in the future."""

    token = "test-token"
    future_iat = time.time() + 3600  # 1 hour in the future

    # Mock dependencies
    with patch("mitlist.core.auth.zitadel._get_public_key_for_kid", new_callable=AsyncMock) as mock_get_key, \
         patch("jose.jwt.get_unverified_header") as mock_header, \
         patch("jose.jwt.decode") as mock_decode:

        mock_get_key.return_value = "dummy-pem-key"
        mock_header.return_value = {"kid": "test-kid"}
        mock_decode.return_value = {"sub": "test-user", "iat": future_iat}

        # Expect verify_access_token to fail due to future iat
        with pytest.raises(ZitadelTokenError) as excinfo:
            await verify_access_token(token)

        assert "Token issued in the future" in str(excinfo.value)
