"""
Test FastAPI application boot, metadata, and root routing.
"""

import pytest
from httpx import AsyncClient
from app.core.config import settings


@pytest.mark.asyncio
async def test_app_metadata():
    """Verify application configuration metadata."""
    assert settings.PROJECT_NAME == "CivicMind AI Intelligence Backend"
    assert settings.API_V1_PREFIX == "/api/v1"
    assert settings.EMBEDDING_DIMENSION == 768


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Verify the root landing endpoint returns operational status."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert data["platform"] == settings.PROJECT_NAME
    assert data["documentation"] == f"{settings.API_V1_PREFIX}/docs"


@pytest.mark.asyncio
async def test_openapi_schema(client: AsyncClient):
    """Verify OpenAPI 3.x schema generation is valid."""
    response = await client.get(f"{settings.API_V1_PREFIX}/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["openapi"].startswith("3.")
    assert schema["info"]["title"] == settings.PROJECT_NAME
