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

## 2025-02-17 - [Account Takeover via Sub Mismatch]
**Vulnerability:** A logic flaw in `mitlist/api/deps.py` allowed an attacker with the same email address but a different OIDC subject (`sub`) to bypass authentication checks and potentially take over an existing user account. The system attempted to update the linked `zitadel_sub` without verification.
**Learning:** Relying solely on email for user lookup when the IDP subject changes is insecure. Email reuse or account recreation on the IDP side should not automatically grant access. Additionally, SQLAlchemy JSON field updates may fail silently if modified in-place without reassignment, masking intended behavior.
**Prevention:** Enforce strict subject matching: if a user is already linked to a `sub`, incoming tokens MUST match that `sub`. Raise `UnauthorizedError` on mismatch. Use "Trust On First Use" (TOFU) only for the initial linking.
