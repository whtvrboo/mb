# Mitlist

Modular monolith FastAPI application for household management.

## Architecture

This application follows a **modular monolith** pattern with strict module boundaries:

- **Modules** (`mitlist/modules/`) are self-contained domains (e.g., `lists`, `finance`, `chores`)
- **Public Interface Rule**: Other modules may ONLY import from `modules/<name>/interface.py` and schemas, never directly from models or service layers
- **Cross-module communication**: Use service composition (synchronous) or domain events (asynchronous)

## Project Structure

```
mitlist/
├── core/              # Core application components
│   ├── config.py      # Settings (pydantic-settings)
│   ├── errors.py      # RFC 7807 error handling
│   ├── logging.py     # Structured logging
│   ├── otel.py        # OpenTelemetry setup
│   └── request_context.py  # Context vars (trace_id, user_id, group_id)
├── db/                # Database layer
│   ├── base.py        # SQLAlchemy base + mixins (VersionMixin)
│   └── engine.py      # Async engine + session factory
├── api/               # API layer
│   ├── deps.py        # FastAPI dependencies
│   ├── health.py      # Health check endpoints
│   └── router.py      # Main API router aggregator
├── modules/           # Domain modules
│   └── lists/         # Example module
│       ├── interface.py  # PUBLIC interface (import this!)
│       ├── models.py     # PRIVATE ORM models
│       ├── schemas.py    # Pydantic schemas
│       ├── service.py    # PRIVATE business logic
│       └── api.py        # FastAPI router
└── main.py            # App factory + entry point
```

## Quick Start (Windows PowerShell)

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Docker Desktop (for PostgreSQL)

### Setup

1. **Clone and navigate to project:**

   ```powershell
   cd C:\Users\Vinylnostalgia\Desktop\dev\mb
   ```

2. **Create virtual environment and install dependencies:**

   ```powershell
   uv venv
   uv sync
   ```

3. **Set up environment variables:**

   ```powershell
   Copy-Item .env.example .env
   # Edit .env if needed (defaults work for local dev)
   ```

4. **Start PostgreSQL:**

   ```powershell
   docker compose up -d
   ```

5. **Run database migrations:**

   ```powershell
   uv run alembic upgrade head
   ```

6. **Start the application:**

   ```powershell
   uv run uvicorn mitlist.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the API:**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health/live

## Development Workflow

### Running Tests

```powershell
uv run pytest
```

### Code Formatting & Linting

```powershell
# Format code
uv run ruff format .

# Lint code
uv run ruff check .
```

### Database Migrations

```powershell
# Create a new migration
uv run alembic revision --autogenerate -m "Description"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1
```

## API Contracts

### Success Responses

**No envelope** - resources are returned directly:

```json
GET /api/v1/lists/1
{
  "id": 1,
  "name": "Grocery List",
  "type": "SHOPPING",
  ...
}
```

### Error Responses (RFC 7807 Problem Details)

All errors return standardized JSON:

```json
{
  "type": "error:business-logic",
  "code": "STALE_WRITE",
  "detail": "Resource was modified by another request",
  "instance": "/api/v1/lists/1",
  "trace_id": "abc-123-def"
}
```

Error types:

- `error:validation` - Request validation failed (422)
- `error:not-found` - Resource not found (404)
- `error:conflict` - Conflict (409, e.g., stale write)
- `error:business-logic` - Business rule violation (400)

## Database Concurrency & Integrity

### Transaction Isolation

- **Default**: `READ COMMITTED`
- **Critical paths** (inventory, finance): Use `with_for_update()` for pessimistic locking

```python
# Example: Inventory decrement (critical path)
result = await db.execute(
    select(Item).where(Item.id == item_id).with_for_update()
)
item = result.scalar_one()
item.quantity_value -= quantity
```

### Optimistic Locking

Models can use `VersionMixin` for optimistic concurrency control:

```python
class List(BaseModel, VersionMixin):
    version_id: Mapped[int] = mapped_column(nullable=False, default=1)
    __mapper_args__ = {"version_id_col": version_id}
```

On stale write, SQLAlchemy raises `StaleDataError` → returns 409 Conflict.

### Query Performance

- **N+1 Prevention**: Use `selectinload()` for To-Many, `joinedload()` for To-One
- **No accessing relationships in loops** - always eager load

## Module Boundaries

### Creating a New Module

1. Create module directory: `mitlist/modules/<name>/`
2. Create `interface.py` with public functions/schemas
3. Create `models.py` (PRIVATE - don't import from other modules)
4. Create `schemas.py` (PUBLIC - can be imported)
5. Create `service.py` (PRIVATE - business logic)
6. Create `api.py` (FastAPI router)
7. Register router in `mitlist/api/router.py`

### Cross-Module Communication

**Pattern A (Synchronous/Critical):**

```python
# In a workflow service or api/deps.py
from mitlist.modules.finance.interface import create_expense
from mitlist.modules.lists.interface import create_list

async def create_user_workflow(db, user_data):
    # Transactions propagate - pass Session explicitly
    user = await create_user(db, user_data)
    await create_list(db, group_id=user.default_group_id, ...)
    await db.commit()
```

**Pattern B (Asynchronous/Decoupled):**

```python
# Use domain events (to be implemented)
events.emit("USER_CREATED", {"user_id": user.id})
# Background task listener handles side effects
```

**Forbidden:**

- ❌ Importing SQLAlchemy models from another module
- ❌ Circular dependencies (Finance imports Auth, Auth imports Finance)

## Observability

### Structured Logging

Every log entry includes:

- `trace_id` - Request correlation ID
- `user_id` - Current user (if authenticated)
- `group_id` - Current group context (if applicable)

**Development**: Console format
**Production**: JSON format

### Distributed Tracing

OpenTelemetry instrumentation is configured:

- FastAPI auto-instrumentation
- Logging correlation with trace IDs
- Trace propagation via `X-Request-ID` header

### Health Checks

- `/health/live` - Liveness probe (always 200 OK)
- `/health/ready` - Readiness probe (checks DB connectivity)

## Coding Standards

See the following documentation files:

- `01_DATABASE_INTEGRITY_AND_CONCURRENCY.md` - DB patterns
- `02_MODULAR_INTEROP_PATTERNS.md` - Module boundaries
- `03_API_CONTRACTS_AND_ERROR_TAXONOMY.md` - API standards
- `05_OBSERVABILITY_AND_OPERATIONS.md` - Logging & tracing
- `setup.md` - FastAPI setup patterns

## Environment Variables

See `.env.example` for required variables:

- `ENVIRONMENT` - Environment name (local, production)
- `PROJECT_NAME` - Application name
- `POSTGRES_SERVER` - Database host (use `db` for Docker Compose)
- `POSTGRES_USER` - Database user
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_DB` - Database name
- `SECRET_KEY` - Secret key for JWT/sessions
- `OTEL_EXPORTER_OTLP_ENDPOINT` - OpenTelemetry endpoint (optional)

## License

[Your License Here]
