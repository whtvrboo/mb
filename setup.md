Setting up a FastAPI repository for a **Modular Monolith** with a team of 3-5 developers requires specific attention to **bootstrapping** and **developer experience (DX)**. If you get the foundation wrong, you will fight circular imports and dependency injection errors forever.

Here is your **Setup Checklist** to get it right on Day 1.

---

### 1. 📦 Dependency Management: Use `uv` or `Poetry`

Do not use a raw `requirements.txt`. You need lockfiles to ensure all 5 developers are on the _exact_ same version of libraries.

- **Recommendation:** Use **[uv](https://github.com/astral-sh/uv)**. It is essentially instant, handles Python versions, and is compatible with `requirements.txt` workflows if needed.
- **Why:** It replaces `pip`, `pip-tools`, and `virtualenv`.
- **Command:** `uv init` then `uv add fastapi uvicorn sqlalchemy alembic pydantic-settings`.

---

### 2. ⚙️ Configuration: `pydantic-settings`

Stop using `os.getenv()` scattered throughout your code. Centralize configuration.

- **The Pattern:**

  ```python
  # app/core/config.py
  from pydantic_settings import BaseSettings, SettingsConfigDict

  class Settings(BaseSettings):
      model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

      PROJECT_NAME: str = "HomeOS"
      POSTGRES_SERVER: str
      POSTGRES_USER: str
      POSTGRES_PASSWORD: str
      POSTGRES_DB: str
      SECRET_KEY: str

      @property
      def SQLALCHEMY_DATABASE_URI(self) -> str:
          return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

  settings = Settings()
  ```

- **Keep in Mind:** Type-cast your env vars here (e.g., `DEBUG: bool`). It prevents string comparison bugs (`if "False"` evaluates to True).

---

### 3. 🏗️ The "App Factory" Pattern

Do not define `app = FastAPI()` globally in `main.py` if you can avoid it. Use a factory function. This allows you to spin up different versions of the app for testing (e.g., overriding the DB with a mock).

```python
# app/main.py
from fastapi import FastAPI
from app.core.config import settings
from app.api.main import api_router  # The main router aggregator

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        # Disable docs in prod
        docs_url="/docs" if settings.ENVIRONMENT == "local" else None,
    )

    # Register Global Middleware (CORS, etc)
    application.add_middleware(...)

    # Register Exception Handlers
    application.add_exception_handler(...)

    # Include Routes
    application.include_router(api_router, prefix="/api/v1")

    return application

app = create_application()
```

---

### 4. 💉 Dependency Injection (DI) Strategy

FastAPI’s DI system is powerful but can get messy.

- **The Golden Rule:** Never instantiate a Service manually inside a Route. Always inject it.
- **Why:** This allows you to swap the Service for a Mock during tests.
- **Setup:**

  ```python
  # app/api/deps.py
  from typing import Generator
  from sqlalchemy.orm import Session
  from app.core.database import SessionLocal

  def get_db() -> Generator:
      db = SessionLocal()
      try:
          yield db
      finally:
          db.close()

  # In your Router
  @router.post("/")
  def create_item(
      db: Session = Depends(get_db), # DB injection
      service: ItemService = Depends(get_item_service) # Service injection
  ):
      pass
  ```

---

### 5. 🔄 Handling Circular Imports (The #1 Headache)

With a Modular Monolith (Finance needs Auth, Auth needs Notifications), you **will** hit circular imports.

- **Solution 1: `TYPE_CHECKING` block**
  Use this for type hinting inside Pydantic models or SQLAlchemy relationships so runtime execution doesn't crash.
  ```python
  from typing import TYPE_CHECKING
  if TYPE_CHECKING:
      from app.modules.finance.models import Expense
  ```
- **Solution 2: String Forward References**
  In SQLAlchemy: `relationship("Expense", ...)` instead of `relationship(Expense, ...)`
- **Solution 3: Local Imports**
  Import the module _inside_ the function/method, not at the top of the file. (Use sparingly).

---

### 6. 🗄️ Async Database Engine (SQLAlchemy 2.0)

Since you are starting fresh, use **Async SQLAlchemy**.

- **Why:** If you use Sync code, one long database query (e.g., "Calculate Monthly Settlement") will block the entire API for everyone else.
- **The Driver:** Use `asyncpg`.
- **Connection Pooling:** Configure this immediately.

  ```python
  # app/core/database.py
  from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

  engine = create_async_engine(
      settings.SQLALCHEMY_DATABASE_URI,
      pool_size=20,        # Connections to keep open
      max_overflow=10,     # Burst connections
      pool_pre_ping=True,  # Check connection health before using
  )
  SessionLocal = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
  ```

---

### 7. 🧹 Linting & Formatting (Ruff)

Don't waste time in Code Review arguing about quotes or trailing commas.

- **Tool:** Use **Ruff**. It replaces Black, Flake8, and Isort.
- **Config (`pyproject.toml`):**

  ```toml
  [tool.ruff]
  line-length = 100
  target-version = "py311"

  [tool.ruff.lint]
  select = ["E", "F", "I", "B"] # Errors, Pyflakes, Imports, Bugbear
  ```

- **Pre-commit:** Set up a `pre-commit` hook so bad code can't be committed.

---

### 8. 🚨 Exception Handling (RFC 7807)

FastAPI's default errors are ugly. Create a global exception handler that returns structured JSON.

- **Create a custom exception base class:**
  ```python
  # app/core/exceptions.py
  class AppError(Exception):
      def __init__(self, code: str, msg: str, status_code: int = 400):
          self.code = code
          self.msg = msg
          self.status_code = status_code
  ```
- **Register handler:** In `main.py`, catch `AppError` and return a JSONResponse with `{"type": "error", "code": ...}`.

---

### 9. 🐳 Docker & Development Environment

- **Docker Compose:** You need at least 2 services locally:
  1.  `db` (Postgres)
  2.  `app` (FastAPI with reload enabled)
- **Volume Mounting:** Mount your local code into the container so you don't have to rebuild the image on every change.
- **Networking:** Ensure your `config.py` allows the app to find the DB at host `db`, not `localhost`.

### Summary Checklist for Day 1:

1.  Initialize with `uv` or Poetry.
2.  Set up `pyproject.toml` with Ruff.
3.  Create `app/core/config.py`.
4.  Configure Async SQLAlchemy with `asyncpg`.
5.  Create the `create_app()` factory.
6.  Set up the Modular directory structure (`app/modules/`).
7.  Get `docker-compose up` running with a DB connection.
