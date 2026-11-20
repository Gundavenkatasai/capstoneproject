"""
CivicMind AI — Grievance Resolution Time Regressor
Predicts operational resolution duration in days using leakage-free intake features.
Strictly prohibits features derived from future resolution reports or closing events.
"""

import os
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingRegressor
import joblib

from ml.data.normalization import clean_text, PRIORITY_LEVELS


CATEGORICAL_FEATURES = ["category", "department_id", "priority", "ward"]
NUMERICAL_FEATURES = ["text_length", "priority_level"]


def extract_regression_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts strictly pre-triage and intake features to prevent leakage:
    - category, department_id, priority, ward
    - text_length: length of title + description
    - priority_level: ordinal encoding of priority
    """
    features = pd.DataFrame()

    features["category"] = df["category"].fillna("Road Infrastructure")
    features["department_id"] = df["department_id"].fillna("dept_pwd")
    features["priority"] = df["priority"].fillna("medium")
    features["ward"] = df["ward"].fillna("Ward 14 (Central)")

    # Derived pre-triage signals
    text_series = (df["title"].fillna("") + " " + df["description"].fillna("")).astype(str)
    features["text_length"] = text_series.apply(lambda s: len(clean_text(s)))
    features["priority_level"] = features["priority"].map(lambda p: PRIORITY_LEVELS.get(p, 1))

    return features


class ResolutionRegressor:
    """
    Predicts estimated resolution time (days) using gradient boosting trees.
    Enforces strictly positive duration bounds [0.5, 30.0].
    """

    def __init__(self, model_version: str = "v1.0.0"):
        self.model_version = model_version
        self.pipeline: Optional[Pipeline] = None
        self.is_trained: bool = False
        self.feature_names: List[str] = []

    def build_pipeline(self) -> Pipeline:
        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "cat",
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                    CATEGORICAL_FEATURES,
                ),
                (
                    "num",
                    StandardScaler(),
                    NUMERICAL_FEATURES,
                ),
            ]
        )

        model = HistGradientBoostingRegressor(
            max_iter=150,
            learning_rate=0.08,
            max_depth=5,
            min_samples_leaf=5,
            random_state=42,
        )

        return Pipeline([
            ("preprocessor", preprocessor),
            ("model", model),
        ])

    def fit(self, df: pd.DataFrame, target_col: str = "actual_duration_days"):
        """Trains regression model on intake features and empirical resolution durations."""
        X = extract_regression_features(df)
        y = df[target_col].values.astype(float)

        self.pipeline = self.build_pipeline()
        self.pipeline.fit(X, y)
        self.is_trained = True
        return self

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Predicts resolution days with strictly positive lower bound of 0.5 days."""
        if not self.is_trained or self.pipeline is None:
            # Fallback to 3.0 days
            return np.full(len(df), 3.0)

        X = extract_regression_features(df)
        preds = self.pipeline.predict(X)
        return np.clip(preds, 0.5, 30.0)

    def predict_single(
        self,
        title: str,
        description: str,
        category: str,
        department_id: str,
        priority: str,
        ward: str,
    ) -> Dict[str, Any]:
        """Predicts duration days for a single grievance with uncertainty intervals."""
        row_df = pd.DataFrame([{
            "title": title,
            "description": description,
            "category": category,
            "department_id": department_id,
            "priority": priority,
            "ward": ward,
        }])

        if not self.is_trained or self.pipeline is None:
            prio_default = {"critical": 1.5, "high": 2.5, "medium": 3.5, "low": 5.0}.get(priority, 3.0)
            return {
                "predicted_duration_days": prio_default,
                "confidence_interval_low": max(0.5, prio_default - 0.8),
                "confidence_interval_high": prio_default + 1.2,
                "is_fallback": True,
                "model_version": self.model_version,
            }

        pred = float(self.predict(row_df)[0])
        # Uncertainty estimate based on 20% margin
        low_bound = round(max(0.5, pred * 0.8), 2)
        high_bound = round(pred * 1.25, 2)

        return {
            "predicted_duration_days": round(pred, 2),
            "confidence_interval_low": low_bound,
            "confidence_interval_high": high_bound,
            "is_fallback": False,
            "model_version": self.model_version,
        }

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: str) -> "ResolutionRegressor":
        return joblib.load(filepath)
