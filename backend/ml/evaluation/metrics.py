"""
CivicMind AI — Comprehensive ML Evaluation Metrics
Standardized performance assessment across classification, regression, and ranking tasks.
"""

from typing import Dict, Any, List, Union
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    mean_absolute_error,
    root_mean_squared_error,
    r2_score,
    median_absolute_error,
)


def compute_multiclass_metrics(
    y_true: Union[List[str], np.ndarray],
    y_pred: Union[List[str], np.ndarray],
    labels: List[str] = None,
) -> Dict[str, Any]:
    """Computes comprehensive multi-class classification metrics."""
    acc = float(accuracy_score(y_true, y_pred))
    macro_prec = float(precision_score(y_true, y_pred, average="macro", zero_division=0))
    weighted_prec = float(precision_score(y_true, y_pred, average="weighted", zero_division=0))
    macro_rec = float(recall_score(y_true, y_pred, average="macro", zero_division=0))
    weighted_rec = float(recall_score(y_true, y_pred, average="weighted", zero_division=0))
    macro_f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    weighted_f1 = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))

    cm = confusion_matrix(y_true, y_pred, labels=labels).tolist() if labels else []

    return {
        "accuracy": round(acc, 4),
        "macro_precision": round(macro_prec, 4),
        "weighted_precision": round(weighted_prec, 4),
        "macro_recall": round(macro_rec, 4),
        "weighted_recall": round(weighted_rec, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
        "labels": labels or sorted(list(set(y_true))),
        "confusion_matrix": cm,
    }


def compute_binary_metrics(
    y_true: Union[List[int], np.ndarray],
    y_pred: Union[List[int], np.ndarray],
    y_prob: Union[List[float], np.ndarray] = None,
) -> Dict[str, Any]:
    """Computes binary classification & calibration metrics for SLA breach prediction."""
    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))

    metrics = {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
    }

    if y_prob is not None:
        try:
            roc_auc = float(roc_auc_score(y_true, y_prob))
            pr_auc = float(average_precision_score(y_true, y_prob))
            brier = float(brier_score_loss(y_true, y_prob))
            metrics["roc_auc"] = round(roc_auc, 4)
            metrics["pr_auc"] = round(pr_auc, 4)
            metrics["brier_score"] = round(brier, 4)
        except Exception:
            pass

    return metrics


def compute_regression_metrics(
    y_true: Union[List[float], np.ndarray],
    y_pred: Union[List[float], np.ndarray],
) -> Dict[str, Any]:
    """Computes regression metrics for grievance resolution time prediction."""
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(root_mean_squared_error(y_true, y_pred))
    medae = float(median_absolute_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))

    return {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "median_ae": round(medae, 4),
        "r2_score": round(r2, 4),
    }
