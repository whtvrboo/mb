## 2024-05-23 - Polymorphic Relationship Indexing
**Learning:** The `Comment` model uses a polymorphic relationship (`parent_type`, `parent_id`) but only had an index on `parent_id`. This causes inefficient index scans when `parent_id` values collide across different types (common with autoincrement integer IDs).
**Action:** Always check polymorphic associations for composite indexes `(type, id)` or `(type, id, sort_col)`.

## 2024-05-23 - Notification Sorting Optimization
**Learning:** `list_notifications` queries by `user_id` and sorts by `created_at DESC`. The single index on `user_id` forces the database to sort results in memory after fetching.
**Action:** Add composite indexes `(filter_col, sort_col)` for frequently accessed sorted lists like feeds and activity logs.

## 2024-05-24 - Redundant Indexing with Composite Indexes
**Learning:** When adding a composite index `(col_a, col_b)` to optimize `WHERE col_a = ? ORDER BY col_b`, the existing index on `col_a` becomes redundant as the composite index can serve queries on `col_a` alone.
**Action:** Remove `index=True` from the leading column of a new composite index to save storage and write overhead.

## 2026-02-15 - Test Fixture ID Dependency
**Learning:** Backend tests failed with 403 Forbidden because the global `client` fixture hardcoded `X-Group-ID: 1`, while the `test_group` fixture generated IDs incrementing per test session/run. This mismatch prevented verifying performance optimizations correctly.
**Action:** Always verify test fixtures handle dynamic ID generation (e.g., passing `test_group.id` to headers) rather than hardcoding assumptions about database state.

## 2026-02-15 - Testing Environment Configuration
**Learning:** `pydantic-settings` validation occurs at import time (`mitlist.core.config`), requiring a `.env` file even for tests where values might be overridden later. Missing `.env` blocked test execution.
**Action:** Ensure a minimal `.env` exists in the test environment before running tests if the application uses strict configuration validation.
