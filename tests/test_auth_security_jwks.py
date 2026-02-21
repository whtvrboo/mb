import pytest
from unittest.mock import patch, AsyncMock, call
from jose import jwt
from mitlist.core.auth.zitadel import verify_access_token, ZitadelTokenError, _jwks_cache
from mitlist.core.config import settings
import time

@pytest.mark.asyncio
async def test_jwks_refresh_rate_limiting():
    """
    Security Test: Verify that JWKS refresh is rate-limited to prevent DoS.
    An attacker sending tokens with random 'kid's should not force a JWKS fetch on every request.
    """
    # Setup mock settings
    with patch("mitlist.core.config.settings.ZITADEL_BASE_URL", "https://auth.example.com"), \
         patch("mitlist.core.config.settings.ZITADEL_ISSUER", "https://auth.example.com"), \
         patch("mitlist.core.config.settings.ZITADEL_AUDIENCE", "audience"):

        # Create a token with a random kid that won't be found
        token = jwt.encode({"sub": "user123"}, "secret", algorithm="HS256", headers={"kid": "random-kid"})

        # Mock discovery and jwks responses
        mock_discovery = {"jwks_uri": "https://auth.example.com/jwks"}
        mock_jwks = {"keys": []}  # Empty keys

        async def mock_fetch_json(url):
            if "openid-configuration" in url:
                return mock_discovery
            elif "jwks" in url:
                return mock_jwks
            return {}

        with patch("mitlist.core.auth.zitadel._fetch_json", side_effect=mock_fetch_json) as mock_fetch:
            # Reset cache to initial state
            _jwks_cache["expires_at"] = 0.0
            _jwks_cache["value"] = None
            if "last_refreshed" in _jwks_cache:
                 _jwks_cache["last_refreshed"] = 0.0

            # 1. First call: Should fetch JWKS because cache is empty
            try:
                await verify_access_token(token)
            except ZitadelTokenError:
                pass

            # Verify fetch was called
            jwks_calls_1 = [c for c in mock_fetch.call_args_list if "jwks" in c[0][0]]
            assert len(jwks_calls_1) >= 1, "Should have fetched JWKS at least once"
            initial_fetch_count = len(jwks_calls_1)

            # 2. Subsequent calls immediately after: Should NOT fetch again due to rate limiting
            for _ in range(5):
                try:
                    await verify_access_token(token)
                except ZitadelTokenError:
                    pass

            jwks_calls_total = [c for c in mock_fetch.call_args_list if "jwks" in c[0][0]]

            # With fix: total calls should be same as initial (or maybe +1 if logic allows one retry per request but cache holds)
            # Actually, verify_access_token calls _get_public_key_for_kid.
            # If rate limited, it won't clear cache, so get_jwks won't fetch.

            # Assert that we didn't fetch significantly more.
            # Without fix, it would be +5 calls.
            # With fix, it should be +0 calls (because last_refreshed is recent).

            assert len(jwks_calls_total) == initial_fetch_count, \
                f"JWKS fetched {len(jwks_calls_total)} times, expected {initial_fetch_count} (rate limiting failed)"
