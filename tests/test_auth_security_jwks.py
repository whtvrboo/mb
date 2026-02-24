import time
from unittest.mock import AsyncMock, patch

import pytest

from mitlist.core.auth.zitadel import (
    ZitadelTokenError,
    _discovery_cache,
    _get_public_key_for_kid,
    _jwks_cache,
)


@pytest.mark.asyncio
async def test_jwks_dos_protection():
    """
    SECURITY TEST: Verify that the application is protected against JWKS cache busting.

    Vulnerability: An attacker could send tokens with random 'kid' headers, forcing the server
    to constantly refresh JWKS from the provider, leading to DoS.

    Fix: We implemented a cooldown (rate limit) on JWKS refreshes.
    """
    # Reset caches
    _jwks_cache["value"] = {"keys": []}
    _jwks_cache["expires_at"] = time.time() + 3600
    _jwks_cache["last_refreshed"] = 0.0  # Ensure we start fresh

    _discovery_cache["value"] = {"jwks_uri": "http://mock/jwks"}
    _discovery_cache["expires_at"] = time.time() + 3600

    # Mock _fetch_json to simulate network request
    with patch("mitlist.core.auth.zitadel._fetch_json", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = {"keys": []}

        # Scenario: Attacker sends 5 requests with different KIDs
        # The first request should trigger a fetch (refresh) because key is missing.
        # Subsequent requests should be rate-limited and NOT trigger a fetch.

        for i in range(5):
            try:
                await _get_public_key_for_kid(f"fake-kid-{i}")
            except ZitadelTokenError:
                pass

        print(f"Network calls: {mock_fetch.call_count}")

        # We expect exactly 1 network call (the initial refresh)
        assert mock_fetch.call_count == 1, "DoS Protection Failed: Excessive JWKS fetches detected!"


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main(["-v", __file__]))
