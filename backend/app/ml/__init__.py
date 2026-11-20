"""
CivicMind AI — ML Package Bridge
Provides transparent access to backend/ml modules.
"""

import sys
import ml

# Bridge subpackages
for submod in [
    "data",
    "classification",
    "embeddings",
    "duplicates",
    "resolution",
    "sla",
    "explainability",
    "registry",
    "evaluation",
    "geospatial",
]:
    try:
        __import__(f"ml.{submod}")
        sys.modules[f"app.ml.{submod}"] = sys.modules[f"ml.{submod}"]
    except Exception:
        pass
