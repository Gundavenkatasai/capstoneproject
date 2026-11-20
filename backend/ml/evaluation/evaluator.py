"""
CivicMind AI — Model Evaluator & Benchmark Comparison
Runs evaluation suites comparing trained production-candidate models against empirical baselines.
"""

from typing import Dict, Any
import numpy as np
import pandas as pd

from ml.evaluation.metrics import (
    compute_multiclass_metrics,
    compute_binary_metrics,
    compute_regression_metrics,
)
from ml.evaluation.baselines import (
    MajorityClassBaseline,
    MedianDurationBaseline,
    PriorProbabilitySlaBaseline,
)


def evaluate_classifier_against_baseline(
    model,
    X_test,
    y_test: list,
    classes: list = None,
) -> Dict[str, Any]:
    """Evaluates classifier model vs majority class baseline."""
    # Model predictions
    y_pred = model.predict(X_test)
    model_metrics = compute_multiclass_metrics(y_test, y_pred, labels=classes)

    # Baseline predictions
    baseline = MajorityClassBaseline().fit(y_test)
    b_pred = baseline.predict(X_test)
    base_metrics = compute_multiclass_metrics(y_test, b_pred, labels=classes)

    return {
        "model_metrics": model_metrics,
        "baseline_metrics": base_metrics,
        "accuracy_delta": round(model_metrics["accuracy"] - base_metrics["accuracy"], 4),
        "f1_delta": round(model_metrics["macro_f1"] - base_metrics["macro_f1"], 4),
    }


def evaluate_regressor_against_baseline(
    model,
    X_test,
    y_test: list,
) -> Dict[str, Any]:
    """Evaluates duration regressor vs median duration baseline."""
    y_pred = model.predict(X_test)
    model_metrics = compute_regression_metrics(y_test, y_pred)

    baseline = MedianDurationBaseline().fit(y_test)
    b_pred = baseline.predict(X_test)
    base_metrics = compute_regression_metrics(y_test, b_pred)

    return {
        "model_metrics": model_metrics,
        "baseline_metrics": base_metrics,
        "mae_reduction": round(base_metrics["mae"] - model_metrics["mae"], 4),
        "rmse_reduction": round(base_metrics["rmse"] - model_metrics["rmse"], 4),
    }


def evaluate_sla_classifier_against_baseline(
    model,
    X_test,
    y_test: list,
) -> Dict[str, Any]:
    """Evaluates SLA breach classifier vs base-rate baseline."""
    y_pred = model.predict(X_test)
    y_prob = None
    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_test)[:, 1]

    model_metrics = compute_binary_metrics(y_test, y_pred, y_prob)

    baseline = PriorProbabilitySlaBaseline().fit(y_test)
    b_pred = baseline.predict(X_test)
    b_prob = baseline.predict_proba(X_test)[:, 1]
    base_metrics = compute_binary_metrics(y_test, b_pred, b_prob)

    return {
        "model_metrics": model_metrics,
        "baseline_metrics": base_metrics,
        "f1_delta": round(model_metrics["f1_score"] - base_metrics["f1_score"], 4),
    }
