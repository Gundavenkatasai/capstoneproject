"""
CivicMind AI — Geospatial Hotspot & Early-Warning Radar Schemas
Pydantic v2 validation contracts for Phase 6 spatial clustering and early-warning radar.
Supports both camelCase (Next.js frontend) and snake_case (FastAPI backend).
"""

from typing import List, Dict, Any, Optional, Literal, Union
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, AliasChoices, field_validator


class HotspotSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: str
    title: str
    category: str
    zone: str
    ward: str
    lat: float = Field(..., validation_alias=AliasChoices("latitude", "lat"))
    lng: float = Field(..., validation_alias=AliasChoices("longitude", "lng"))
    radiusMeters: int = Field(..., validation_alias=AliasChoices("radius_meters", "radiusMeters"))
    complaintCount: int = Field(..., validation_alias=AliasChoices("complaint_count", "complaintCount"))
    riskLevel: Literal["low", "medium", "high", "critical"] = Field(
        ..., validation_alias=AliasChoices("risk_level", "riskLevel")
    )
    riskScore: int = Field(..., validation_alias=AliasChoices("risk_score", "riskScore"))
    trend: Literal["increasing", "stable", "decreasing"]
    summary: str
    recommendedAction: str = Field(
        ..., validation_alias=AliasChoices("recommended_action", "recommendedAction")
    )
    relatedComplaintIds: List[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("related_complaint_ids", "relatedComplaintIds"),
    )
    detectedAt: str = Field(
        ..., validation_alias=AliasChoices("detected_at", "detectedAt")
    )
    historicalVelocity: List[int] = Field(
        default_factory=list,
        validation_alias=AliasChoices("historical_velocity", "historicalVelocity"),
    )
    isAcknowledged: bool = Field(
        False, validation_alias=AliasChoices("is_acknowledged", "isAcknowledged")
    )
    source: str = "operational"

    @field_validator("detectedAt", mode="before")
    @classmethod
    def parse_detected_at(cls, v: Any) -> str:
        if isinstance(v, datetime):
            return v.isoformat()
        return str(v)


class HotspotAcknowledgeRequest(BaseModel):
    notes: Optional[str] = Field(None, max_length=1000)


class RadarSummaryResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    totalActiveHotspots: int = Field(..., validation_alias=AliasChoices("total_active_hotspots", "totalActiveHotspots"))
    criticalHotspots: int = Field(..., validation_alias=AliasChoices("critical_hotspots", "criticalHotspots"))
    highRiskHotspots: int = Field(..., validation_alias=AliasChoices("high_risk_hotspots", "highRiskHotspots"))
    emergingSurges: int = Field(..., validation_alias=AliasChoices("emerging_surges", "emergingSurges"))
    mostAffectedCategory: str = Field(..., validation_alias=AliasChoices("most_affected_category", "mostAffectedCategory"))
    mostAffectedWard: str = Field(..., validation_alias=AliasChoices("most_affected_ward", "mostAffectedWard"))
    wardRiskDistribution: Dict[str, int] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("ward_risk_distribution", "wardRiskDistribution"),
    )
    categoryDistribution: Dict[str, int] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("category_distribution", "categoryDistribution"),
    )
    isOperational: bool = Field(
        True, validation_alias=AliasChoices("is_operational", "isOperational")
    )
    dataSource: str = Field(
        "postgres_operational",
        validation_alias=AliasChoices("data_source", "dataSource"),
    )
