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

## 2026-02-02 - [Account Takeover via IDP Mismatch]
**Vulnerability:** The application allowed an existing user to be logged in with a token that had a matching email but a different `sub` (subject) identifier, updating the stored `sub` blindly. This allowed an attacker to hijack an account if they could claim the email on the IDP.
**Learning:** "Trust On First Use" (TOFU) must only apply to the *first* link. Once an identity is linked, the identifier must be immutable. Code that "fixes" metadata synchronization (like updating a changed `sub`) can inadvertently introduce account takeover vulnerabilities.
**Prevention:** Explicitly check if an external ID is already linked. If `existing_id` is present and `existing_id != new_id`, reject the login. Only update if `existing_id` is null.
