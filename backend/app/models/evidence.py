"""
CivicMind AI — Grievance Multimedia Evidence Model
"""

import uuid
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, BigInteger, Text, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.grievance import Grievance
    from app.models.user import User


class GrievanceEvidence(Base):
    __tablename__ = "grievance_evidence"
    __table_args__ = (
        CheckConstraint(
            "file_type IN ('image', 'document', 'audio')",
            name="chk_evidence_file_type",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    grievance_id: Mapped[Optional[str]] = mapped_column(
        String(30),
        ForeignKey("grievances.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_url: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    grievance: Mapped["Grievance"] = relationship(
        "Grievance",
        back_populates="evidence",
    )
    uploader: Mapped["User"] = relationship(
        "User",
        back_populates="evidence_uploads",
    )
