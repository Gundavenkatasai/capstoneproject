"""
Test Redis connectivity, ping, and basic cache operations.
"""

import pytest
from app.core.redis import get_redis_client, check_redis_health


@pytest.mark.asyncio
async def test_redis_health():
    """Verify check_redis_health returns True and PONG."""
    is_ok, msg = await check_redis_health()
    assert is_ok is True
    assert "PONG" in msg


@pytest.mark.asyncio
async def test_redis_crud_operations():
    """Verify Redis set, get, ttl, and delete cycle."""
    redis = get_redis_client()
    test_key = "test:civicmind:ping"
    test_val = "operational"

    # Set with 60s TTL
    await redis.set(test_key, test_val, ex=60)

    # Get
    retrieved = await redis.get(test_key)
    assert retrieved == test_val

    # Delete
    deleted = await redis.delete(test_key)
    assert deleted == 1

    # Verify gone
    assert await redis.get(test_key) is None
