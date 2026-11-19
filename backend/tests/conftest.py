"""
CivicMind AI — Pytest Configuration & Shared Fixtures
"""

import sys
from pathlib import Path
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from typing import AsyncGenerator

# Ensure backend root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.main import app
from app.core.database import AsyncSessionFactory, async_engine
from app.core.redis import get_redis_client, close_redis_connection
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Asynchronous HTTP test client bound directly to the FastAPI ASGI application.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides an isolated async database session for individual test runs.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def cleanup_connections():
    """
    Ensures connection pools are cleanly closed when test suite finishes.
    """
    yield
    await close_redis_connection()
    await async_engine.dispose()
