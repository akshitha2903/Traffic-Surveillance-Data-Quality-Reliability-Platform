from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings

# Create database connection engine using asyncpg driver
engine = create_async_engine(
    settings.postgres_dsn,
    echo=False,  # Set to True for SQL log output in development if needed
    pool_pre_ping=True,
)

# Session factory for generating db sessions
SessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection helper for FastAPI endpoints."""
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
