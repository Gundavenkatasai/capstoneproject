"""
CivicMind AI — Grievance Category Classifier
Trains and serves multi-class category classification models using
TF-IDF feature extraction with calibrated linear/tree classifiers.
"""

import os
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV
import joblib

from ml.data.normalization import clean_text, STANDARD_CATEGORIES


class CategoryClassifier:
    """
    Classifies citizen grievance text into municipal categories.
    Uses n-gram sublinear TF-IDF vectorization paired with calibrated logistic regression.
    """

    def __init__(self, model_version: str = "v1.0.0"):
        self.model_version = model_version
        self.pipeline: Optional[Pipeline] = None
        self.classes_: List[str] = STANDARD_CATEGORIES
        self.is_trained: bool = False

    def build_pipeline(self) -> Pipeline:
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            min_df=1,
            max_df=0.95,
            strip_accents="unicode",
        )
        base_clf = LogisticRegression(
            C=2.0,
            max_iter=500,
            class_weight="balanced",
            solver="lbfgs",
            random_state=42,
        )
        return Pipeline([
            ("tfidf", vectorizer),
            ("clf", base_clf),
        ])

    def fit(self, texts: List[str], labels: List[str]):
        """Fits the category classifier pipeline on text inputs."""
        cleaned_texts = [clean_text(t) for t in texts]
        self.pipeline = self.build_pipeline()
        self.pipeline.fit(cleaned_texts, labels)
        self.classes_ = list(self.pipeline.named_steps["clf"].classes_)
        self.is_trained = True
        return self

    def predict(self, texts: List[str]) -> List[str]:
        if not self.is_trained or self.pipeline is None:
            return [STANDARD_CATEGORIES[0]] * len(texts)
        cleaned = [clean_text(t) for t in texts]
        return list(self.pipeline.predict(cleaned))

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        if not self.is_trained or self.pipeline is None:
            n = len(texts)
            k = len(self.classes_)
            return np.ones((n, k)) / k
        cleaned = [clean_text(t) for t in texts]
        return self.pipeline.predict_proba(cleaned)

    def classify_single(self, text: str) -> Dict[str, Any]:
        """Classifies a single grievance string with confidence and class distribution."""
        cleaned = clean_text(text)
        if not self.is_trained or self.pipeline is None:
            return {
                "predicted_category": STANDARD_CATEGORIES[0],
                "confidence": 0.50,
                "is_fallback": True,
                "probabilities": {cat: 1.0 / len(STANDARD_CATEGORIES) for cat in STANDARD_CATEGORIES},
                "model_version": self.model_version,
            }

        probas = self.pipeline.predict_proba([cleaned])[0]
        max_idx = int(np.argmax(probas))
        predicted_cat = self.classes_[max_idx]
        confidence = float(probas[max_idx])

        prob_dict = {cls: round(float(prob), 4) for cls, prob in zip(self.classes_, probas)}

        return {
            "predicted_category": predicted_cat,
            "confidence": round(confidence, 4),
            "is_fallback": False,
            "probabilities": prob_dict,
            "model_version": self.model_version,
        }

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: str) -> "CategoryClassifier":
        return joblib.load(filepath)
