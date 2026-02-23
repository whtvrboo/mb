import time
from unittest.mock import AsyncMock, patch

import pytest

from mitlist.core.auth.zitadel import ZitadelTokenError, _get_public_key_for_kid, _jwks_cache


@pytest.mark.asyncio
async def test_jwks_dos_protection():
    """Test that we don't refresh JWKS too often when receiving invalid KIDs."""

    # Reset cache for test
    _jwks_cache["value"] = {"keys": []}
    # Initially valid cache so get_jwks doesn't fetch on first try
    _jwks_cache["expires_at"] = time.time() + 3600

    # We patch _fetch_json to count network calls
    with patch("mitlist.core.auth.zitadel.get_discovery", new_callable=AsyncMock) as mock_discovery:
        mock_discovery.return_value = {"jwks_uri": "http://test/jwks"}

        with patch("mitlist.core.auth.zitadel._fetch_json", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = {"keys": []}

            # --- First call with bad KID ---
            try:
                await _get_public_key_for_kid("bad-kid-1")
            except ZitadelTokenError:
                pass

            # Why 1 call?
            # 1. First get_jwks uses cached value (no fetch).
            # 2. Key not found.
            # 3. Cache invalidated (expires_at=0).
            # 4. Second get_jwks calls _fetch_json (1 fetch).
            assert mock_fetch.call_count == 1, f"Expected 1 fetch, got {mock_fetch.call_count}"

            # --- Second call with DIFFERENT bad KID immediately after ---
            try:
                await _get_public_key_for_kid("bad-kid-2")
            except ZitadelTokenError:
                pass

            # Without fix:
            # 1. First get_jwks uses cached value from previous fetch (no fetch).
            # 2. Key not found.
            # 3. Cache invalidated.
            # 4. Second get_jwks calls _fetch_json (1 fetch).
            # Total = 2 fetches.

            # With fix:
            # Should detect recent refresh and NOT invalidate cache.
            # Total should remain 1.

            assert mock_fetch.call_count == 1, (
                f"Expected 1 fetch (cached), got {mock_fetch.call_count}"
            )
