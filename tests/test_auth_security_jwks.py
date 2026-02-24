import pytest
import time
from unittest.mock import patch, AsyncMock
from jose import jwt
from mitlist.core.auth.zitadel import verify_access_token, ZitadelTokenError, _jwks_cache

# Mock discovery and JWKS responses
DISCOVERY_RESPONSE = {"jwks_uri": "https://auth.example.com/keys"}
JWKS_RESPONSE = {"keys": []}  # Empty JWKS, so no key will ever be found


@pytest.mark.asyncio
async def test_jwks_dos_protection():
    """
    Test that sending multiple requests with unknown 'kid's does NOT trigger excessive JWKS fetches.
    This verifies the rate limiting on JWKS refreshes.
    """
    # Reset cache state
    _jwks_cache["value"] = None
    _jwks_cache["expires_at"] = 0.0
    _jwks_cache["last_refreshed"] = 0.0

    # Mock settings and _fetch_json
    with (
        patch("mitlist.core.config.settings.ZITADEL_BASE_URL", "https://auth.example.com"),
        patch("mitlist.core.config.settings.ZITADEL_JWKS_CACHE_TTL_SECONDS", 3600),
        patch("mitlist.core.auth.zitadel._fetch_json", new_callable=AsyncMock) as mock_fetch,
    ):
        # Setup mock behavior
        mock_fetch.side_effect = lambda url: (
            DISCOVERY_RESPONSE if "well-known" in url else JWKS_RESPONSE
        )

        # Generate 5 tokens with different unknown kids
        tokens = []
        for i in range(5):
            token = jwt.encode(
                {"sub": f"user{i}", "exp": time.time() + 3600},
                "secret",
                algorithm="HS256",
                headers={"kid": f"unknown_kid_{i}"},
            )
            tokens.append(token)

        # Attack: Send 5 requests
        for token in tokens:
            try:
                await verify_access_token(token)
            except ZitadelTokenError:
                pass  # Expected
            except Exception:
                pass

        # Expected calls:
        # 1. Discovery (first request)
        # 2. JWKS fetch (initial)
        # 3. JWKS fetch (refresh for kid_0)
        # 4. kid_1..4 fail immediately due to cooldown (no refresh)
        # Total = 3 calls

        call_count = mock_fetch.call_count

        # Assert that we are protected (max 3 calls)
        assert call_count <= 3, f"Too many JWKS refreshes! Protection failed. Calls: {call_count}"
