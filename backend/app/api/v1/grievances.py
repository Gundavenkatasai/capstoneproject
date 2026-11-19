"""
CivicMind AI — Grievance Management & Lifecycle API Endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.grievance import (
    GrievanceCreateRequest,
    GrievanceResponse,
    GrievanceListResponse,
    GrievanceStatusTransitionRequest,
    ResolutionReportCreateRequest,
    CitizenResolutionVerifyRequest,
    GrievanceAppealRequest,
    GrievanceReassignRequest,
)
from app.services.grievance_service import GrievanceService


router = APIRouter(prefix="/grievances", tags=["Grievance Lifecycle Engine"])


@router.post(
    "",
    response_model=GrievanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register Citizen Grievance",
    description="Submits a new citizen grievance, assigns an atomic sequence-based tracking ID (GRV-YYYY-XXXXX), calculates SLA, associates pre-uploaded evidence, and logs initial timeline event.",
)
async def create_grievance(
    payload: GrievanceCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GrievanceResponse:
    ip_address = request.client.host if request.client else "127.0.0.1"
    return await GrievanceService.create_grievance(
        session=db,
        payload=payload,
        current_user=current_user,
        ip_address=ip_address,
    )


@router.get(
    "",
    response_model=GrievanceListResponse,
    summary="List Grievances (Role-Scoped & Filtered)",
    description="Returns paginated grievances scoped by caller role (citizens see own, officers see department/assigned, admins see all) with multi-field search and status/priority filters.",
)
async def list_grievances(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by grievance status"),
    priority: Optional[str] = Query(None, description="Filter by grievance priority"),
    department_id: Optional[str] = Query(None, description="Filter by department ID"),
    category: Optional[str] = Query(None, description="Filter by category substring"),
    ward: Optional[str] = Query(None, description="Filter by municipal ward"),
    search: Optional[str] = Query(None, description="Search query across ID, title, description, address"),
    assigned_to_me: bool = Query(False, description="Filter only grievances assigned to caller (officers)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GrievanceListResponse:
    return await GrievanceService.list_grievances(
        session=db,
        current_user=current_user,
        page=page,
        page_size=page_size,
        status_filter=status,
        priority_filter=priority,
        department_filter=department_id,
        category_filter=category,
        ward_filter=ward,
        search=search,
        assigned_to_me=assigned_to_me,
    )


@router.get(
    "/{id}",
    response_model=GrievanceResponse,
    summary="Retrieve Grievance Details",
    description="Fetches full grievance dossier including location, evidence, timeline, and resolution reports. Protected by strict IDOR isolation.",
)
async def get_grievance_by_id(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GrievanceResponse:
    return await GrievanceService.get_grievance_by_id(
        session=db,
        grievance_id=id,
        current_user=current_user,
    )


@router.patch(
    "/{id}/status",
    response_model=GrievanceResponse,
    summary="Transition Grievance Lifecycle Status",
    description="Validates and executes lifecycle state machine transitions with role enforcement and immutable audit recording.",
)
async def transition_status(
    id: str,
    payload: GrievanceStatusTransitionRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GrievanceResponse:
    ip_address = request.client.host if request.client else "127.0.0.1"
    return await GrievanceService.transition_status(
        session=db,
        grievance_id=id,
        target_status=payload.status,
        notes=payload.notes,
        current_user=current_user,
        ip_address=ip_address,
    )


@router.post(
    "/{id}/resolve",
    response_model=GrievanceResponse,
    summary="Submit Field Resolution Report",
    description="Enables designated municipal officers or administrators to file resolution documentation and photographic evidence, advancing the grievance to 'resolution_submitted'.",
)
async def submit_resolution(
    id: str,
    payload: ResolutionReportCreateRequest,
    request: Request,
    current_user: User = Depends(require_role(["officer", "admin"])),
    db: AsyncSession = Depends(get_db),
) -> GrievanceResponse:
    ip_address = request.client.host if request.client else "127.0.0.1"
    return await GrievanceService.submit_resolution(
        session=db,
        grievance_id=id,
        report_text=payload.report_text,
        officer_evidence_urls=payload.officer_evidence_urls,
        current_user=current_user,
        ip_address=ip_address,
    )


@router.post(
    "/{id}/verify",
    response_model=GrievanceResponse,
    summary="Citizen Verification of Resolution",
    description="Citizen accepts or rejects the officer's resolution. Acceptance marks the grievance as 'citizen_verified' or 'closed'; rejection transitions it to 'reopened'.",
)
async def verify_resolution(
    id: str,
    payload: CitizenResolutionVerifyRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GrievanceResponse:
    ip_address = request.client.host if request.client else "127.0.0.1"
    return await GrievanceService.verify_resolution(
        session=db,
        grievance_id=id,
        rating=payload.rating,
        comment=payload.comment,
        action=payload.action,
        current_user=current_user,
        ip_address=ip_address,
    )


@router.post(
    "/{id}/appeal",
    response_model=GrievanceResponse,
    summary="File Citizen Appeal / Reopen Grievance",
    description="Citizen appeals a closed or verified grievance with substantive grounds, transitioning the grievance to 'reopened' for supervisory intervention.",
)
async def submit_appeal(
    id: str,
    payload: GrievanceAppealRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GrievanceResponse:
    ip_address = request.client.host if request.client else "127.0.0.1"
    return await GrievanceService.submit_appeal(
        session=db,
        grievance_id=id,
        reason=payload.reason,
        evidence_file_ids=payload.evidence_file_ids,
        current_user=current_user,
        ip_address=ip_address,
    )


@router.post(
    "/{id}/assign",
    response_model=GrievanceResponse,
    summary="Reassign Department or Officer",
    description="Reallocates grievance responsibility across departments or field officers. Restricted to officers and administrators.",
)
async def reassign_grievance(
    id: str,
    payload: GrievanceReassignRequest,
    request: Request,
    current_user: User = Depends(require_role(["officer", "admin"])),
    db: AsyncSession = Depends(get_db),
) -> GrievanceResponse:
    ip_address = request.client.host if request.client else "127.0.0.1"
    return await GrievanceService.reassign_grievance(
        session=db,
        grievance_id=id,
        department_id=payload.department_id,
        officer_id=payload.officer_id,
        reason=payload.reason,
        current_user=current_user,
        ip_address=ip_address,
    )
