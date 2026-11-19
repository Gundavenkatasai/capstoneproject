"""
Test system health probes: /health, /health/database, /health/redis, /api/v1/health.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_aggregate_health_endpoint(client: AsyncClient):
    """Verify /health returns 200 with all components healthy."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"]["reachable"] is True
    assert data["database"]["status"] == "healthy"
    assert data["redis"]["reachable"] is True
    assert data["redis"]["status"] == "healthy"
    assert data["pgvector"]["reachable"] is True
    assert data["pgvector"]["status"] == "healthy"
    assert data["pgvector"]["details"]["dimension"] == 768


@pytest.mark.asyncio
async def test_database_health_endpoint(client: AsyncClient):
    """Verify dedicated /health/database probe returns 200."""
    response = await client.get("/health/database")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "postgresql-pgvector"
    assert data["status"] == "healthy"
    assert data["reachable"] is True
    assert "pgvector extension enabled" in data["message"]


@pytest.mark.asyncio
async def test_redis_health_endpoint(client: AsyncClient):
    """Verify dedicated /health/redis probe returns 200."""
    response = await client.get("/health/redis")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "redis"
    assert data["status"] == "healthy"
    assert data["reachable"] is True
    assert "PONG" in data["message"]


@pytest.mark.asyncio
async def test_api_v1_health_endpoint(client: AsyncClient):
    """Verify /api/v1/health returns 200."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "civicmind-api-v1"
    assert data["status"] == "healthy"
    assert data["reachable"] is True
