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
## 2025-02-18 - Account Takeover via IdP Subject Mismatch
**Vulnerability:** The application blindly updated the local user's linked IdP subject (`zitadel_sub`) to match the incoming token's `sub`, even if the user was already linked to a different subject. This allowed an attacker with access to the same email address (e.g., via account recreation or IdP compromise) to take over an existing account.
**Learning:** Trust On First Use (TOFU) must be implemented strictly as "First Use Only". Subsequent logins must verify the immutable link established during the first use. SQLAlchemy's JSON field update tracking requires explicit reassignment of a new dictionary object to persist changes reliable.
**Prevention:** Enforce an immutable link between local user identity and external IdP subject. Raise an explicit security exception (e.g., `UnauthorizedError`) on subject mismatch rather than updating the record.
