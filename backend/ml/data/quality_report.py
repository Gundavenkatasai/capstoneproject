"""
CivicMind AI — Dataset Quality and Integrity Report
Generates empirical diagnostics on data distributions, label counts, and missingness.
"""

from typing import Dict, Any
import pandas as pd


def generate_quality_report(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generates a comprehensive dataset quality profile:
    - Row and column counts
    - Missing value rates
    - Category & Department distributions
    - SLA breach base rate
    - Duration percentiles (median, 90th percentile)
    """
    total = len(df)
    if total == 0:
        return {"error": "Empty dataset"}

    missing_counts = df.isnull().sum().to_dict()

    cat_counts = df["category"].value_counts().to_dict() if "category" in df.columns else {}
    dept_counts = df["department_id"].value_counts().to_dict() if "department_id" in df.columns else {}
    prio_counts = df["priority"].value_counts().to_dict() if "priority" in df.columns else {}

    sla_breach_rate = float(df["sla_breached"].mean()) if "sla_breached" in df.columns else 0.0

    duration_stats = {}
    if "actual_duration_days" in df.columns:
        dur = df["actual_duration_days"]
        duration_stats = {
            "mean": round(float(dur.mean()), 2),
            "median": round(float(dur.median()), 2),
            "std": round(float(dur.std()), 2),
            "min": round(float(dur.min()), 2),
            "max": round(float(dur.max()), 2),
            "p90": round(float(dur.quantile(0.90)), 2),
        }

    return {
        "total_records": total,
        "missing_values": missing_counts,
        "category_distribution": cat_counts,
        "department_distribution": dept_counts,
        "priority_distribution": prio_counts,
        "sla_breach_rate": round(sla_breach_rate, 4),
        "duration_statistics": duration_stats,
    }
