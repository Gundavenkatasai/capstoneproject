"""
CivicMind AI — Grievance, Lifecycle, Evidence & Resolution Pydantic Schemas
"""

import uuid
from typing import Optional, List, Literal, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, model_validator


GrievanceStatusType = Literal[
    "submitted",
    "analyzed",
    "assigned",
    "in_progress",
    "resolution_submitted",
    "citizen_verified",
    "closed",
    "escalated",
    "reopened",
]

GrievancePriorityType = Literal["critical", "high", "medium", "low"]
SlaBreachRiskType = Literal["critical", "high", "medium", "low"]
EvidenceFileType = Literal["image", "document", "audio"]


# ---------------------------------------------------------------------------
# Location Schema
# ---------------------------------------------------------------------------
class GrievanceLocationSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    address: str
    ward: str
    zone: str
    lat: float
    lng: float


# ---------------------------------------------------------------------------
# Evidence Schemas
# ---------------------------------------------------------------------------
class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    type: str
    url: str
    name: str
    size: str
    file_name: str
    fileName: str
    file_type: str
    fileType: str
    file_size_bytes: int
    fileSizeBytes: int
    storage_url: str
    storageUrl: str
    created_at: datetime
    createdAt: datetime


# ---------------------------------------------------------------------------
# Timeline Schemas
# ---------------------------------------------------------------------------
class TimelineEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    status: str
    title: str
    description: str
    timestamp: datetime
    actor: str
    actorRole: str
    actor_name: str
    actor_role: str
    notes: Optional[str] = None
    created_at: datetime
    createdAt: datetime


# ---------------------------------------------------------------------------
# Resolution Report Schemas
# ---------------------------------------------------------------------------
class ResolutionReportCreateRequest(BaseModel):
    report_text: str = Field(..., min_length=10, max_length=5000)
    officer_evidence_urls: List[str] = Field(default_factory=list)


class ResolutionReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    report_text: str
    reportText: str
    text: str
    resolved_at: datetime
    resolvedAt: datetime
    officer_evidence_urls: List[str]
    officerEvidence: List[str]
    citizen_rating: Optional[int] = None
    citizenFeedbackRating: Optional[int] = None
    citizen_comment: Optional[str] = None
    citizenFeedbackComment: Optional[str] = None
    ai_verification_confidence: float = 0.950
    aiVerificationConfidence: float = 0.950
    verified_by_admin: bool = False
    verifiedByAdmin: bool = False


# ---------------------------------------------------------------------------
# Grievance Request Schemas
# ---------------------------------------------------------------------------
class GrievanceCreateRequest(BaseModel):
    title: str = Field(..., min_length=5, max_length=300)
    description: str = Field(..., min_length=10, max_length=10000)
    category: str = Field(..., min_length=2, max_length=150)
    subcategory: Optional[str] = Field("General Civic Issue", max_length=150)
    department_id: Optional[str] = Field(None, max_length=50)
    priority: Optional[GrievancePriorityType] = "medium"
    address: str = Field(..., min_length=3, max_length=350)
    ward: str = Field(..., min_length=1, max_length=100)
    zone: str = Field(..., min_length=1, max_length=100)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    is_anonymous: bool = False
    language: str = Field("en", max_length=10)
    evidence_file_ids: List[uuid.UUID] = Field(default_factory=list)


class GrievanceStatusTransitionRequest(BaseModel):
    status: GrievanceStatusType
    notes: Optional[str] = Field(None, max_length=2000)


class GrievanceReassignRequest(BaseModel):
    department_id: Optional[str] = Field(None, max_length=50)
    officer_id: Optional[uuid.UUID] = None
    reason: Optional[str] = Field(None, max_length=1000)


class CitizenResolutionVerifyRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=2000)
    action: Literal["accept", "reject"] = "accept"


class GrievanceAppealRequest(BaseModel):
    reason: str = Field(..., min_length=10, max_length=3000)
    evidence_file_ids: List[uuid.UUID] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Grievance Full Response Schema
# ---------------------------------------------------------------------------
class GrievanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    title: str
    description: str
    citizen_id: str
    citizenId: str
    citizen_name: str
    citizenName: str
    citizen_phone: Optional[str] = None
    citizenPhone: Optional[str] = None
    category: str
    subcategory: str
    department_id: str
    departmentId: str
    department_name: str
    departmentName: str
    assigned_officer_id: Optional[str] = None
    assignedOfficerId: Optional[str] = None
    assigned_officer_name: Optional[str] = None
    assignedOfficerName: Optional[str] = None
    location: GrievanceLocationSchema
    priority: GrievancePriorityType
    status: GrievanceStatusType
    ai_confidence: float
    aiConfidence: float
    submitted_at: datetime
    submittedAt: datetime
    updated_at: datetime
    updatedAt: datetime
    expected_resolution_date: datetime
    expectedResolutionDate: datetime
    actual_resolution_date: Optional[datetime] = None
    actualResolutionDate: Optional[datetime] = None
    sla_deadline: datetime
    slaDeadline: datetime
    sla_breached: bool
    slaBreached: bool
    sla_breach_risk: SlaBreachRiskType
    slaBreachRisk: SlaBreachRiskType
    duplicate_probability: float
    duplicateProbability: float
    duplicate_cluster_id: Optional[str] = None
    duplicateClusterId: Optional[str] = None
    is_anonymous: bool
    isAnonymous: bool
    language: str
    predicted_duration_days: float
    predictedDurationDays: float
    evidence: List[EvidenceResponse] = Field(default_factory=list)
    timeline: List[TimelineEventResponse] = Field(default_factory=list)
    resolution_report: Optional[ResolutionReportResponse] = None
    resolutionReport: Optional[ResolutionReportResponse] = None


class GrievanceListResponse(BaseModel):
    items: List[GrievanceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ---------------------------------------------------------------------------
# Triage Preview Schema (Deterministic Rule-Based Fallback)
# ---------------------------------------------------------------------------
class TriagePreviewRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=300)
    description: str = Field(..., min_length=5, max_length=10000)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None


class TriagePreviewResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    predicted_category: str
    predictedCategory: str
    predicted_subcategory: str
    predictedSubcategory: str
    suggested_department_id: str
    suggestedDepartmentId: str
    suggested_department_name: str
    suggestedDepartmentName: str
    priority: GrievancePriorityType
    confidence: float
    predicted_duration_days: float
    predictedDurationDays: float
    is_mock_fallback: bool = True
    isMockFallback: bool = True
    keywords_matched: List[str] = Field(default_factory=list)
    keywordsMatched: List[str] = Field(default_factory=list)
    confidence_interval_low: Optional[float] = None
    confidence_interval_high: Optional[float] = None
    sla_breach_risk: Optional[str] = None
    slaBreachRisk: Optional[str] = None
    sla_breach_probability: Optional[float] = None
    slaBreachProbability: Optional[float] = None
    shap_factors: Optional[List[Dict[str, Any]]] = None
    shapFactors: Optional[List[Dict[str, Any]]] = None
    token_attributions: Optional[List[Dict[str, Any]]] = None
    model_metadata: Optional[Dict[str, Any]] = None
