"""
WMI Database Module
====================
Sets up SQLAlchemy async engine, session factory, and declarative base
for PostgreSQL. Provides a dependency injection function for FastAPI routes.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from backend.app.config import get_settings


# --- Declarative Base ---

class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# --- Engine & Session Factory ---

settings = get_settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,          # Set True for SQL debugging
    pool_size=10,        # Connection pool size
    max_overflow=20,     # Extra connections beyond pool_size
    pool_pre_ping=True,  # Verify connections before use
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
)


# --- FastAPI Dependency ---

async def get_db() -> AsyncSession:
    """
    FastAPI dependency that yields an async database session.
    Automatically commits on success and rolls back on exception.

    Usage in routes:
        @router.get("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# --- Lifecycle Helpers ---

async def init_db():
    """
    Creates all tables defined by ORM models.
    Called once on application startup.
    """
    async with engine.begin() as conn:
        # Import all models so they are registered with Base.metadata
        import backend.app.models  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    Disposes the connection pool.
    Called on application shutdown.
    """
    await engine.dispose()
