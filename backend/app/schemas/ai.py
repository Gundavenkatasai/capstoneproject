"""
CivicMind AI — Machine Learning API Schemas
Pydantic v2 validation contracts for all Phase 5 AI intelligence endpoints.
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class SHAPFactorSchema(BaseModel):
    feature: str
    weight: float
    effect: Literal["positive", "negative"]
    description: str


class TokenAttributionSchema(BaseModel):
    token: str
    importance: float
    is_salient: bool = False


# 1. Classification
class CategoryClassifyRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=300)
    description: str = Field(..., min_length=5, max_length=10000)


class CategoryClassifyResponse(BaseModel):
    predicted_category: str
    confidence: float
    probabilities: Dict[str, float] = Field(default_factory=dict)
    is_fallback: bool = False
    model_version: str = "v1.0.0"


# 2. Department Recommendation
class DepartmentRecommendRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=300)
    description: str = Field(..., min_length=5, max_length=10000)
    category_hint: Optional[str] = None


class DepartmentRecommendResponse(BaseModel):
    recommended_department_id: str
    recommended_department_name: str
    confidence: float
    second_choice_id: Optional[str] = None
    second_choice_name: Optional[str] = None
    department_fit_score: float
    is_fallback: bool = False
    model_version: str = "v1.0.0"


# 3. Duplicate Search
class DuplicateSearchRequest(BaseModel):
    grievance_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category: Optional[str] = None
    similarity_threshold: float = Field(0.82, ge=0.5, le=1.0)
    limit: int = Field(5, ge=1, le=20)


class DuplicateMatchItem(BaseModel):
    grievance_id: str
    title: str
    category: str
    ward: Optional[str] = None
    status: Optional[str] = None
    similarity_score: float
    proximity_meters: float = 0.0
    ai_recommendation: str
    reason: str


class DuplicateSearchResponse(BaseModel):
    matches: List[DuplicateMatchItem] = Field(default_factory=list)
    total_found: int = 0
    query_target: Optional[str] = None
    search_vector_dimension: int = 768


# 4. Resolution Time Prediction
class ResolutionPredictionRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=300)
    description: str = Field(..., min_length=5, max_length=10000)
    category: str = Field("Road Infrastructure", max_length=150)
    department_id: str = Field("dept_pwd", max_length=50)
    priority: str = Field("medium", max_length=20)
    ward: str = Field("Ward 14 (Central)", max_length=100)


class ResolutionPredictionResponse(BaseModel):
    predicted_duration_days: float
    confidence_interval_low: float
    confidence_interval_high: float
    is_fallback: bool = False
    model_version: str = "v1.0.0"


# 5. SLA Breach Risk Prediction
class SlaRiskRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=300)
    description: str = Field(..., min_length=5, max_length=10000)
    category: str = Field("Road Infrastructure", max_length=150)
    department_id: str = Field("dept_pwd", max_length=50)
    priority: str = Field("medium", max_length=20)
    ward: str = Field("Ward 14 (Central)", max_length=100)


class SlaRiskResponse(BaseModel):
    breach_probability: float
    risk_tier: Literal["low", "medium", "high", "critical"]
    is_at_risk: bool
    contributing_factors: List[str] = Field(default_factory=list)
    recommended_action: str
    is_fallback: bool = False
    model_version: str = "v1.0.0"


# 6. Explainability
class ExplainabilityResponse(BaseModel):
    grievance_id: str
    predicted_duration_days: float
    sla_breach_probability: float
    shap_factors: List[SHAPFactorSchema] = Field(default_factory=list)
    token_attributions: List[TokenAttributionSchema] = Field(default_factory=list)
    explanation_summary: str


# 7. Model Registry & Health
class ModelRegistryHealthResponse(BaseModel):
    status: str
    is_initialized: bool
    readiness_status: str
    models_loaded: Dict[str, bool]
    embedding_dimension: int
    artifacts_directory: str
    last_trained_at: Optional[str] = None
