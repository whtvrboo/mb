import pytest
import asyncio
from datetime import datetime
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from fastapi import FastAPI
from mitlist.modules.chores.api import router as chores_router
from mitlist.modules.plants.api import router as plants_router
from mitlist.modules.pets.api import router as pets_router
from mitlist.modules.assets.api import router as assets_router
from mitlist.db.base import Base
from mitlist.api import deps
from mitlist.modules.auth.models import User, UserGroup, Group

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

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
    app = FastAPI()
    app.include_router(chores_router)
    app.include_router(plants_router)
    app.include_router(pets_router)
    app.include_router(assets_router)
    return app

@pytest.fixture(scope="function")
async def client(app_instance: FastAPI, db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
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
    group = Group(
        name="Test Group",
        created_by_id=test_user.id
    )
    db_session.add(group)
    await db_session.flush()
    await db_session.refresh(group)
    
    membership = UserGroup(
        user_id=test_user.id,
        group_id=group.id,
        role="ADMIN",
        joined_at=datetime.utcnow()
    )
    db_session.add(membership)
    await db_session.commit()
    return group

@pytest.fixture
def auth_headers(test_group: Group) -> dict:
    """Return headers for authenticated requests."""
    return {"Authorization": "Bearer test_token", "X-Group-ID": str(test_group.id)}

@pytest.fixture(scope="function")
async def authed_client(client: AsyncClient, app_instance: FastAPI, db_session: AsyncSession, test_user: User, test_group: Group) -> AsyncClient:
    """Client with overridden auth dependencies."""
    
    async def override_get_current_user():
        return test_user
        
    async def override_get_current_group_id():
        return test_group.id
        
    app_instance.dependency_overrides[deps.get_current_user] = override_get_current_user
    app_instance.dependency_overrides[deps.get_current_group_id] = override_get_current_group_id
    
    return client
