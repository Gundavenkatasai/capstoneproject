"""
CivicMind AI — Early-Warning Radar API Router
Phase 6 Geospatial Grievance Intelligence & Hotspot Detection.

Provides endpoints for querying spatial hotspots, triggering clustering scans,
retrieving summary metrics, and acknowledging task force dispatches.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_optional_current_user, require_role
from app.models.user import User
from app.schemas.radar import (
    HotspotSchema,
    HotspotAcknowledgeRequest,
    RadarSummaryResponse,
)
from app.services.radar_service import radar_service

router = APIRouter(prefix="", tags=["Early-Warning Radar & Hotspots"])


@router.get(
    "/early-warning/hotspots",
    response_model=List[HotspotSchema],
    summary="List Geographic Hotspots",
    description="Returns active geographic grievance clusters with velocity and risk metrics.",
)
@router.get(
    "/radar/hotspots",
    response_model=List[HotspotSchema],
    summary="List Geographic Hotspots (Alias)",
    include_in_schema=False,
)
async def list_hotspots(
    category: Optional[str] = Query(None, description="Filter by grievance category"),
    risk_level: Optional[str] = Query(None, alias="riskLevel", description="Filter by risk tier (critical, high, medium, low)"),
    ward: Optional[str] = Query(None, description="Filter by ward name"),
    db: AsyncSession = Depends(get_db),
) -> List[HotspotSchema]:
    return await radar_service.get_hotspots(
        db=db,
        category=category,
        risk_level=risk_level,
        ward=ward,
    )


@router.get(
    "/early-warning/hotspots/{hotspot_id}",
    response_model=HotspotSchema,
    summary="Get Hotspot Details",
    description="Retrieves a specific hotspot by its unique identifier.",
)
async def get_hotspot_by_id(
    hotspot_id: str,
    db: AsyncSession = Depends(get_db),
) -> HotspotSchema:
    item = await radar_service.get_hotspot_by_id(db=db, hotspot_id=hotspot_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hotspot with id '{hotspot_id}' not found.",
        )
    return item


@router.post(
    "/early-warning/hotspots/{hotspot_id}/acknowledge",
    response_model=HotspotSchema,
    summary="Acknowledge & Dispatch Intervention",
    description="Marks a hotspot as acknowledged and dispatches task force teams.",
)
async def acknowledge_hotspot(
    hotspot_id: str,
    body: Optional[HotspotAcknowledgeRequest] = None,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> HotspotSchema:
    notes = body.notes if body else "Emergency task force intervention dispatched"
    updated = await radar_service.acknowledge_hotspot(
        db=db,
        hotspot_id=hotspot_id,
        notes=notes,
        current_user=current_user,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hotspot with id '{hotspot_id}' not found.",
        )
    return updated


@router.get(
    "/early-warning/summary",
    response_model=RadarSummaryResponse,
    summary="Radar Analytics Summary",
    description="Returns aggregate early-warning statistics across all active hotspots.",
)
@router.get(
    "/radar/summary",
    response_model=RadarSummaryResponse,
    summary="Radar Analytics Summary (Alias)",
    include_in_schema=False,
)
async def get_radar_summary(
    db: AsyncSession = Depends(get_db),
) -> RadarSummaryResponse:
    return await radar_service.get_radar_summary(db=db)


@router.post(
    "/early-warning/scan",
    response_model=List[HotspotSchema],
    summary="Execute Spatial Clustering Scan",
    description="Triggers DBSCAN spatial clustering over active grievances to discover or update hotspots.",
)
async def execute_spatial_scan(
    radius_km: float = Query(0.5, ge=0.1, le=5.0, description="Epsilon clustering radius in km"),
    min_samples: int = Query(2, ge=2, le=20, description="Minimum incidents to form a cluster"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[HotspotSchema]:
    return await radar_service.scan_and_sync_hotspots(
        db=db,
        radius_km=radius_km,
        min_samples=min_samples,
    )
