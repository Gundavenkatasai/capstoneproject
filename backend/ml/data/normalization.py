"""
CivicMind AI — Text & Metadata Normalization
Ensures consistent preprocessing across inference and training pipelines.
"""

import re
import unicodedata
from typing import Dict, List, Optional, Tuple


STANDARD_CATEGORIES: List[str] = [
    "Road Infrastructure",
    "Sanitation & Waste Management",
    "Water Supply & Drainage",
    "Urban Electricity & Street Lighting",
    "Health & Public Safety",
    "Parks & Horticulture",
    "Revenue & Property Tax",
    "Encroachment & Town Planning",
]

STANDARD_DEPARTMENTS: Dict[str, Dict[str, str]] = {
    "dept_pwd": {
        "id": "dept_pwd",
        "code": "PWD-RDS",
        "name": "Public Works Department (PWD)",
        "category": "Road Infrastructure",
    },
    "dept_sanitation": {
        "id": "dept_sanitation",
        "code": "MC-SWM",
        "name": "Municipal Solid Waste Management",
        "category": "Sanitation & Waste Management",
    },
    "dept_wssb": {
        "id": "dept_wssb",
        "code": "WSSB-OPS",
        "name": "Water Supply & Sewerage Board",
        "category": "Water Supply & Drainage",
    },
    "dept_electricity": {
        "id": "dept_electricity",
        "code": "EB-LTG",
        "name": "Urban Electricity & Street Lighting",
        "category": "Urban Electricity & Street Lighting",
    },
    "dept_health": {
        "id": "dept_health",
        "code": "MOH-HPS",
        "name": "Health & Public Safety Department",
        "category": "Health & Public Safety",
    },
    "dept_horticulture": {
        "id": "dept_horticulture",
        "code": "PRK-HORT",
        "name": "Parks & Horticulture Board",
        "category": "Parks & Horticulture",
    },
}

CATEGORY_TO_DEPARTMENT: Dict[str, str] = {
    "Road Infrastructure": "dept_pwd",
    "Sanitation & Waste Management": "dept_sanitation",
    "Water Supply & Drainage": "dept_wssb",
    "Urban Electricity & Street Lighting": "dept_electricity",
    "Health & Public Safety": "dept_health",
    "Parks & Horticulture": "dept_horticulture",
    "Revenue & Property Tax": "dept_pwd",
    "Encroachment & Town Planning": "dept_pwd",
}

PRIORITY_LEVELS: Dict[str, int] = {
    "low": 0,
    "medium": 1,
    "high": 2,
    "critical": 3,
}

PRIORITY_SLA_HOURS: Dict[str, int] = {
    "critical": 48,
    "high": 72,
    "medium": 96,
    "low": 120,
}


def clean_text(text: Optional[str]) -> str:
    """
    Cleans raw grievance text:
    - Normalizes Unicode (NFKD)
    - Strips URLs, email addresses, and phone numbers (privacy & leak prevention)
    - Replaces excess whitespace and non-printable characters
    - Preserves semantic words, municipal keywords, and punctuation signals
    """
    if not text:
        return ""

    # Normalize unicode
    text = unicodedata.normalize("NFKD", str(text))

    # Strip URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)

    # Strip email addresses
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", " ", text)

    # Strip phone numbers (e.g. +91 9900000001, 9876543210)
    text = re.sub(r"(\+91[\s-]?)?[6-9]\d{9}", " ", text)

    # Replace weird quotes, dashes
    text = re.sub(r"[‘’]", "'", text)
    text = re.sub(r"[“”]", '"', text)
    text = re.sub(r"[—–]", "-", text)

    # Collapse repeated whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def combine_title_description(title: str, description: str) -> str:
    """Combines cleaned title and description into an enriched textual document."""
    c_title = clean_text(title)
    c_desc = clean_text(description)
    if c_title and c_desc:
        return f"{c_title}. {c_desc}"
    return c_title or c_desc or ""
