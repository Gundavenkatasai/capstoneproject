"""
CivicMind AI — Machine Learning Intelligence & Inference Engine Tests
Phase 5 Test Suite: Dataset readiness, leak-free splits, 768-dim embeddings,
classification, department routing, duration regression, SLA risk, explainability,
duplicate detection, Celery tasks, and AI API endpoints.
"""

import uuid
from datetime import datetime, timezone, timedelta
import pytest
import numpy as np
from httpx import AsyncClient
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_sync_db
from app.models.grievance import Grievance
from app.models.department import Department
from app.models.user import User
from app.models.embedding import GrievanceEmbedding
from app.models.duplicate import DuplicateCluster

from ml.data.benchmark_dataset import BENCHMARK_RESEARCH_DATASET_v1
from ml.data.extractor import audit_production_dataset_sync
from ml.data.splitting import temporal_split, stratified_split, verify_no_split_leakage
from ml.embeddings.sentence_embedder import sentence_embedder
from ml.duplicates.detector import DuplicateDetector, cosine_similarity
from ml.classification.category_classifier import CategoryClassifier
from ml.classification.department_recommender import DepartmentRecommender
from ml.resolution.regressor import ResolutionRegressor
from ml.sla.classifier import SlaRiskClassifier
from ml.explainability.shap_explainer import TabularExplainer
from ml.explainability.token_attribution import TokenAttributionExplainer
from ml.registry.model_registry import model_registry
from app.tasks.ml import generate_grievance_embedding_task, detect_duplicate_grievances_task


def test_data_readiness_audit_empirical():
    """
    Validates empirical dataset readiness gate.
    With only test fixtures in the database, the gate must honestly report insufficient_data.
    """
    audit = audit_production_dataset_sync()
    assert audit.total_grievances >= 0
    # Since operational completions are 0, it must NOT be marked ready
    assert audit.is_ready is False
    assert "Insufficient" in audit.reason or "cold-start" in audit.reason or "variance" in audit.reason
    assert "postgres_operational_insufficient" in audit.source


def test_dataset_splitting_leak_free():
    """
    Validates that temporal and stratified dataset splits prevent data leakage across partitions.
    """
    df = BENCHMARK_RESEARCH_DATASET_v1.copy()

    # Temporal split
    train_t, val_t, test_t = temporal_split(df, test_size=0.2, val_size=0.1)
    assert len(train_t) > len(val_t)
    assert len(train_t) > len(test_t)
    leakage_t = verify_no_split_leakage(train_t, test_t)
    assert leakage_t["leakage_detected"] is False
    assert leakage_t["id_overlap_count"] == 0

    # Stratified split
    train_s, val_s, test_s = stratified_split(df, stratify_col="category", test_size=0.2, val_size=0.1)
    assert len(train_s) > 0 and len(test_s) > 0
    leakage_s = verify_no_split_leakage(train_s, test_s)
    assert leakage_s["leakage_detected"] is False
    assert leakage_s["id_overlap_count"] == 0


def test_768_dim_dense_embedding_invariant():
    """
    Strict architectural invariant: Vector embeddings MUST have exactly 768 dimensions
    to match the PostgreSQL pgvector vector(768) schema definition.
    """
    text = "Severe deep pothole causing vehicle tire damage near Metro Station"
    vec = sentence_embedder.embed_text(text)

    # 1. Dimension invariant
    assert len(vec) == 768, f"Expected 768 dimensions, got {len(vec)}"
    assert len(vec) == settings.EMBEDDING_DIMENSION

    # 2. Type invariant
    assert isinstance(vec[0], float)

    # 3. Batch encoding invariant
    batch = ["Pothole on main road", "Garbage dump overflowing"]
    vectors = sentence_embedder.embed_batch(batch)
    assert len(vectors) == 2
    assert len(vectors[0]) == 768
    assert len(vectors[1]) == 768

    # 4. Semantic similarity: similar municipal issues have higher similarity than unrelated issues
    v_pothole = sentence_embedder.embed_text("Deep pothole crater on tarmac road")
    v_crater = sentence_embedder.embed_text("Road surface collapsed with dangerous cavity")
    v_tax = sentence_embedder.embed_text("Discrepancy in property tax online assessment calculation")

    sim_related = cosine_similarity(v_pothole, v_crater)
    sim_unrelated = cosine_similarity(v_pothole, v_tax)

    assert sim_related > sim_unrelated, f"Expected related ({sim_related}) > unrelated ({sim_unrelated})"


def test_category_classifier_inference():
    """
    Validates category classifier predicts one of the 8 standard municipal categories
    with confidence scores and calibrated class probabilities.
    """
    model_registry.initialize_models()
    clf = model_registry.category_classifier
    assert clf is not None

    res = clf.classify_single("Garbage bin overflowing with rotten waste attracting stray animals")
    assert res["predicted_category"] == "Sanitation & Waste Management"
    assert 0.0 <= res["confidence"] <= 1.0
    assert len(res["probabilities"]) == 8
    assert sum(res["probabilities"].values()) == pytest.approx(1.0, abs=0.01)


def test_department_recommender_inference():
    """
    Validates department recommender routes grievances to the correct municipal entity
    and identifies secondary fallback departments.
    """
    model_registry.initialize_models()
    dept_rec = model_registry.department_recommender
    assert dept_rec is not None

    res = dept_rec.recommend("Water supply pipeline ruptured flooding drinking water into drain")
    assert res["recommended_department_id"] == "dept_wssb"
    assert "Water" in res["recommended_department_name"]
    assert 0.0 <= res["confidence"] <= 1.0
    assert res["second_choice_id"] is not None


def test_resolution_duration_regressor_bounds():
    """
    Validates that predicted duration is strictly positive and non-zero [0.5, 30.0 days],
    and uncertainty intervals are properly ordered.
    """
    model_registry.initialize_models()
    reg = model_registry.resolution_regressor
    assert reg is not None

    crit_res = reg.predict_single(
        title="Live high voltage transformer sparking violently",
        description="Transformer blowing sparks over children playground in residential sector",
        category="Urban Electricity & Street Lighting",
        department_id="dept_electricity",
        priority="critical",
        ward="Ward 14 (Central)",
    )

    assert 0.5 <= crit_res["predicted_duration_days"] <= 30.0
    assert crit_res["confidence_interval_low"] < crit_res["confidence_interval_high"]
    assert crit_res["confidence_interval_low"] >= 0.5

    # Low priority routine issue should have equal or longer predicted duration
    low_res = reg.predict_single(
        title="Paver blocks on garden walkway slightly loose",
        description="Few decorative paver stones in park have minor gaps",
        category="Parks & Horticulture",
        department_id="dept_horticulture",
        priority="low",
        ward="Ward 56 (Jayanagar)",
    )
    assert low_res["predicted_duration_days"] >= crit_res["predicted_duration_days"]


def test_sla_breach_risk_classifier():
    """
    Validates SLA breach probability prediction and risk tier assignment.
    """
    model_registry.initialize_models()
    sla = model_registry.sla_classifier
    assert sla is not None

    res = sla.predict_single(
        title="Hazardous open drain during monsoon storm",
        description="Huge open culvert overflowing onto main avenue creating death trap",
        category="Water Supply & Drainage",
        department_id="dept_wssb",
        priority="critical",
        ward="Ward 14 (Central)",
    )

    assert 0.0 <= res["breach_probability"] <= 1.0
    assert res["risk_tier"] in ("low", "medium", "high", "critical")
    assert isinstance(res["is_at_risk"], bool)
    assert len(res["contributing_factors"]) > 0
    assert len(res["recommended_action"]) > 0


def test_duplicate_detector_in_memory():
    """
    Validates semantic duplicate discovery and non-destructive clustering logic.
    """
    detector = DuplicateDetector(similarity_threshold=0.80, max_proximity_meters=1000.0)

    candidates = [
        {
            "id": "GRV-EXISTING-001",
            "title": "Severe road pothole on 80ft Road Koramangala",
            "description": "Deep hole near 4th block signal causing traffic jam and bike falls",
            "category": "Road Infrastructure",
            "latitude": 12.9352,
            "longitude": 77.6245,
        },
        {
            "id": "GRV-EXISTING-002",
            "title": "Unpaid property tax receipt not downloaded",
            "description": "Challan paid but receipt is not generating on municipal portal",
            "category": "Revenue & Property Tax",
            "latitude": 12.9716,
            "longitude": 77.5946,
        },
    ]

    matches = detector.find_in_memory_duplicates(
        query_text="Severe road pothole on 80ft Road Koramangala near signal causing bike falls",
        query_lat=12.9353,
        query_lng=77.6246,
        candidates=candidates,
        limit=5,
    )

    assert len(matches) >= 1
    top = matches[0]
    assert top["grievance_id"] == "GRV-EXISTING-001"
    assert top["similarity_score"] >= 0.80
    assert top["proximity_meters"] < 50.0
    assert top["ai_recommendation"] in ("merge_candidate", "potential_duplicate")


def test_explainability_tabular_and_tokens():
    """
    Validates SHAP factor explanations and token-level lexical attributions.
    """
    # Tabular explanations
    shap_factors = TabularExplainer.explain_duration_prediction(
        predicted_days=2.5,
        priority="critical",
        category="Road Infrastructure",
        department_name="Public Works Department (PWD)",
        ward="Ward 14 (Central)",
        text_length=150,
    )
    assert len(shap_factors) >= 3
    for f in shap_factors:
        assert "feature" in f
        assert "weight" in f
        assert f["effect"] in ("positive", "negative")
        assert len(f["description"]) > 0

    # Token attributions
    text = "Massive pothole crater on road near bridge"
    tokens = TokenAttributionExplainer.attribute_tokens(text)
    assert len(tokens) > 0
    token_words = [t["token"] for t in tokens]
    assert any(w in token_words for w in ["pothole", "crater", "road", "bridge"])


def test_model_registry_health_and_triage():
    """
    Validates that model registry initializes cleanly, reports health, and produces full triage.
    """
    health = model_registry.get_health()
    assert health["status"] == "healthy"
    assert health["is_initialized"] is True
    assert health["embedding_dimension"] == 768
    assert health["models_loaded"]["category_classifier"] is True
    assert health["models_loaded"]["department_recommender"] is True
    assert health["models_loaded"]["resolution_regressor"] is True
    assert health["models_loaded"]["sla_classifier"] is True

    triage = model_registry.predict_full_triage(
        title="Dangling electrical wire touching pedestrian sidewalk",
        description="High tension line broken and sparking near apartment entrance gate",
        ward="Ward 14 (Central)",
    )

    assert triage["predicted_category"] == "Urban Electricity & Street Lighting"
    assert triage["suggested_department_id"] == "dept_electricity"
    assert triage["priority"] in ("critical", "high")
    assert 0.5 <= triage["predicted_duration_days"] <= 30.0
    assert len(triage["shap_factors"]) > 0
    assert len(triage["token_attributions"]) > 0


@pytest.mark.asyncio
async def test_ai_api_triage_preview_endpoint(client: AsyncClient):
    """
    Tests POST /api/v1/ai/triage-preview returns complete ML metadata and dual-case fields.
    """
    payload = {
        "title": "Severe sewage overflow flooding residential lane",
        "description": "Black foul water overflowing from municipal main drain into homes for 3 days",
        "address": "Ward 14 (Central)",
    }
    response = await client.post("/api/v1/ai/triage-preview", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["predictedCategory"] == "Water Supply & Drainage"
    assert data["suggestedDepartmentId"] == "dept_wssb"
    assert data["priority"] in ("critical", "high", "medium")
    assert data["predictedDurationDays"] > 0
    assert data["isMockFallback"] is False
    assert len(data["keywordsMatched"]) > 0
    assert "shap_factors" in data or "shapFactors" in data


@pytest.mark.asyncio
async def test_ai_api_classify_and_recommend(client: AsyncClient):
    """
    Tests POST /api/v1/ai/classify and POST /api/v1/ai/department-recommendation.
    """
    # 1. Classify
    c_res = await client.post(
        "/api/v1/ai/classify",
        json={"title": "Massive road pothole", "description": "Deep asphalt crater on road causing bike skids"},
    )
    assert c_res.status_code == 200
    c_data = c_res.json()
    assert c_data["predicted_category"] == "Road Infrastructure"
    assert c_data["confidence"] > 0.0

    # 2. Recommend Department
    d_res = await client.post(
        "/api/v1/ai/department-recommendation",
        json={"title": "Rotting street garbage", "description": "Garbage dump uncollected for five days"},
    )
    assert d_res.status_code == 200
    d_data = d_res.json()
    assert d_data["recommended_department_id"] == "dept_sanitation"
    assert d_data["confidence"] > 0.0


@pytest.mark.asyncio
async def test_ai_api_resolution_and_sla_risk(client: AsyncClient):
    """
    Tests POST /api/v1/ai/resolution-prediction and POST /api/v1/ai/sla-risk.
    """
    # Resolution prediction
    r_res = await client.post(
        "/api/v1/ai/resolution-prediction",
        json={
            "title": "Deep road crater",
            "description": "Hazardous road collapse requiring tar mix",
            "category": "Road Infrastructure",
            "department_id": "dept_pwd",
            "priority": "high",
            "ward": "Ward 14 (Central)",
        },
    )
    assert r_res.status_code == 200
    r_data = r_res.json()
    assert 0.5 <= r_data["predicted_duration_days"] <= 30.0

    # SLA risk prediction
    s_res = await client.post(
        "/api/v1/ai/sla-risk",
        json={
            "title": "Deep road crater",
            "description": "Hazardous road collapse requiring tar mix",
            "category": "Road Infrastructure",
            "department_id": "dept_pwd",
            "priority": "critical",
            "ward": "Ward 14 (Central)",
        },
    )
    assert s_res.status_code == 200
    s_data = s_res.json()
    assert 0.0 <= s_data["breach_probability"] <= 1.0
    assert s_data["risk_tier"] in ("low", "medium", "high", "critical")


@pytest.mark.asyncio
async def test_ai_api_models_health_evaluation(client: AsyncClient):
    """
    Tests GET /api/v1/ai/models, GET /api/v1/ai/health, and GET /api/v1/ai/evaluation.
    """
    # 1. Health
    h_res = await client.get("/api/v1/ai/health")
    assert h_res.status_code == 200
    h_data = h_res.json()
    assert h_data["status"] == "healthy"
    assert h_data["embedding_dimension"] == 768

    # 2. Models metadata
    m_res = await client.get("/api/v1/ai/models")
    assert m_res.status_code == 200
    m_data = m_res.json()
    assert "models" in m_data
    assert "category_classifier" in m_data["models"]
    assert "resolution_regressor" in m_data["models"]

    # 3. Evaluation
    e_res = await client.get("/api/v1/ai/evaluation")
    assert e_res.status_code == 200
    e_data = e_res.json()
    assert e_data["status"] == "evaluated"
    assert "category_classifier" in e_data["models"]


def test_celery_ml_tasks_execution():
    """
    Tests synchronous execution of generate_grievance_embedding_task
    and verifies that a 768-dimensional vector is persisted in PostgreSQL pgvector.
    """
    # 1. Ensure test department and user exist
    test_gid = f"GRV-TEST-{uuid.uuid4().hex[:6].upper()}"

    with get_sync_db() as session:
        dept = session.get(Department, "dept_pwd")
        if not dept:
            dept = Department(
                id="dept_pwd",
                code="PWD-RDS",
                name="Public Works Department",
                head_name="Chief Engineer",
            )
            session.add(dept)

        user = session.execute(select(User).where(User.role == "citizen")).scalars().first()
        if not user:
            user = User(
                id=uuid.uuid4(),
                email=f"test_ml_{uuid.uuid4().hex[:4]}@civicmind.gov",
                password_hash="test_hash",
                name="ML Test Citizen",
                role="citizen",
            )
            session.add(user)
            session.flush()

        now = datetime.now(timezone.utc)
        grv = Grievance(
            id=test_gid,
            title="Massive trench left open across pedestrian footpath",
            description="Contractor dug up pedestrian walkway and left it unbarricaded for a week",
            citizen_id=user.id,
            department_id="dept_pwd",
            category="Road Infrastructure",
            subcategory="Footpath & Pavements",
            priority="high",
            status="submitted",
            address="Near Metro Station Pillar 42",
            ward="Ward 14 (Central)",
            zone="Zone A (Central)",
            latitude=12.9716,
            longitude=77.5946,
            expected_resolution_date=now + timedelta(days=3),
            sla_deadline=now + timedelta(hours=72),
        )
        session.add(grv)
        session.commit()

    # 2. Execute embedding task
    res = generate_grievance_embedding_task(test_gid)
    assert res["status"] == "completed"
    assert res["dimension"] == 768

    # 3. Query PostgreSQL to verify pgvector storage
    with get_sync_db() as session:
        emb = session.get(GrievanceEmbedding, test_gid)
        assert emb is not None
        assert len(emb.embedding) == 768
        assert emb.grievance_id == test_gid

        # Cleanup
        session.delete(emb)
        grv_del = session.get(Grievance, test_gid)
        if grv_del:
            session.delete(grv_del)
        session.commit()
