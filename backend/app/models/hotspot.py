"""
CivicMind AI — Geographic Hotspot & Early-Warning Radar Model
"""

from typing import List
from datetime import datetime
from sqlalchemy import (
    String,
    Text,
    Integer,
    Float,
    Boolean,
    DateTime,
    CheckConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Hotspot(Base):
    __tablename__ = "hotspots"
    __table_args__ = (
        CheckConstraint(
            "risk_level IN ('critical', 'high', 'medium', 'low')",
            name="chk_hotspot_risk_level",
        ),
        CheckConstraint(
            "risk_score >= 0 AND risk_score <= 100",
            name="chk_hotspot_risk_score",
        ),
        CheckConstraint(
            "trend IN ('increasing', 'stable', 'decreasing')",
            name="chk_hotspot_trend",
        ),
    )

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    category: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    zone: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    ward: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    radius_meters: Mapped[int] = mapped_column(Integer, nullable=False)
    complaint_count: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    trend: Mapped[str] = mapped_column(String(20), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_action: Mapped[str] = mapped_column(Text, nullable=False)
    historical_velocity: Mapped[List[int]] = mapped_column(
        ARRAY(Integer),
        default=list,
        nullable=False,
    )
    is_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
