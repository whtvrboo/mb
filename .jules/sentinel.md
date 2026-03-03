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

## 2024-10-27 - [MEDIUM] Fix DoS vulnerability via unbounded list inputs
**Vulnerability:** Several Pydantic schemas handling list inputs (`RecipeCreate.ingredients`, `CalendarEventCreate.attendee_ids`, `ProposalCreate.ballot_options`, `CommentCreate.mentioned_user_ids`) did not define a maximum length (`max_length`). This created a Denial of Service (DoS) vulnerability where an attacker could submit an extremely large payload (e.g., thousands of items), exhausting server memory or database connection resources during validation and insertion.
**Learning:** Pydantic's `Field(default_factory=list)` allows arrays of infinite size by default. When building APIs that accept arrays of objects or IDs for bulk operations, these fields must be explicitly bounded to prevent resource exhaustion attacks.
**Prevention:** Always define a `max_length` parameter for `list` inputs in create/update Pydantic schemas (e.g., `Field(default_factory=list, max_length=100)`). Apply this specifically to request schemas to avoid unintentionally blocking valid large data responses from the server.
