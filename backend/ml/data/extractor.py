"""
CivicMind AI — Database Extractor & Dataset Readiness Audit
Extracts operational data from PostgreSQL and assesses production readiness.
If production data fails the readiness gate, gracefully falls back to the
curated municipal benchmark dataset with explicit traceability.
"""

from typing import Dict, Any, Tuple, Optional
import pandas as pd
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_sync_db
from app.models.grievance import Grievance
from app.models.resolution import ResolutionReport
from ml.data.benchmark_dataset import BENCHMARK_RESEARCH_DATASET_v1
from ml.data.normalization import clean_text, combine_title_description


MIN_SAMPLE_THRESHOLD = 50
MIN_RESOLVED_THRESHOLD = 30


class DatasetReadinessReport:
    def __init__(
        self,
        total_grievances: int,
        resolved_count: int,
        sla_breached_count: int,
        is_ready: bool,
        reason: str,
        source: str,
    ):
        self.total_grievances = total_grievances
        self.resolved_count = resolved_count
        self.sla_breached_count = sla_breached_count
        self.is_ready = is_ready
        self.reason = reason
        self.source = source

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_grievances": self.total_grievances,
            "resolved_count": self.resolved_count,
            "sla_breached_count": self.sla_breached_count,
            "is_ready": self.is_ready,
            "reason": self.reason,
            "source": self.source,
        }


def audit_production_dataset_sync() -> DatasetReadinessReport:
    """
    Performs an empirical census on PostgreSQL tables to evaluate ML readiness.
    Checks:
    1. Total grievance volume >= MIN_SAMPLE_THRESHOLD
    2. Resolution completion volume >= MIN_RESOLVED_THRESHOLD
    3. Outcome variance (both breached and unbreached cases exist)
    """
    with get_sync_db() as session:
        total_count = session.execute(select(func.count(Grievance.id))).scalar() or 0
        resolved_count = (
            session.execute(
                select(func.count(Grievance.id)).where(Grievance.status.in_(["closed", "citizen_verified", "resolution_submitted"]))
            ).scalar()
            or 0
        )
        breached_count = (
            session.execute(
                select(func.count(Grievance.id)).where(Grievance.sla_breached == True)
            ).scalar()
            or 0
        )

    if total_count < MIN_SAMPLE_THRESHOLD:
        return DatasetReadinessReport(
            total_grievances=total_count,
            resolved_count=resolved_count,
            sla_breached_count=breached_count,
            is_ready=False,
            reason=f"Insufficient sample count ({total_count} < {MIN_SAMPLE_THRESHOLD}). Production system is in early cold-start stage.",
            source="postgres_operational_insufficient",
        )

    if resolved_count < MIN_RESOLVED_THRESHOLD:
        return DatasetReadinessReport(
            total_grievances=total_count,
            resolved_count=resolved_count,
            sla_breached_count=breached_count,
            is_ready=False,
            reason=f"Insufficient completed resolutions ({resolved_count} < {MIN_RESOLVED_THRESHOLD}) to supervise duration regression.",
            source="postgres_operational_insufficient",
        )

    if breached_count == 0 or breached_count == resolved_count:
        return DatasetReadinessReport(
            total_grievances=total_count,
            resolved_count=resolved_count,
            sla_breached_count=breached_count,
            is_ready=False,
            reason="Zero outcome variance in SLA breach labels. Binary classification requires both positive and negative cases.",
            source="postgres_operational_insufficient",
        )

    return DatasetReadinessReport(
        total_grievances=total_count,
        resolved_count=resolved_count,
        sla_breached_count=breached_count,
        is_ready=True,
        reason="Operational database meets empirical readiness thresholds for training.",
        source="postgres_operational",
    )


def load_dataset_for_training(force_benchmark: bool = False) -> Tuple[pd.DataFrame, DatasetReadinessReport]:
    """
    Loads dataset for ML training and benchmarking.
    If production data is insufficient or force_benchmark=True, returns BENCHMARK_RESEARCH_DATASET_v1.
    """
    audit = audit_production_dataset_sync()

    if force_benchmark or not audit.is_ready:
        df = BENCHMARK_RESEARCH_DATASET_v1.copy()
        audit.source = "benchmark_research_v1"
        return df, audit

    # If production data is sufficient, extract it
    with get_sync_db() as session:
        grievances = session.execute(select(Grievance)).scalars().all()

        records = []
        for g in grievances:
            records.append({
                "id": g.id,
                "title": g.title,
                "description": g.description,
                "category": g.category,
                "subcategory": g.subcategory,
                "department_id": g.department_id,
                "department_name": g.category,  # fallback
                "priority": g.priority,
                "ward": g.ward,
                "zone": g.zone,
                "latitude": g.latitude,
                "longitude": g.longitude,
                "submitted_at": g.submitted_at.isoformat() if g.submitted_at else "",
                "expected_duration_days": float(g.predicted_duration_days or 3.0),
                "actual_duration_days": float(g.predicted_duration_days or 3.0),
                "sla_hours": 72,
                "sla_breached": g.sla_breached,
                "full_text": combine_title_description(g.title, g.description),
            })

    df = pd.DataFrame(records)
    return df, audit
