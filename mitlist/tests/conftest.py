import pytest
import asyncio
from datetime import datetime, timezone
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from fastapi import FastAPI
from mitlist.modules.chores.api import router as chores_router
from mitlist.modules.plants.api import router as plants_router
from mitlist.modules.pets.api import router as pets_router
from mitlist.modules.assets.api import router as assets_router
from mitlist.modules.governance.api import router as governance_router
from mitlist.modules.audit.api import router as audit_router
from mitlist.modules.documents.api import router as documents_router
from mitlist.modules.lists.api import router as lists_router
from mitlist.modules.lists.api import inventory_router as lists_inventory_router
from mitlist.modules.notifications.api import router as notifications_router
from mitlist.modules.notifications.api import comments_router as notifications_comments_router
from mitlist.modules.notifications.api import reactions_router as notifications_reactions_router
from mitlist.modules.gamification.api import router as gamification_router
from mitlist.modules.recipes.api import router as recipes_router
from mitlist.modules.calendar.api import router as calendar_router
from mitlist.db.base import Base

# Import models so Base.metadata has all tables (governance, audit, documents, etc.)
from mitlist.modules.governance.models import Proposal, BallotOption, VoteRecord  # noqa: F401
from mitlist.modules.audit.models import AuditLog, Tag, TagAssignment, ReportSnapshot  # noqa: F401
from mitlist.modules.documents.models import Document, DocumentShare, SharedCredential  # noqa: F401
from mitlist.modules.lists.models import List, Item, InventoryItem, ListShare  # noqa: F401
from mitlist.modules.notifications.models import (
    Comment,
    Mention,
    Notification,
    NotificationPreference,
    Reaction,
)  # noqa: F401
from mitlist.modules.auth.models import CommonItemConcept  # noqa: F401
from mitlist.modules.gamification.models import (
    UserPoints,
    Achievement,
    UserAchievement,
    Streak,
    Leaderboard,
)  # noqa: F401 UserPoints, Achievement, UserAchievement, Streak, Leaderboard  # noqa: F401
from mitlist.modules.recipes.models import (
    Recipe,
    RecipeIngredient,
    RecipeStep,
    MealPlan,
    MealPlanShoppingSync,
)  # noqa: F401
from mitlist.modules.calendar.models import CalendarEvent, EventAttendee, Reminder  # noqa: F401
from mitlist.api import deps
from mitlist.modules.auth.models import User, UserGroup, Group, CommonItemConcept  # noqa: F401

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for a test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session
        # Cleanup
        await session.rollback()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def app_instance() -> FastAPI:
    """Create a fresh FastAPI app instance for testing."""
    from mitlist.core.errors import AppError, app_error_handler

    app = FastAPI()
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(chores_router)
    app.include_router(plants_router)
    app.include_router(pets_router)
    app.include_router(assets_router)
    app.include_router(governance_router)
    app.include_router(audit_router)
    app.include_router(documents_router)
    app.include_router(notifications_router)
    app.include_router(notifications_comments_router)
    app.include_router(notifications_reactions_router)
    app.include_router(gamification_router)
    app.include_router(recipes_router)
    app.include_router(calendar_router)
    app.include_router(lists_router)
    app.include_router(lists_inventory_router)
    return app


@pytest.fixture(scope="function")
async def client(
    app_instance: FastAPI, db_session: AsyncSession
) -> AsyncGenerator[AsyncClient, None]:
    """Get a TestClient with overridden dependencies."""

    async def override_get_db():
        yield db_session

    app_instance.dependency_overrides[deps.get_db] = override_get_db

    # We use http://test as base URL for httpx
    transport = ASGITransport(app=app_instance)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app_instance.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        name="Test User",
        hashed_password="hashed_secret",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_group(db_session: AsyncSession, test_user: User) -> Group:
    """Create a test group and add test user as admin."""
    group = Group(name="Test Group", created_by_id=test_user.id)
    db_session.add(group)
    await db_session.flush()
    await db_session.refresh(group)

    membership = UserGroup(
        user_id=test_user.id, group_id=group.id, role="ADMIN", joined_at=datetime.now(timezone.utc)
    )
    db_session.add(membership)
    await db_session.commit()
    return group


@pytest.fixture
def auth_headers(test_group: Group) -> dict:
    """Return headers for authenticated requests."""
    return {"Authorization": "Bearer test_token", "X-Group-ID": str(test_group.id)}


@pytest.fixture(scope="function")
async def authed_client(
    client: AsyncClient,
    app_instance: FastAPI,
    db_session: AsyncSession,
    test_user: User,
    test_group: Group,
) -> AsyncClient:
    """Client with overridden auth dependencies."""

    async def override_get_current_user():
        return test_user

    async def override_get_current_group_id():
        return test_group.id

    app_instance.dependency_overrides[deps.get_current_user] = override_get_current_user
    app_instance.dependency_overrides[deps.get_current_group_id] = override_get_current_group_id

    return client
