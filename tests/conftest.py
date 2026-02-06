"""Pytest fixtures for testing."""

import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from mitlist.db.base import Base
from mitlist.main import app
from mitlist.modules.auth.models import Group, User, UserGroup
from mitlist.modules.finance.models import Category


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Create test database engine."""
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    await test_engine.dispose()


@pytest.fixture
async def db(engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for each test."""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def test_user(db: AsyncSession) -> User:
    """Create test user."""
    user = User(
        email="test@example.com",
        hashed_password="EXTERNAL_AUTH:test-sub",
        name="Test User",
        is_active=True,
        preferences={},
        last_login_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@pytest.fixture
async def test_user2(db: AsyncSession) -> User:
    """Create second test user."""
    user = User(
        email="test2@example.com",
        hashed_password="EXTERNAL_AUTH:test-sub-2",
        name="Test User 2",
        is_active=True,
        preferences={},
        last_login_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@pytest.fixture
async def test_group(db: AsyncSession, test_user: User) -> Group:
    """Create test group with test_user as admin."""
    group = Group(
        name="Test Group",
        description="Test group for testing",
        created_by_id=test_user.id,
    )
    db.add(group)
    await db.flush()
    await db.refresh(group)

    membership = UserGroup(
        user_id=test_user.id,
        group_id=group.id,
        role="ADMIN",
        joined_at=datetime.now(timezone.utc),
    )
    db.add(membership)
    await db.flush()
    return group


@pytest.fixture
async def test_category(db: AsyncSession, test_group: Group) -> Category:
    """Create test category."""
    category = Category(
        group_id=test_group.id,
        name="Groceries",
        icon_emoji="🛒",
        color_hex="#FF5733",
        is_income=False,
    )
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return category


@pytest.fixture
async def client(
    db: AsyncSession, test_user: User, test_group: Group
) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with mocked authentication."""

    async def override_get_db():
        yield db

    async def override_get_current_user():
        return test_user

    from mitlist.api.deps import get_current_user, get_db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Group-ID": str(test_group.id)},
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
