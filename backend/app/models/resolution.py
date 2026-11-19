"""
CivicMind AI — Grievance Resolution Report Model
"""

import uuid
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import (
    String,
    Text,
    Numeric,
    SmallInteger,
    Boolean,
    DateTime,
    ForeignKey,
    CheckConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.grievance import Grievance
    from app.models.user import User


class ResolutionReport(Base):
    __tablename__ = "resolution_reports"
    __table_args__ = (
        CheckConstraint(
            "citizen_rating IS NULL OR (citizen_rating >= 1 AND citizen_rating <= 5)",
            name="chk_resolution_citizen_rating",
        ),
    )

    grievance_id: Mapped[str] = mapped_column(
        String(30),
        ForeignKey("grievances.id", ondelete="CASCADE"),
        primary_key=True,
    )
    officer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    report_text: Mapped[str] = mapped_column(Text, nullable=False)
    resolved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    officer_evidence_urls: Mapped[List[str]] = mapped_column(
        ARRAY(Text),
        default=list,
        nullable=False,
    )
    ai_verification_confidence: Mapped[float] = mapped_column(
        Numeric(4, 3),
        default=0.950,
        nullable=False,
    )
    citizen_rating: Mapped[Optional[int]] = mapped_column(
        SmallInteger,
        nullable=True,
    )
    citizen_comment: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    verified_by_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Relationships
    grievance: Mapped["Grievance"] = relationship(
        "Grievance",
        back_populates="resolution_report",
    )
    officer: Mapped["User"] = relationship(
        "User",
        back_populates="resolution_reports",
    )
