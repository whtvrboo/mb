
import time
from unittest.mock import AsyncMock, patch

import pytest

from mitlist.core.auth.zitadel import ZitadelTokenError, _get_public_key_for_kid, _jwks_cache


@pytest.mark.asyncio
async def test_jwks_refresh_flood():
    # Setup cache to look valid initially
    # Use patch.dict to avoid polluting global state for other tests
    with patch.dict(_jwks_cache, {"value": {"keys": []}, "expires_at": time.time() + 3600, "last_refreshed": 0.0}):
        # We patch _fetch_json so we can count actual network requests
        # get_jwks calls get_discovery too, so let's mock get_discovery to avoid those calls counting
        with patch("mitlist.core.auth.zitadel._fetch_json", new_callable=AsyncMock) as mock_fetch, \
             patch("mitlist.core.auth.zitadel.get_discovery", new_callable=AsyncMock) as mock_discovery:

            mock_fetch.return_value = {"keys": []}
            mock_discovery.return_value = {"jwks_uri": "http://example.com/jwks"}

            # First call with unknown kid
            try:
                await _get_public_key_for_kid("unknown_kid_1")
            except ZitadelTokenError:
                pass

            # Expect 1 fetch because it forces a refresh when kid is not found in cache
            assert mock_fetch.call_count == 1

            # Reset mock
            mock_fetch.reset_mock()

            # Second call immediately with different unknown kid
            try:
                await _get_public_key_for_kid("unknown_kid_2")
            except ZitadelTokenError:
                pass

            # WITH FIX: This should NOT trigger refresh, so call_count is 0 (since we reset mock)
            assert mock_fetch.call_count == 0
