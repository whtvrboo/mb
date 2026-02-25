import pytest
import time
from unittest.mock import patch, AsyncMock, MagicMock
from mitlist.core.auth.zitadel import _get_public_key_for_kid, ZitadelTokenError, _jwks_cache, _discovery_cache

# Mock data
MOCK_DISCOVERY = {"jwks_uri": "https://example.com/jwks"}
MOCK_JWKS = {
    "keys": [
        {
            "kty": "RSA",
            "kid": "valid-kid",
            "n": "xxx",
            "e": "AQAB"
        }
    ]
}

@pytest.mark.asyncio
async def test_jwks_flooding_vulnerability():
    """
    Test that calling _get_public_key_for_kid with invalid KIDs triggers
    multiple JWKS fetches (vulnerability reproduction).
    """
    # Reset caches
    _jwks_cache["value"] = None
    _jwks_cache["expires_at"] = 0.0
    _discovery_cache["value"] = MOCK_DISCOVERY
    _discovery_cache["expires_at"] = time.time() + 3600

    # Mock settings and fetch_json
    with patch("mitlist.core.auth.zitadel.settings") as mock_settings, \
         patch("mitlist.core.auth.zitadel._fetch_json", new_callable=AsyncMock) as mock_fetch:

        mock_settings.zitadel_discovery_url = "https://example.com/.well-known/openid-configuration"
        mock_settings.ZITADEL_JWKS_CACHE_TTL_SECONDS = 3600

        # Setup mock fetch to return JWKS
        mock_fetch.return_value = MOCK_JWKS

        # 1. Call with invalid KID 1
        try:
            await _get_public_key_for_kid("invalid-kid-1")
        except ZitadelTokenError:
            pass

        # Should fetch JWKS only once because the cache was just refreshed
        # and the cooldown prevents the immediate second fetch.
        assert mock_fetch.call_count == 1
        initial_call_count = mock_fetch.call_count

        # 2. Call with invalid KID 2 immediately
        try:
            await _get_public_key_for_kid("invalid-kid-2")
        except ZitadelTokenError:
            pass

        # Secure behavior: Should NOT fetch JWKS again due to cooldown
        assert mock_fetch.call_count == initial_call_count
        print(f"Fetch called {mock_fetch.call_count} times (unchanged due to rate limiting)")
