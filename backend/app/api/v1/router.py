"""
CivicMind AI — API v1 Router Assembly
Centralizes versioned routes including authentication, RBAC gates, and system health.
"""

from datetime import datetime, timezone
import time
import uuid
from fastapi import APIRouter, Depends
from app.schemas.health import SingleComponentHealthResponse
from app.core.database import check_db_health
from app.core.dependencies import (
    get_current_user,
    require_role,
    verify_user_access,
    verify_department_access,
)
from app.models.user import User
from app.api.v1.auth import router as auth_router

api_router = APIRouter()

# Mount Authentication router
api_router.include_router(auth_router)


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


# ==============================================================================
# RBAC & Object-Level Authorization Verification Endpoints
# ==============================================================================

@api_router.get(
    "/rbac/citizen-only",
    summary="Citizen Role Gate Test",
    description="Protected endpoint restricted exclusively to users with citizen role.",
    tags=["Role-Based Access Control"],
)
async def rbac_citizen_only(current_user: User = Depends(require_role(["citizen"]))):
    return {"message": f"Welcome citizen {current_user.name}", "role": current_user.role}


@api_router.get(
    "/rbac/officer-only",
    summary="Officer Role Gate Test",
    description="Protected endpoint restricted exclusively to users with officer role.",
    tags=["Role-Based Access Control"],
)
async def rbac_officer_only(current_user: User = Depends(require_role(["officer"]))):
    return {"message": f"Welcome officer {current_user.name}", "role": current_user.role}


@api_router.get(
    "/rbac/admin-only",
    summary="Administrator Role Gate Test",
    description="Protected endpoint restricted exclusively to users with admin role.",
    tags=["Role-Based Access Control"],
)
async def rbac_admin_only(current_user: User = Depends(require_role(["admin"]))):
    return {"message": f"Welcome administrator {current_user.name}", "role": current_user.role}


@api_router.get(
    "/rbac/users/{target_user_id}/records",
    summary="Object-Level User Access IDOR Guard Test",
    description="Verifies that citizens can only access their own records, while administrators have elevated cross-user access.",
    tags=["Role-Based Access Control"],
)
async def rbac_object_level_user_check(
    target_user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
):
    verify_user_access(current_user, target_user_id)
    return {
        "message": f"Access granted to records for user {target_user_id}",
        "authorized_by": current_user.email,
        "caller_role": current_user.role,
    }


@api_router.get(
    "/rbac/departments/{department_id}/confidential",
    summary="Object-Level Department Access Guard Test",
    description="Verifies that officers can only access their assigned department data, while administrators have citywide jurisdiction.",
    tags=["Role-Based Access Control"],
)
async def rbac_object_level_dept_check(
    department_id: str,
    current_user: User = Depends(get_current_user),
):
    verify_department_access(current_user, department_id)
    return {
        "message": f"Access granted to department {department_id}",
        "authorized_by": current_user.email,
        "caller_role": current_user.role,
    }
