"""
CivicMind AI — AI Operational Preview Endpoints
Provides deterministic triage classification and routing preview fallbacks.
"""

from fastapi import APIRouter
from app.schemas.grievance import TriagePreviewRequest, TriagePreviewResponse
from app.services.grievance_service import GrievanceService


router = APIRouter(prefix="/ai", tags=["AI Intelligence Preview"])


@router.post(
    "/triage-preview",
    response_model=TriagePreviewResponse,
    summary="Preview AI Grievance Triage",
    description="Provides instant municipal department routing, category prediction, priority classification, and SLA estimate before final grievance submission.",
)
async def triage_preview(payload: TriagePreviewRequest) -> TriagePreviewResponse:
    return GrievanceService.triage_preview(payload)
