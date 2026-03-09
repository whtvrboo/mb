## 2024-05-23 - Polymorphic Relationship Indexing
**Learning:** The `Comment` model uses a polymorphic relationship (`parent_type`, `parent_id`) but only had an index on `parent_id`. This causes inefficient index scans when `parent_id` values collide across different types (common with autoincrement integer IDs).
**Action:** Always check polymorphic associations for composite indexes `(type, id)` or `(type, id, sort_col)`.

## 2024-05-23 - Notification Sorting Optimization
**Learning:** `list_notifications` queries by `user_id` and sorts by `created_at DESC`. The single index on `user_id` forces the database to sort results in memory after fetching.
**Action:** Add composite indexes `(filter_col, sort_col)` for frequently accessed sorted lists like feeds and activity logs.

## 2024-05-24 - Redundant Indexing with Composite Indexes
**Learning:** When adding a composite index `(col_a, col_b)` to optimize `WHERE col_a = ? ORDER BY col_b`, the existing index on `col_a` becomes redundant as the composite index can serve queries on `col_a` alone.
**Action:** Remove `index=True` from the leading column of a new composite index to save storage and write overhead.

## 2024-05-25 - Avoid N+1 Queries in Decrementing/Incrementing Database Rows
**Learning:** Performing arithmetic updates (like `vote_count = max(0, vote_count - weight)`) on numerous records by iterating, selecting the current record, updating in Python, and then flushing causes a classic N+1 database query problem and degrades performance rapidly.
**Action:** Use single bulk `update()` statements with SQL mathematical functions (like `func.greatest(0, col - weight)`) inside `db.execute()` to offload the calculations entirely to the database engine and prevent iterative trips across the network.
