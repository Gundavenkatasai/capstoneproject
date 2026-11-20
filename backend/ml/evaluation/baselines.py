"""
CivicMind AI — ML Baseline Models
Provides empirical baselines for classification and regression benchmarking:
- Majority Class Classifier
- Median Duration Regressor
- Prior Probability SLA Classifier
- Simple TF-IDF + Logistic Regression
"""

from typing import Dict, Any, List, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, Ridge


class MajorityClassBaseline:
    """Predicts the most frequent class observed in training."""

    def __init__(self):
        self.majority_class: Optional[str] = None
        self.classes_: List[str] = []

    def fit(self, y: List[str]):
        vals, counts = np.unique(y, return_counts=True)
        self.majority_class = vals[np.argmax(counts)]
        self.classes_ = list(vals)
        return self

    def predict(self, X) -> List[str]:
        return [self.majority_class] * len(X)

    def predict_proba(self, X) -> np.ndarray:
        probas = np.zeros((len(X), len(self.classes_)))
        idx = self.classes_.index(self.majority_class)
        probas[:, idx] = 1.0
        return probas


class MedianDurationBaseline:
    """Predicts the constant median duration observed in training."""

    def __init__(self):
        self.median_duration: float = 3.0

    def fit(self, y: List[float]):
        self.median_duration = float(np.median(y))
        return self

    def predict(self, X) -> List[float]:
        return [self.median_duration] * len(X)


class PriorProbabilitySlaBaseline:
    """Predicts the empirical base rate of SLA breaches observed in training."""

    def __init__(self):
        self.prior_probability: float = 0.20

    def fit(self, y: List[bool]):
        self.prior_probability = float(np.mean(y))
        return self

    def predict(self, X) -> List[bool]:
        return [bool(self.prior_probability >= 0.5)] * len(X)

    def predict_proba(self, X) -> np.ndarray:
        p = self.prior_probability
        return np.array([[1.0 - p, p] for _ in range(len(X))])
