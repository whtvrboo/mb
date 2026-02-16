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

## 2026-02-03 - [Account Takeover via Weak Identity Linking]
**Vulnerability:** The `get_current_user` function automatically updated the `zitadel_sub` preference if it didn't match the token's subject, based solely on email matching. This allowed any valid token with the same email (from a different IDP subject) to hijack the account (Trust On First Use logic extended indefinitely).
**Learning:** Convenience features like "auto-update user identity" can undermine security guarantees. Trust On First Use (TOFU) must be strictly "First Use Only", not "Trust Every Time".
**Prevention:** When linking external identities, make the link immutable after creation. Explicitly reject mismatched identities for the same user account unless a secure re-linking flow (e.g., email verification) is performed.
