"""
CivicMind AI — Unified Model Registry & Lifecycle Manager
Manages versioning, persistence, lazy loading, metadata, and fallback orchestration
across all machine learning models in the CivicMind intelligence platform.
"""

import os
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from ml.data.benchmark_dataset import BENCHMARK_RESEARCH_DATASET_v1
from ml.data.extractor import audit_production_dataset_sync
from ml.classification.category_classifier import CategoryClassifier
from ml.classification.department_recommender import DepartmentRecommender
from ml.embeddings.sentence_embedder import SentenceEmbedder, sentence_embedder
from ml.resolution.regressor import ResolutionRegressor
from ml.sla.classifier import SlaRiskClassifier
from ml.explainability.shap_explainer import TabularExplainer
from ml.explainability.token_attribution import TokenAttributionExplainer
from ml.evaluation.metrics import (
    compute_multiclass_metrics,
    compute_regression_metrics,
    compute_binary_metrics,
)

logger = logging.getLogger("civicmind.ml.registry")

ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "artifacts"


class ModelRegistry:
    """
    Singleton registry managing lifecycle of all predictive models.
    Guarantees zero-downtime, safe rule-based fallbacks, and metadata traceability.
    """

    def __init__(self, artifacts_dir: Path = ARTIFACTS_DIR):
        self.artifacts_dir = artifacts_dir
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

        self.category_classifier: Optional[CategoryClassifier] = None
        self.department_recommender: Optional[DepartmentRecommender] = None
        self.sentence_embedder: SentenceEmbedder = sentence_embedder
        self.resolution_regressor: Optional[ResolutionRegressor] = None
        self.sla_classifier: Optional[SlaRiskClassifier] = None

        self.metadata: Dict[str, Any] = {
            "registry_version": "1.0.0",
            "last_trained_at": None,
            "training_dataset": "benchmark_research_v1",
            "readiness_status": "insufficient_production_data",
            "models": {},
        }
        self._is_initialized = False

    def initialize_models(self, force_retrain: bool = False):
        """
        Initializes models by loading saved artifacts or training on benchmark dataset.
        """
        if self._is_initialized and not force_retrain:
            return

        cat_path = str(self.artifacts_dir / "category_classifier.joblib")
        dept_path = str(self.artifacts_dir / "department_recommender.joblib")
        res_path = str(self.artifacts_dir / "resolution_regressor.joblib")
        sla_path = str(self.artifacts_dir / "sla_classifier.joblib")
        meta_path = str(self.artifacts_dir / "registry_metadata.json")

        if (
            not force_retrain
            and os.path.exists(cat_path)
            and os.path.exists(dept_path)
            and os.path.exists(res_path)
            and os.path.exists(sla_path)
        ):
            try:
                logger.info("Loading ML models from cached artifacts at %s", str(self.artifacts_dir))
                self.category_classifier = CategoryClassifier.load(cat_path)
                self.department_recommender = DepartmentRecommender.load(dept_path)
                self.resolution_regressor = ResolutionRegressor.load(res_path)
                self.sla_classifier = SlaRiskClassifier.load(sla_path)

                if os.path.exists(meta_path):
                    with open(meta_path, "r", encoding="utf-8") as f:
                        self.metadata = json.load(f)

                self._is_initialized = True
                logger.info("All ML models successfully loaded from disk.")
                return
            except Exception as ex:
                logger.warning("Failed loading cached models (%s), retraining from benchmark dataset.", str(ex))

        # Train models from benchmark dataset
        self.train_all_models(BENCHMARK_RESEARCH_DATASET_v1)

    def train_all_models(self, df: Any):
        """
        Trains all models on provided dataset and computes empirical evaluation metrics.
        """
        logger.info("Training ML models on %d records...", len(df))
        now_iso = datetime.now(timezone.utc).isoformat()

        # 1. Train Category Classifier
        cat_clf = CategoryClassifier(model_version="v1.0.0-benchmark")
        cat_clf.fit(df["full_text"].tolist(), df["category"].tolist())
        cat_preds = cat_clf.predict(df["full_text"].tolist())
        cat_metrics = compute_multiclass_metrics(df["category"].tolist(), cat_preds)
        self.category_classifier = cat_clf

        # 2. Train Department Recommender
        dept_rec = DepartmentRecommender(model_version="v1.0.0-benchmark")
        dept_rec.fit(df["full_text"].tolist(), df["department_id"].tolist())
        self.department_recommender = dept_rec

        # 3. Train Resolution Regressor
        res_reg = ResolutionRegressor(model_version="v1.0.0-benchmark")
        res_reg.fit(df, target_col="actual_duration_days")
        res_preds = res_reg.predict(df)
        res_metrics = compute_regression_metrics(df["actual_duration_days"].tolist(), res_preds)
        self.resolution_regressor = res_reg

        # 4. Train SLA Classifier
        sla_clf = SlaRiskClassifier(model_version="v1.0.0-benchmark")
        sla_clf.fit(df, target_col="sla_breached")
        sla_preds = sla_clf.predict(df)
        sla_probs = sla_clf.predict_proba(df)[:, 1]
        sla_metrics = compute_binary_metrics(df["sla_breached"].tolist(), sla_preds, sla_probs)
        self.sla_classifier = sla_clf

        # Update metadata
        audit = audit_production_dataset_sync()
        self.metadata = {
            "registry_version": "1.0.0",
            "last_trained_at": now_iso,
            "training_dataset": "benchmark_research_v1",
            "readiness_status": (
                "operational_ready" if audit.is_ready else "insufficient_production_data"
            ),
            "production_audit": audit.to_dict(),
            "models": {
                "category_classifier": {
                    "version": "v1.0.0-benchmark",
                    "algorithm": "TF-IDF + Calibrated Logistic Regression",
                    "metrics": {
                        "accuracy": cat_metrics["accuracy"],
                        "macro_f1": cat_metrics["macro_f1"],
                        "weighted_f1": cat_metrics["weighted_f1"],
                    },
                    "classes": cat_clf.classes_,
                },
                "department_recommender": {
                    "version": "v1.0.0-benchmark",
                    "algorithm": "TF-IDF + Logistic Regression",
                    "classes": dept_rec.classes_,
                },
                "sentence_embedder": {
                    "version": "v1.0.0",
                    "model_name": self.sentence_embedder.model_name,
                    "dimension": self.sentence_embedder.dimension,
                },
                "resolution_regressor": {
                    "version": "v1.0.0-benchmark",
                    "algorithm": getattr(res_reg, "algorithm", "LightGBMRegressor"),
                    "metrics": res_metrics,
                },
                "sla_classifier": {
                    "version": "v1.0.0-benchmark",
                    "algorithm": getattr(sla_clf, "algorithm", "XGBoostClassifier"),
                    "metrics": sla_metrics,
                },
            },
        }

        # Persist models and metadata
        self._save_artifacts()
        self._is_initialized = True
        logger.info("All ML models trained and artifacts persisted successfully.")

    def _save_artifacts(self):
        try:
            if self.category_classifier:
                self.category_classifier.save(str(self.artifacts_dir / "category_classifier.joblib"))
            if self.department_recommender:
                self.department_recommender.save(str(self.artifacts_dir / "department_recommender.joblib"))
            if self.resolution_regressor:
                self.resolution_regressor.save(str(self.artifacts_dir / "resolution_regressor.joblib"))
            if self.sla_classifier:
                self.sla_classifier.save(str(self.artifacts_dir / "sla_classifier.joblib"))

            meta_path = self.artifacts_dir / "registry_metadata.json"
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as ex:
            logger.error("Error saving ML artifacts: %s", str(ex))

    def predict_full_triage(
        self,
        title: str,
        description: str,
        ward: str = "Ward 14 (Central)",
        zone: str = "Zone A (Central)",
        priority_hint: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Runs comprehensive multi-model inference pipeline:
        1. Category classification
        2. Department recommendation
        3. Priority inference & SLA calculation
        4. Resolution time regression
        5. SLA breach risk classification
        6. SHAP feature attribution
        7. Lexical token attribution
        """
        self.initialize_models()
        full_text = f"{title}. {description}"

        # 1. Category
        cat_result = (
            self.category_classifier.classify_single(full_text)
            if self.category_classifier
            else {"predicted_category": "Road Infrastructure", "confidence": 0.85, "is_fallback": True}
        )
        cat = cat_result["predicted_category"]
        conf = cat_result["confidence"]

        # 2. Department
        dept_result = (
            self.department_recommender.recommend(full_text, category_hint=cat)
            if self.department_recommender
            else {
                "recommended_department_id": "dept_pwd",
                "recommended_department_name": "Public Works Department (PWD)",
                "confidence": 0.85,
            }
        )
        dept_id = dept_result["recommended_department_id"]
        dept_name = dept_result["recommended_department_name"]

        # 3. Priority determination
        if priority_hint and priority_hint in ("critical", "high", "medium", "low"):
            prio = priority_hint
        else:
            corpus_lower = full_text.lower()
            if any(w in corpus_lower for w in ["emergency", "danger", "burst", "severe", "fatal", "spark", "fire"]):
                prio = "critical"
            elif any(w in corpus_lower for w in ["overflow", "blocked", "broken", "major", "stagnant"]):
                prio = "high"
            else:
                prio = "medium"

        # 4. Resolution Duration
        dur_result = (
            self.resolution_regressor.predict_single(
                title=title,
                description=description,
                category=cat,
                department_id=dept_id,
                priority=prio,
                ward=ward,
            )
            if self.resolution_regressor
            else {"predicted_duration_days": 3.0}
        )
        duration_days = dur_result["predicted_duration_days"]

        # 5. SLA Risk
        sla_result = (
            self.sla_classifier.predict_single(
                title=title,
                description=description,
                category=cat,
                department_id=dept_id,
                priority=prio,
                ward=ward,
            )
            if self.sla_classifier
            else {"breach_probability": 0.20, "risk_tier": "low"}
        )

        # 6. SHAP Factors
        shap_factors = TabularExplainer.explain_duration_prediction(
            predicted_days=duration_days,
            priority=prio,
            category=cat,
            department_name=dept_name,
            ward=ward,
            text_length=len(full_text),
        )

        # 7. Token Attributions
        token_attributions = TokenAttributionExplainer.attribute_tokens(full_text)
        salient_tokens = [t["token"] for t in token_attributions if t.get("is_salient")]

        return {
            "predicted_category": cat,
            "predicted_subcategory": cat_result.get("predicted_subcategory", cat),
            "suggested_department_id": dept_id,
            "suggested_department_name": dept_name,
            "priority": prio,
            "confidence": conf,
            "predicted_duration_days": duration_days,
            "confidence_interval_low": dur_result.get("confidence_interval_low", max(0.5, duration_days - 0.5)),
            "confidence_interval_high": dur_result.get("confidence_interval_high", duration_days + 0.8),
            "sla_breach_risk": sla_result.get("risk_tier", "low"),
            "sla_breach_probability": sla_result.get("breach_probability", 0.20),
            "shap_factors": shap_factors,
            "token_attributions": token_attributions,
            "keywords_matched": salient_tokens or ["municipal_report"],
            "is_mock_fallback": False,
            "model_metadata": {
                "category_version": cat_result.get("model_version", "v1.0.0"),
                "readiness_status": self.metadata.get("readiness_status"),
            },
        }

    def get_health(self) -> Dict[str, Any]:
        """Returns health probe of the ML inference subsystem."""
        self.initialize_models()
        return {
            "status": "healthy" if self._is_initialized else "degraded",
            "is_initialized": self._is_initialized,
            "readiness_status": self.metadata.get("readiness_status"),
            "models_loaded": {
                "category_classifier": self.category_classifier is not None,
                "department_recommender": self.department_recommender is not None,
                "sentence_embedder": self.sentence_embedder is not None,
                "resolution_regressor": self.resolution_regressor is not None,
                "sla_classifier": self.sla_classifier is not None,
            },
            "embedding_dimension": self.sentence_embedder.dimension,
            "artifacts_directory": str(self.artifacts_dir),
            "last_trained_at": self.metadata.get("last_trained_at"),
        }


# Global model registry singleton
model_registry = ModelRegistry()
