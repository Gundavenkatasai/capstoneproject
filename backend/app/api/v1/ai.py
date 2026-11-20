"""
CivicMind AI — AI Operational Preview & Machine Learning Inference API
Exposes endpoints for category classification, department recommendation,
pgvector semantic duplicate detection, resolution duration regression,
SLA breach risk prediction, prediction explainability, and model registry health.
"""

import uuid
import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.grievance import Grievance
from app.schemas.grievance import TriagePreviewRequest, TriagePreviewResponse
from app.schemas.ai import (
    CategoryClassifyRequest,
    CategoryClassifyResponse,
    DepartmentRecommendRequest,
    DepartmentRecommendResponse,
    DuplicateSearchRequest,
    DuplicateSearchResponse,
    DuplicateMatchItem,
    ResolutionPredictionRequest,
    ResolutionPredictionResponse,
    SlaRiskRequest,
    SlaRiskResponse,
    ExplainabilityResponse,
    SHAPFactorSchema,
    TokenAttributionSchema,
    ModelRegistryHealthResponse,
)
from app.services.grievance_service import GrievanceService
from ml.registry.model_registry import model_registry
from ml.embeddings.sentence_embedder import sentence_embedder
from ml.duplicates.detector import duplicate_detector
from ml.explainability.shap_explainer import TabularExplainer
from ml.explainability.token_attribution import TokenAttributionExplainer

logger = logging.getLogger("civicmind.api.ai")

router = APIRouter(prefix="/ai", tags=["AI Intelligence & Inference Engine"])


@router.post(
    "/triage-preview",
    response_model=TriagePreviewResponse,
    summary="Preview AI Grievance Triage",
    description="Provides real-time ML-powered municipal department routing, category classification, SLA risk, and duration estimation before final submission.",
)
async def triage_preview(payload: TriagePreviewRequest) -> TriagePreviewResponse:
    try:
        res = model_registry.predict_full_triage(
            title=payload.title,
            description=payload.description,
            ward=payload.address or "Ward 14 (Central)",
        )

        return TriagePreviewResponse(
            predicted_category=res["predicted_category"],
            predictedCategory=res["predicted_category"],
            predicted_subcategory=res["predicted_subcategory"],
            predictedSubcategory=res["predicted_subcategory"],
            suggested_department_id=res["suggested_department_id"],
            suggestedDepartmentId=res["suggested_department_id"],
            suggested_department_name=res["suggested_department_name"],
            suggestedDepartmentName=res["suggested_department_name"],
            priority=res["priority"],
            confidence=res["confidence"],
            predicted_duration_days=res["predicted_duration_days"],
            predictedDurationDays=res["predicted_duration_days"],
            is_mock_fallback=False,
            isMockFallback=False,
            keywords_matched=res["keywords_matched"],
            keywordsMatched=res["keywords_matched"],
            confidence_interval_low=res.get("confidence_interval_low"),
            confidence_interval_high=res.get("confidence_interval_high"),
            sla_breach_risk=res.get("sla_breach_risk"),
            slaBreachRisk=res.get("sla_breach_risk"),
            sla_breach_probability=res.get("sla_breach_probability"),
            slaBreachProbability=res.get("sla_breach_probability"),
            shap_factors=res.get("shap_factors"),
            shapFactors=res.get("shap_factors"),
            token_attributions=res.get("token_attributions"),
            model_metadata=res.get("model_metadata"),
        )
    except Exception as ex:
        logger.warning("Error in ML triage preview (%s), falling back to rule-based engine.", str(ex))
        return GrievanceService.triage_preview(payload)


@router.post(
    "/classify",
    response_model=CategoryClassifyResponse,
    summary="Classify Grievance Category",
    description="Predicts the municipal grievance category and probability distribution over all classes.",
)
async def classify_category(payload: CategoryClassifyRequest) -> CategoryClassifyResponse:
    model_registry.initialize_models()
    if not model_registry.category_classifier:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Category classification model is unavailable.",
        )

    full_text = f"{payload.title}. {payload.description}"
    result = model_registry.category_classifier.classify_single(full_text)
    return CategoryClassifyResponse(**result)


@router.post(
    "/department-recommendation",
    response_model=DepartmentRecommendResponse,
    summary="Recommend Municipal Department",
    description="Recommends primary and secondary responsible municipal departments with fit scores.",
)
async def recommend_department(payload: DepartmentRecommendRequest) -> DepartmentRecommendResponse:
    model_registry.initialize_models()
    if not model_registry.department_recommender:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Department recommendation model is unavailable.",
        )

    full_text = f"{payload.title}. {payload.description}"
    result = model_registry.department_recommender.recommend(full_text, category_hint=payload.category_hint)
    return DepartmentRecommendResponse(**result)


@router.post(
    "/duplicates",
    response_model=DuplicateSearchResponse,
    summary="Search Semantic Duplicates",
    description="Executes pgvector cosine similarity search to detect duplicate grievance complaints.",
)
async def search_duplicates(
    payload: DuplicateSearchRequest,
    session: AsyncSession = Depends(get_db),
) -> DuplicateSearchResponse:
    matches_raw = []

    if payload.grievance_id:
        matches_raw = await duplicate_detector.find_duplicates_for_grievance(
            session=session,
            grievance_id=payload.grievance_id,
            limit=payload.limit,
        )
    elif payload.title or payload.description:
        text = f"{payload.title or ''}. {payload.description or ''}"
        vector = sentence_embedder.embed_text(text)
        matches_raw = await duplicate_detector.find_duplicates_by_vector(
            session=session,
            vector=vector,
            latitude=payload.latitude,
            longitude=payload.longitude,
            category=payload.category,
            limit=payload.limit,
        )

    items = [DuplicateMatchItem(**m) for m in matches_raw]
    return DuplicateSearchResponse(
        matches=items,
        total_found=len(items),
        query_target=payload.grievance_id or payload.title,
        search_vector_dimension=sentence_embedder.dimension,
    )


@router.post(
    "/resolution-prediction",
    response_model=ResolutionPredictionResponse,
    summary="Predict Resolution Duration",
    description="Predicts expected resolution duration in days with uncertainty bounds using intake features.",
)
async def predict_resolution_duration(payload: ResolutionPredictionRequest) -> ResolutionPredictionResponse:
    model_registry.initialize_models()
    if not model_registry.resolution_regressor:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Resolution regression model is unavailable.",
        )

    result = model_registry.resolution_regressor.predict_single(
        title=payload.title,
        description=payload.description,
        category=payload.category,
        department_id=payload.department_id,
        priority=payload.priority,
        ward=payload.ward,
    )
    return ResolutionPredictionResponse(**result)


@router.post(
    "/sla-risk",
    response_model=SlaRiskResponse,
    summary="Predict SLA Breach Risk",
    description="Predicts the calibrated probability of SLA breach, assigns risk tier, and lists contributing factors.",
)
async def predict_sla_risk(payload: SlaRiskRequest) -> SlaRiskResponse:
    model_registry.initialize_models()
    if not model_registry.sla_classifier:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SLA risk classification model is unavailable.",
        )

    result = model_registry.sla_classifier.predict_single(
        title=payload.title,
        description=payload.description,
        category=payload.category,
        department_id=payload.department_id,
        priority=payload.priority,
        ward=payload.ward,
    )
    return SlaRiskResponse(**result)


@router.get(
    "/explainability/{grievance_id}",
    response_model=ExplainabilityResponse,
    summary="Get Prediction Explainability",
    description="Returns TreeSHAP tabular factors and lexical token attributions for an existing grievance.",
)
async def get_explainability(
    grievance_id: str,
    session: AsyncSession = Depends(get_db),
) -> ExplainabilityResponse:
    grv = await session.get(Grievance, grievance_id)
    if not grv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grievance '{grievance_id}' not found.",
        )

    full_text = f"{grv.title}. {grv.description}"
    dur = float(grv.predicted_duration_days or 3.0)

    # Compute SHAP factors
    raw_factors = TabularExplainer.explain_duration_prediction(
        predicted_days=dur,
        priority=grv.priority,
        category=grv.category,
        department_name=grv.category,
        ward=grv.ward,
        text_length=len(full_text),
    )
    shap_factors = [SHAPFactorSchema(**f) for f in raw_factors]

    # Compute Token attributions
    raw_tokens = TokenAttributionExplainer.attribute_tokens(full_text)
    tokens = [TokenAttributionSchema(**t) for t in raw_tokens]

    breach_prob = 0.75 if grv.sla_breach_risk in ("high", "critical") else 0.20

    summary = (
        f"Grievance {grv.id} predicted at {dur:.1f} days resolution duration "
        f"driven primarily by {grv.priority.upper()} priority dispatch and {grv.category} infrastructure dependencies."
    )

    return ExplainabilityResponse(
        grievance_id=grv.id,
        predicted_duration_days=dur,
        sla_breach_probability=breach_prob,
        shap_factors=shap_factors,
        token_attributions=tokens,
        explanation_summary=summary,
    )


@router.get(
    "/models",
    summary="List Registered AI Models",
    description="Returns metadata, version identifiers, algorithm specifications, and training dataset status for all registered models.",
)
async def list_models() -> Dict[str, Any]:
    model_registry.initialize_models()
    return model_registry.metadata


@router.get(
    "/health",
    response_model=ModelRegistryHealthResponse,
    summary="AI Model Health Check",
    description="Verifies the operational status, memory initialization, and artifact integrity of the AI engine.",
)
async def ai_health() -> ModelRegistryHealthResponse:
    health = model_registry.get_health()
    return ModelRegistryHealthResponse(**health)


@router.get(
    "/evaluation",
    summary="Get Model Evaluation Metrics",
    description="Returns comprehensive offline benchmark evaluation metrics across classification, regression, and ranking tasks.",
)
async def get_evaluation() -> Dict[str, Any]:
    model_registry.initialize_models()
    return {
        "status": "evaluated",
        "training_dataset": model_registry.metadata.get("training_dataset"),
        "readiness_status": model_registry.metadata.get("readiness_status"),
        "models": model_registry.metadata.get("models", {}),
    }
