import asyncio
import base64
import json
from unittest.mock import AsyncMock, patch

import pytest

from mitlist.core.auth.zitadel import ZitadelTokenError, _jwks_cache, verify_access_token

# Sample JWKS response
JWKS_DATA = {
    "keys": [
        {
            "kid": "good-kid",
            "kty": "RSA",
            "alg": "RS256",
            "use": "sig",
            "n": "somerandommodulus",
            "e": "AQAB",
        }
    ]
}

DISCOVERY_DATA = {"jwks_uri": "https://auth.example.com/keys"}


def make_token(kid: str) -> str:
    """Create a dummy JWT with a specific kid."""
    header = {"alg": "RS256", "kid": kid, "typ": "JWT"}
    h_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    # Payload and signature don't matter because we expect failure at kid lookup
    return f"{h_b64}.e30.sig"


@pytest.mark.asyncio
async def test_jwks_flooding_prevention():
    """Verify that multiple requests with unknown kids do not flood the JWKS endpoint."""

    # Reset global cache state
    _jwks_cache["value"] = None
    _jwks_cache["expires_at"] = 0.0
    if "last_refreshed" in _jwks_cache:
        _jwks_cache["last_refreshed"] = 0.0

    # Mock _fetch_json to control network responses
    with patch("mitlist.core.auth.zitadel._fetch_json", new_callable=AsyncMock) as mock_fetch:
        # First call is discovery, subsequent are JWKS
        # We allow infinite side effects returning JWKS_DATA
        mock_fetch.side_effect = [DISCOVERY_DATA] + [JWKS_DATA] * 100

        # Create a batch of concurrent requests with different unknown kids
        tasks = []
        for i in range(10):
            token = make_token(f"bad-kid-{i}")
            tasks.append(verify_access_token(token))

        # Run them concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Assert all failed with ZitadelTokenError
        for res in results:
            assert isinstance(res, ZitadelTokenError)
            assert "Unknown signing key" in str(res)

        # Assert network calls
        # Expected behavior with fix:
        # 1. Discovery (1 call)
        # 2. JWKS fetch (1 call) - triggered by the first request that wins the lock
        # Total: 2 calls.

        # Current behavior (without fix):
        # 1. Discovery (1 call, cached for subsequent)
        # 2. JWKS fetch (10 calls) - one for each request because they all see cache miss and force
        #    refresh
        # Total: 11 calls.

        # We assert strictly <= 3 to prove rate limiting works.
        # 1. Discovery fetch (initial)
        # 2. JWKS fetch (optimistic check sees empty/expired cache)
        # 3. JWKS fetch (forced refresh inside lock because key was missing)
        # subsequent requests are blocked by rate limit.
        # Without fix, this would be 10+ calls.
        assert mock_fetch.call_count <= 3, f"Expected <= 3 fetches, got {mock_fetch.call_count}"
