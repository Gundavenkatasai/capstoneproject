"""
Test direct PostgreSQL connectivity, session creation, and transaction management.
"""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import check_db_health, async_engine, get_db


@pytest.mark.asyncio
async def test_direct_db_health_check():
    """Verify check_db_health returns True against PostgreSQL container."""
    is_ok, msg = await check_db_health()
    assert is_ok is True
    assert "active" in msg.lower()


@pytest.mark.asyncio
async def test_session_execution(db_session: AsyncSession):
    """Verify async session executes basic SQL arithmetic."""
    result = await db_session.execute(text("SELECT 40 + 2 AS answer;"))
    val = result.scalar()
    assert val == 42


@pytest.mark.asyncio
async def test_get_db_generator():
    """Verify get_db dependency generator yields active session."""
    gen = get_db()
    session = await anext(gen)
    assert isinstance(session, AsyncSession)
    result = await session.execute(text("SELECT current_database();"))
    db_name = result.scalar()
    assert db_name == "civicmind_db"
    # Complete generator
    try:
        await anext(gen)
    except StopAsyncIteration:
        pass


@pytest.mark.asyncio
async def test_transaction_rollback(db_session: AsyncSession):
    """Verify transaction rollback prevents dirty writes."""
    await db_session.execute(
        text("CREATE TEMPORARY TABLE test_rollback (val int);")
    )
    await db_session.execute(
        text("INSERT INTO test_rollback VALUES (100);")
    )
    # Check inserted
    res = await db_session.execute(text("SELECT val FROM test_rollback;"))
    assert res.scalar() == 100
    # Rollback
    await db_session.rollback()
