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

## 2025-02-17 - [DoS Risk via Unbounded Pydantic Lists]
**Vulnerability:** Found multiple Pydantic input schemas using `list[T]` (e.g., `attendee_ids: list[int] = Field(default_factory=list)`) without a `max_length` parameter constraint.
**Learning:** Pydantic's `list[T]` type natively does not enforce any size limit constraint. Without a `max_length` limit, the application is vulnerable to Denial of Service (DoS) attacks if an attacker submits an excessively large array payload, forcing the server to parse and instantiate massive lists in memory.
**Prevention:** Always define a maximum size limit using `Field(..., max_length=X)` for any array fields in input models (e.g., `Field(default_factory=list, max_length=100)`) to restrict the payload size and protect memory.
