"""
CivicMind AI — Department Recommendation Engine
Recommends responsible municipal departments with probability distribution,
secondary choice fallback, and keyword fit scoring.
"""

import os
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

from ml.data.normalization import (
    clean_text,
    STANDARD_DEPARTMENTS,
    CATEGORY_TO_DEPARTMENT,
)


class DepartmentRecommender:
    """
    Recommends primary and secondary municipal departments based on grievance description.
    """

    def __init__(self, model_version: str = "v1.0.0"):
        self.model_version = model_version
        self.pipeline: Optional[Pipeline] = None
        self.classes_: List[str] = list(STANDARD_DEPARTMENTS.keys())
        self.is_trained: bool = False

    def build_pipeline(self) -> Pipeline:
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            min_df=1,
            strip_accents="unicode",
        )
        clf = LogisticRegression(
            C=1.5,
            max_iter=500,
            class_weight="balanced",
            solver="lbfgs",
            random_state=42,
        )
        return Pipeline([
            ("tfidf", vectorizer),
            ("clf", clf),
        ])

    def fit(self, texts: List[str], dept_ids: List[str]):
        cleaned_texts = [clean_text(t) for t in texts]
        self.pipeline = self.build_pipeline()
        self.pipeline.fit(cleaned_texts, dept_ids)
        self.classes_ = list(self.pipeline.named_steps["clf"].classes_)
        self.is_trained = True
        return self

    def recommend(self, text: str, category_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Recommends primary and second-choice department with fit scores.
        """
        cleaned = clean_text(text)

        if not self.is_trained or self.pipeline is None:
            # Fallback to category hint or default PWD
            default_dept = CATEGORY_TO_DEPARTMENT.get(category_hint or "", "dept_pwd")
            meta = STANDARD_DEPARTMENTS.get(default_dept, STANDARD_DEPARTMENTS["dept_pwd"])
            return {
                "recommended_department_id": default_dept,
                "recommended_department_name": meta["name"],
                "confidence": 0.85,
                "second_choice_id": "dept_sanitation" if default_dept != "dept_sanitation" else "dept_pwd",
                "second_choice_name": STANDARD_DEPARTMENTS["dept_sanitation"]["name"],
                "department_fit_score": 0.85,
                "is_fallback": True,
                "model_version": self.model_version,
            }

        probas = self.pipeline.predict_proba([cleaned])[0]
        sorted_indices = np.argsort(probas)[::-1]

        top_idx = sorted_indices[0]
        top_dept_id = self.classes_[top_idx]
        top_conf = float(probas[top_idx])

        second_dept_id = None
        second_dept_name = None
        if len(sorted_indices) > 1:
            second_idx = sorted_indices[1]
            second_dept_id = self.classes_[second_idx]
            second_meta = STANDARD_DEPARTMENTS.get(second_dept_id, {})
            second_dept_name = second_meta.get("name", second_dept_id)

        top_meta = STANDARD_DEPARTMENTS.get(top_dept_id, {})
        top_name = top_meta.get("name", top_dept_id)

        return {
            "recommended_department_id": top_dept_id,
            "recommended_department_name": top_name,
            "confidence": round(top_conf, 4),
            "second_choice_id": second_dept_id,
            "second_choice_name": second_dept_name,
            "department_fit_score": round(top_conf, 4),
            "is_fallback": False,
            "model_version": self.model_version,
        }

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: str) -> "DepartmentRecommender":
        return joblib.load(filepath)
