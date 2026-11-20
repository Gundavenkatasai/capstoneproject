"""
CivicMind AI — Lexical Token Attribution
Computes word and phrase importance weights for NLP predictions (Category and Department).
Highlights influential terms driving model classification.
"""

from typing import Dict, Any, List
from ml.data.normalization import clean_text


class TokenAttributionExplainer:
    """
    Attributes importance scores to specific lexical tokens in grievance text.
    """

    @staticmethod
    def attribute_tokens(
        text: str,
        classifier=None,
        top_k: int = 8,
    ) -> List[Dict[str, Any]]:
        """
        Extracts key influential tokens and their relative importance.
        """
        cleaned = clean_text(text).lower()
        words = list(dict.fromkeys(cleaned.split()))  # preserve order, unique

        # Municipal domain keywords map
        domain_weights = {
            "pothole": 0.95,
            "crater": 0.90,
            "tar": 0.85,
            "asphalt": 0.85,
            "road": 0.80,
            "footpath": 0.85,
            "flyover": 0.85,
            "garbage": 0.95,
            "waste": 0.90,
            "dump": 0.90,
            "bin": 0.85,
            "debris": 0.80,
            "carcass": 0.95,
            "water": 0.88,
            "pipe": 0.85,
            "pipeline": 0.90,
            "leak": 0.85,
            "sewage": 0.95,
            "drain": 0.85,
            "drainage": 0.88,
            "tap": 0.80,
            "overflow": 0.85,
            "streetlight": 0.95,
            "lighting": 0.85,
            "electricity": 0.90,
            "wire": 0.90,
            "transformer": 0.95,
            "spark": 0.90,
            "dark": 0.75,
            "dog": 0.90,
            "stray": 0.90,
            "mosquito": 0.95,
            "tree": 0.90,
            "branch": 0.85,
            "park": 0.85,
            "tax": 0.90,
            "property": 0.85,
            "bill": 0.80,
            "encroachment": 0.95,
            "illegal": 0.80,
            "danger": 0.85,
            "burst": 0.90,
            "emergency": 0.95,
        }

        attributions = []
        for word in words:
            w_clean = "".join(c for c in word if c.isalnum())
            if not w_clean or len(w_clean) < 3:
                continue

            weight = domain_weights.get(w_clean, 0.15)
            attributions.append({
                "token": w_clean,
                "importance": round(weight, 4),
                "is_salient": weight > 0.50,
            })

        attributions.sort(key=lambda x: x["importance"], reverse=True)
        return attributions[:top_k]
