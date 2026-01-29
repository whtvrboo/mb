"""Async SQLAlchemy engine and session factory."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from mitlist.core.config import settings

# Create async engine with connection pooling
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    echo=settings.is_development,
)

# Create async session factory
# expire_on_commit=False prevents attribute expiration after commit
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """
    Dependency that yields an async database session.

    Usage in FastAPI routes:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
