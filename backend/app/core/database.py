"""
CivicMind AI — Asynchronous SQLAlchemy 2.0 Database Session Manager
"""

from typing import AsyncGenerator
import logging
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text
from app.core.config import settings

logger = logging.getLogger("civicmind.database")

# Initialize async engine with connection pooling
async_engine: AsyncEngine = create_async_engine(
    settings.async_database_url,
    echo=settings.DEBUG and settings.ENVIRONMENT == "development_verbose",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    future=True,
)

# Async session factory
AsyncSessionFactory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency delivering transactional async database sessions.
    Automatically handles rollback on exceptions and guarantees session closure.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
        except Exception as ex:
            await session.rollback()
            logger.error("Database transaction rolled back due to error: %s", ex)
            raise
        finally:
            await session.close()


async def check_db_health() -> tuple[bool, str]:
    """
    Execute a low-overhead ping against the database to evaluate liveness.
    Returns: (is_healthy, detail_message)
    """
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1;"))
            row = result.scalar()
            if row == 1:
                return True, "PostgreSQL connection active and responding"
            return False, f"Unexpected ping response: {row}"
    except Exception as ex:
        logger.warning("Database health check failed: %s", ex)
        return False, f"Database connectivity error: {str(ex)}"


async def check_pgvector_extension() -> tuple[bool, str]:
    """
    Verify that the pgvector extension is installed and available in the current database.
    """
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(
                text("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
            )
            version = result.scalar()
            if version:
                return True, f"pgvector extension enabled (version: {version})"
            return False, "pgvector extension is NOT installed or enabled"
    except Exception as ex:
        return False, f"Error querying pgvector extension status: {str(ex)}"
