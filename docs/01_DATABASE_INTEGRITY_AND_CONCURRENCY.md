# 🛡️ Database Integrity, Concurrency & Performance

## 1. Transaction Isolation & Locking Strategies

- **Default Isolation:** `READ COMMITTED`.
- **Critical Paths (Inventory/Finance):**
  - **Pessimistic Locking:** Use `with_for_update()` (SELECT FOR UPDATE) when calculating settlements or decrementing inventory.
    ```python
    # REQUIRED for inventory decrements
    item = db.query(Item).filter(Item.id == id).with_for_update().first()
    ```
  - **Optimistic Locking:** For standard CRUD (User settings, Lists), use a `version_id` column.
    - _Standard:_ SQLAlchemy `mapper_args: {"version_id_col": version_id}`.
    - _Failure:_ Catch `StaleDataError` and force client refresh.

## 2. Query Performance & Anti-Patterns

- **N+1 Prevention:**
  - **Strict Rule:** No accessing relationships in a loop.
  - **Solution:** Use `options(joinedload(Model.rel))` for To-One and `options(selectinload(Model.rel))` for To-Many.
  - **Enforcement:** Use `sqlalchemy-warn` in the test suite to fail tests that emit > N queries.
- **Index Selectivity:**
  - Do not index low-cardinality columns (e.g., `status` enum) unless part of a composite index.
  - **Composite Indexes:** Required for standard access patterns (e.g., `ix_expense_group_date` for Ledger views).

## 3. Migration Safety (Zero Downtime Principles)

- **Forbidden Operations:**
  - Renaming columns (requires dual-write strategy).
  - Adding `NOT NULL` columns without a default (locks table).
- **Data Migrations:**
  - Schema changes live in `alembic/versions`.
  - Data backfills/transformations live in `scripts/maintenance`. **Never** put massive data updates in a transactional migration file (causes production timeouts).

## 4. Constraint Enforcement

- **Logic in DB:** Check Constraints (`CK_expense_amount_positive`) and Unique Constraints (`UQ_user_email`) are mandatory. Application validation is a UI convenience, not a security layer.
