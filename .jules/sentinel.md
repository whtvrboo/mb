## 2024-05-23 - [Insecure Password Storage Placeholder]
**Vulnerability:** Found `mitlist/modules/documents/service.py` using Base64 encoding for "encrypting" shared credential passwords, with a comment "replace with Fernet/vault in production".
**Learning:** Placeholder security code is a major risk. Developers might assume encryption is in place because of the function names `_encrypt_password`.
**Prevention:** Never commit insecure placeholder crypto. If a dependency is missing, fail loud or use a dummy implementation that raises NotImplementedError, rather than a vulnerable one. Always verify "encryption" functions actually encrypt.

## 2024-05-24 - [Invite Limit Race Condition]
**Vulnerability:** The `accept_invite` function checked `use_count < max_uses` before incrementing it, without a database lock (Time-of-Check to Time-of-Use).
**Learning:** Checking business limits in application code without database locking is unsafe under concurrency.
**Prevention:** Use `SELECT ... FOR UPDATE` (or `with_for_update()` in SQLAlchemy) when reading a value that determines whether a subsequent write is allowed.

## 2026-02-02 - [Unbounded List Input (DoS Risk)]
**Vulnerability:** The finance module schemas (`ExpenseCreate`, `SplitPresetCreate`) accepted lists (`splits`, `members`) without a `max_length` constraint. This allowed attackers to send massive payloads (e.g., 100k+ items), potentially causing memory exhaustion or DB bottlenecks.
**Learning:** Pydantic's `list[T]` does not imply any size limit. It defaults to unbounded, which is dangerous for public APIs.
**Prevention:** Always define `max_length` for `list` fields in Pydantic models that accept user input. Use `Field(..., max_length=N)`.

## 2026-05-25 - [JWKS Refresh DoS]
**Vulnerability:** The `_get_public_key_for_kid` function in `mitlist/core/auth/zitadel.py` unconditionally forced a JWKS refresh from the identity provider when a `kid` was not found in the cache. An attacker could flood the service with requests containing random `kid` headers, causing a Denial of Service by exhausting network connections or hitting rate limits on the IDP.
**Learning:** Caching strategies that refresh on "miss" must be protected against "cache miss storms" or intentional cache busting. Blindly refreshing on every unknown key assumes good faith clients.
**Prevention:** Implement a rate limit or cooldown period (e.g., 10 seconds) for cache refresh operations triggered by user input. Return an error immediately if a refresh was performed recently.
