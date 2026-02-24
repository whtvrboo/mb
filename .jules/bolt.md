## 2024-05-23 - Polymorphic Relationship Indexing
**Learning:** The `Comment` model uses a polymorphic relationship (`parent_type`, `parent_id`) but only had an index on `parent_id`. This causes inefficient index scans when `parent_id` values collide across different types (common with autoincrement integer IDs).
**Action:** Always check polymorphic associations for composite indexes `(type, id)` or `(type, id, sort_col)`.

## 2024-05-23 - Notification Sorting Optimization
**Learning:** `list_notifications` queries by `user_id` and sorts by `created_at DESC`. The single index on `user_id` forces the database to sort results in memory after fetching.
**Action:** Add composite indexes `(filter_col, sort_col)` for frequently accessed sorted lists like feeds and activity logs.

## 2024-05-24 - Redundant Indexing with Composite Indexes
**Learning:** When adding a composite index `(col_a, col_b)` to optimize `WHERE col_a = ? ORDER BY col_b`, the existing index on `col_a` becomes redundant as the composite index can serve queries on `col_a` alone.
**Action:** Remove `index=True` from the leading column of a new composite index to save storage and write overhead.

## 2026-02-15 - Implicit Primary Key Sorting
**Learning:** SQLite secondary indexes implicitly include the primary key (ROWID) at the end, making `(group_id)` effectively `(group_id, id)`. This can mask sorting performance issues that only appear in production databases like PostgreSQL, which do not include the PK in secondary indexes by default.
**Action:** When optimizing `ORDER BY id` queries, always explicitly add the ID to the index `(filter_col, id)` even if local SQLite tests don't show a massive speedup, to ensure correctness and performance on Postgres.
