"""
CivicMind AI — Redis Client & Health Check Module
"""

import logging
from redis.asyncio import Redis, from_url
from app.core.config import settings

logger = logging.getLogger("civicmind.redis")

_redis_client: Redis | None = None


def get_redis_client() -> Redis:
    """
    Get or initialize the shared async Redis connection pool.
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = from_url(
            settings.redis_connection_url,
            decode_responses=True,
            health_check_interval=30,
        )
    return _redis_client


async def close_redis_connection() -> None:
    """
    Gracefully close the Redis client pool on application shutdown.
    """
    global _redis_client
    if _redis_client is not None:
        try:
            await _redis_client.aclose()
        except Exception:
            pass
        _redis_client = None
        logger.info("Closed Redis connection pool.")


async def check_redis_health() -> tuple[bool, str]:
    """
    Ping the Redis service to verify broker and cache reachability.
    Returns: (is_healthy, detail_message)
    """
    try:
        client = get_redis_client()
        pong = await client.ping()
        if pong:
            return True, "Redis connection active (PONG received)"
        return False, "Redis did not return expected PONG response"
    except Exception as ex:
        logger.warning("Redis health check failed: %s", ex)
        return False, f"Redis connectivity error: {str(ex)}"
