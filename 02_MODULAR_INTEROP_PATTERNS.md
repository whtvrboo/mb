# 🧩 Modular Interoperability Standards

## 1. The Public Interface Rule

Modules (Auth, Finance, Chores) are treated as internal microservices.

- **Private Implementation:** `modules/finance/service.py` is PRIVATE.
- **Public Interface:** Create `modules/finance/interface.py`.
  - _Allowed:_ Other modules may ONLY import from `interface.py` or Pydantic schemas.
  - _Forbidden:_ Importing SQLAlchemy models from another module.

## 2. Cross-Module Transactions

- **The Problem:** "User Created" triggers "Create Default Lists".
- **Pattern A (Synchronous/Critical):**
  - Use **Service Composition** in a higher-level "Workflow" service or `api/deps.py`.
  - _Rule:_ Transactions must propagate. Pass the `Session` object explicitly.
- **Pattern B (Asynchronous/Decoupled):**
  - Use **Domain Events**.
  - _Publisher:_ `events.emit("USER_CREATED", payload)`
  - _Consumer:_ Background task listener.
  - _Consistency:_ Use **Outbox Pattern** if the side effect is critical (e.g., creating a ledger).

## 3. Circular Dependencies

- **Strict Ban:** If Finance imports Auth, Auth cannot import Finance.
- **Resolution:**
  1.  Extract shared logic to `app/core`.
  2.  Use Dependency Injection (pass the function/service as an arg).
  3.  Use Event-based coupling.
