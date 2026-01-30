# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Server
```powershell
# Start the application (with hot reload)
uv run uvicorn mitlist.main:app --reload --host 0.0.0.0 --port 8000

# Access points:
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs
# - Health: http://localhost:8000/health/live
```

### Database
```powershell
# Start PostgreSQL
docker compose up -d

# Create a new migration
uv run alembic revision --autogenerate -m "Description"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1
```

### Testing & Linting
```powershell
# Run tests
uv run pytest

# Format code
uv run ruff format .

# Lint code
uv run ruff check .
```

### Environment Setup
```powershell
# Create virtual environment
uv venv

# Install dependencies
uv sync
```

## Architecture

### Modular Monolith Pattern

This application follows a **strict modular monolith** architecture with enforced module boundaries:

- **Modules** (`mitlist/modules/`) are self-contained domains (auth, lists, finance, chores, etc.)
- **CRITICAL RULE**: Other modules may ONLY import from `modules/<name>/interface.py` and `schemas.py`
- **NEVER** import from another module's `models.py` or `service.py` directly
- Each module exposes a public interface file that re-exports approved functions and schemas

### Module Structure

Each module follows this pattern:
```
mitlist/modules/<name>/
├── interface.py    # PUBLIC - other modules import from here
├── schemas.py      # PUBLIC - Pydantic schemas
├── models.py       # PRIVATE - SQLAlchemy ORM models
├── service.py      # PRIVATE - business logic
└── api.py          # FastAPI router
```

### Cross-Module Communication

**Pattern A (Synchronous/Critical):**
- Use service composition via interface imports
- Transactions propagate - always pass the AsyncSession explicitly
- Example: workflow service imports from multiple `interface.py` files

**Pattern B (Asynchronous/Decoupled):**
- Use domain events (to be implemented)
- For eventual consistency scenarios

**Circular Dependencies:**
- Strictly forbidden between modules
- If needed, extract shared logic to `mitlist/core/`

### Available Modules

- **auth**: Users, groups, invites, Zitadel OIDC authentication
- **lists**: Lists, items, inventory management
- **finance**: Expenses, budgets, settlements, recurring expenses
- **chores**: Chore tracking, assignments, templates
- **governance**: Proposals, voting, delegations
- **assets**: Home assets, maintenance, insurance
- **documents**: Document storage and sharing
- **recipes**: Recipes, meal plans, shopping sync
- **calendar**: Events, attendees, reminders
- **notifications**: Notifications, comments, mentions, reactions
- **gamification**: Points, achievements, streaks, leaderboards
- **pets**: Pet management, medical records, schedules
- **plants**: Plant tracking, care schedules
- **audit**: Audit logs, tags, reporting

## Database Patterns

### Concurrency Control

**Optimistic Locking (VersionMixin):**
- Use `VersionMixin` for resources updated by multiple users
- SQLAlchemy auto-increments `version_id` on each update
- Stale writes raise `StaleDataError` → return 409 Conflict
- Example: Lists, expenses that users collaborate on

```python
class List(BaseModel, VersionMixin):
    version_id: Mapped[int] = mapped_column(nullable=False, default=1)
    __mapper_args__ = {"version_id_col": version_id}
```

**Pessimistic Locking (SELECT FOR UPDATE):**
- Use for critical inventory/finance operations
- Prevents race conditions on counters and balances

```python
result = await db.execute(
    select(Item).where(Item.id == item_id).with_for_update()
)
item = result.scalar_one()
item.quantity_value -= quantity
```

### Query Performance

- **Always eager load relationships** using `selectinload()` (To-Many) or `joinedload()` (To-One)
- **Never access relationships in loops** without eager loading
- Default transaction isolation: `READ COMMITTED`

### Models

- All models inherit from `BaseModel` which provides: `id`, `created_at`, `updated_at`
- Import `BaseModel`, `TimestampMixin`, `VersionMixin` from `mitlist.db.base`
- All model imports must be added to `alembic/env.py` for migration detection

## API Contracts

### Success Responses
- **No envelope** - resources returned directly as JSON
- Use appropriate HTTP status codes (200, 201, 204)

### Error Responses (RFC 7807)
All errors return standardized JSON with:
- `type`: Error category (error:validation, error:not-found, error:conflict, error:business-logic)
- `code`: Machine-readable error code
- `detail`: Human-readable message
- `instance`: Request path
- `trace_id`: Correlation ID for debugging

Example:
```json
{
  "type": "error:business-logic",
  "code": "STALE_WRITE",
  "detail": "Resource was modified by another request",
  "instance": "/api/v1/lists/1",
  "trace_id": "abc-123-def"
}
```

## Authentication & Authorization

### Zitadel OIDC Integration
- Primary authentication via Zitadel (self-hosted OIDC provider)
- Bearer token validation using JWKS
- Optional introspection for critical paths via `require_introspection_user`
- Auto-create users on first login if `ZITADEL_USER_AUTOCREATE=true`

### Dependencies
- `get_current_user`: Standard auth dependency, validates JWT locally
- `require_introspection_user`: Critical paths that need active token verification
- `get_current_group_id`: Resolves group scope from `X-Group-ID` header or `group_id` query param
- `require_group_admin`: Validates user has ADMIN role in group

### Group-Scoped Resources
- Most resources belong to a group (multi-tenant)
- Provide group context via `X-Group-ID` header (preferred) or `group_id` query param
- Dependencies validate group membership before allowing access

## Observability

### Request Context
Every request automatically tracks:
- `trace_id`: Correlation ID from `X-Request-ID` header or auto-generated UUID
- `user_id`: Current authenticated user
- `group_id`: Current group scope (when applicable)

### Structured Logging
- Development: Console format with colors
- Production: JSON format for log aggregation
- All log entries include trace_id, user_id, group_id context
- Use `logging.getLogger(__name__)` in each module

### OpenTelemetry
- FastAPI auto-instrumentation enabled
- Trace propagation via `X-Request-ID` header
- Export endpoint configurable via `OTEL_EXPORTER_OTLP_ENDPOINT`

### Health Checks
- `/health/live`: Liveness probe (always 200)
- `/health/ready`: Readiness probe (checks DB connectivity)

## Adding a New Module

1. Create module directory: `mitlist/modules/<name>/`
2. Create required files:
   - `interface.py` - Public API exports
   - `models.py` - SQLAlchemy ORM models
   - `schemas.py` - Pydantic request/response schemas
   - `service.py` - Business logic functions
   - `api.py` - FastAPI router with endpoints
3. Import models in `alembic/env.py` for migration detection
4. Register router in `mitlist/api/router.py`:
   ```python
   from mitlist.modules.<name> import api as <name>_api
   api_router.include_router(<name>_api.router, dependencies=[Depends(get_current_user)])
   ```
5. Run `uv run alembic revision --autogenerate -m "Add <name> module"`

## Important Files

- `mitlist/main.py`: Application factory and FastAPI setup
- `mitlist/api/router.py`: Router aggregation (where all modules register)
- `mitlist/api/deps.py`: Shared FastAPI dependencies (auth, db session)
- `mitlist/core/config.py`: Settings loaded from environment variables
- `mitlist/core/errors.py`: RFC 7807 error handling and custom exceptions
- `mitlist/db/base.py`: SQLAlchemy base and mixins (VersionMixin, TimestampMixin)
- `mitlist/db/engine.py`: Async database engine and session factory
- `alembic/env.py`: Migration configuration (import all models here)

## Environment Variables

See `.env.example`. Key variables:
- `ENVIRONMENT`: local, development, or production
- `POSTGRES_SERVER`: Database host (use `db` for Docker Compose, `localhost` for local psql)
- `ZITADEL_BASE_URL`: Self-hosted Zitadel instance URL
- `ZITADEL_AUDIENCE`: Expected audience claim in access tokens
- `SECRET_KEY`: Secret key for application use
- `OTEL_EXPORTER_OTLP_ENDPOINT`: OpenTelemetry collector endpoint (optional)
