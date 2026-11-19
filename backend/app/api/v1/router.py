"""
CivicMind AI — API v1 Router Assembly
Centralizes versioned routes. Prepared with modular endpoints for future implementation phases.
"""

from datetime import datetime, timezone
import time
from fastapi import APIRouter
from app.schemas.health import SingleComponentHealthResponse
from app.core.database import check_db_health
from app.core.config import settings

api_router = APIRouter()


@api_router.get(
    "/health",
    response_model=SingleComponentHealthResponse,
    summary="API v1 Health Probe",
    description="Validates that the API v1 routing layer is active and operational.",
    tags=["System Health"],
)
async def api_v1_health() -> SingleComponentHealthResponse:
    start_time = time.perf_counter()
    db_ok, db_msg = await check_db_health()
    elapsed = (time.perf_counter() - start_time) * 1000

    return SingleComponentHealthResponse(
        service="civicmind-api-v1",
        status="healthy" if db_ok else "degraded",
        reachable=True,
        message=f"API v1 gateway active. Database: {db_msg}",
        latency_ms=round(elapsed, 2),
        timestamp=datetime.now(timezone.utc),
    )
