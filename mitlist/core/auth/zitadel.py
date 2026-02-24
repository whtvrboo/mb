"""Zitadel OIDC/JWT verification helpers.

Default strategy: validate access tokens locally using JWKS.
Critical strategy: validate locally + check revocation via introspection.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Optional

import httpx
from jose import jwk, jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError

from mitlist.core.config import settings


@dataclass(frozen=True)
class VerifiedToken:
    token: str
    claims: dict[str, Any]

    @property
    def sub(self) -> Optional[str]:
        return self.claims.get("sub")

    @property
    def email(self) -> Optional[str]:
        return self.claims.get("email")


class ZitadelTokenError(Exception):
    """Raised when a token cannot be verified or is invalid."""


_discovery_cache: dict[str, Any] = {"expires_at": 0.0, "value": None}
_jwks_cache: dict[str, Any] = {"expires_at": 0.0, "value": None, "last_refreshed": 0.0}


async def _fetch_json(url: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()


async def get_discovery() -> dict[str, Any]:
    """Fetch and cache the OIDC discovery document."""
    now = time.time()
    if _discovery_cache["value"] is not None and now < _discovery_cache["expires_at"]:
        return _discovery_cache["value"]

    url = settings.zitadel_discovery_url
    if not url:
        raise ZitadelTokenError("Zitadel discovery URL is not configured (ZITADEL_BASE_URL).")

    doc = await _fetch_json(url)
    _discovery_cache["value"] = doc
    _discovery_cache["expires_at"] = now + max(30, settings.ZITADEL_JWKS_CACHE_TTL_SECONDS)
    return doc


async def get_jwks() -> dict[str, Any]:
    """Fetch and cache the JWKS (public keys)."""
    now = time.time()
    if _jwks_cache["value"] is not None and now < _jwks_cache["expires_at"]:
        return _jwks_cache["value"]

    discovery = await get_discovery()
    jwks_uri = discovery.get("jwks_uri")
    if not jwks_uri:
        raise ZitadelTokenError("Discovery document missing jwks_uri.")

    jwks = await _fetch_json(jwks_uri)
    _jwks_cache["value"] = jwks
    _jwks_cache["expires_at"] = now + max(30, settings.ZITADEL_JWKS_CACHE_TTL_SECONDS)
    return jwks


def _jwk_to_public_pem(key_dict: dict[str, Any]) -> str:
    key_obj = jwk.construct(key_dict)
    pem = key_obj.to_pem()
    if isinstance(pem, bytes):
        return pem.decode("utf-8")
    return str(pem)


async def _get_public_key_for_kid(kid: str) -> str:
    jwks = await get_jwks()
    keys = jwks.get("keys", [])
    for k in keys:
        if k.get("kid") == kid:
            return _jwk_to_public_pem(k)

    # key rotation: refresh once
    last_refreshed = _jwks_cache.get("last_refreshed", 0.0)
    now = time.time()
    if now - last_refreshed < 10.0:
        raise ZitadelTokenError(f"Unknown signing key (kid={kid}).")

    _jwks_cache["expires_at"] = 0.0
    jwks = await get_jwks()
    _jwks_cache["last_refreshed"] = now

    keys = jwks.get("keys", [])
    for k in keys:
        if k.get("kid") == kid:
            return _jwk_to_public_pem(k)

    raise ZitadelTokenError(f"Unknown signing key (kid={kid}).")


async def verify_access_token(token: str) -> VerifiedToken:
    """Verify a Zitadel access token locally using JWKS."""
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            raise ZitadelTokenError("JWT header missing kid.")

        public_key = await _get_public_key_for_kid(kid)

        verify_aud = bool(settings.ZITADEL_AUDIENCE)
        verify_iss = bool(settings.zitadel_issuer)
        options = {
            "verify_signature": True,
            "verify_exp": True,
            "verify_nbf": True,
            "verify_iat": False,
            "verify_aud": verify_aud,
            "verify_iss": verify_iss,
            "require_exp": True,
            "leeway": settings.ZITADEL_CLOCK_SKEW_SECONDS,
        }

        claims = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=settings.ZITADEL_AUDIENCE if verify_aud else None,
            issuer=settings.zitadel_issuer if verify_iss else None,
            options=options,
        )
        return VerifiedToken(token=token, claims=claims)
    except (ExpiredSignatureError, JWTClaimsError, JWTError) as e:
        raise ZitadelTokenError(f"Invalid token: {e}") from e


async def introspect_token(token: str) -> dict[str, Any]:
    """Call Zitadel introspection endpoint and return response JSON."""
    url = settings.zitadel_introspection_url
    if not url:
        raise ZitadelTokenError("Zitadel introspection URL is not configured (ZITADEL_BASE_URL).")

    client_id = settings.ZITADEL_INTROSPECTION_CLIENT_ID
    client_secret = settings.ZITADEL_INTROSPECTION_CLIENT_SECRET
    if not (client_id and client_secret):
        raise ZitadelTokenError(
            "Introspection client credentials not configured "
            "(ZITADEL_INTROSPECTION_CLIENT_ID/SECRET)."
        )

    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        resp = await client.post(
            url,
            data={"token": token},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            auth=(client_id, client_secret),
        )
        resp.raise_for_status()
        return resp.json()


async def require_active_token(token: str) -> dict[str, Any]:
    """Introspect token and require active=true."""
    data = await introspect_token(token)
    if not data.get("active"):
        raise ZitadelTokenError("Token is not active (revoked or expired).")
    return data
