"""
CivicMind AI — Grievance Model
"""

import uuid
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import (
    String,
    Text,
    Boolean,
    Numeric,
    Float,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Index,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.department import Department
    from app.models.embedding import GrievanceEmbedding
    from app.models.evidence import GrievanceEvidence
    from app.models.timeline import GrievanceTimeline
    from app.models.resolution import ResolutionReport
    from app.models.duplicate import ClusterMembership


class Grievance(Base):
    __tablename__ = "grievances"
    __table_args__ = (
        CheckConstraint(
            "priority IN ('critical', 'high', 'medium', 'low')",
            name="chk_grievance_priority",
        ),
        CheckConstraint(
            "status IN ('submitted', 'analyzed', 'assigned', 'in_progress', "
            "'resolution_submitted', 'citizen_verified', 'closed', 'escalated', 'reopened')",
            name="chk_grievance_status",
        ),
        Index("idx_grievances_dept_status_priority", "department_id", "status", "priority"),
        Index("idx_grievances_lat_lng", "latitude", "longitude"),
        Index("idx_grievances_sla_deadline", "sla_deadline"),
    )

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    citizen_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    department_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    assigned_officer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    category: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    subcategory: Mapped[str] = mapped_column(String(150), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="submitted", nullable=False, index=True)
    address: Mapped[str] = mapped_column(String(350), nullable=False)
    ward: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    zone: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    ai_confidence: Mapped[float] = mapped_column(Numeric(4, 3), default=0.900, nullable=False)
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    predicted_duration_days: Mapped[float] = mapped_column(Numeric(4, 2), default=3.0, nullable=False)
    expected_resolution_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sla_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sla_breached: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sla_breach_risk: Mapped[str] = mapped_column(String(20), default="low", nullable=False)
    duplicate_probability: Mapped[float] = mapped_column(Numeric(4, 3), default=0.000, nullable=False)
    duplicate_cluster_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    actual_resolution_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    citizen: Mapped["User"] = relationship(
        "User",
        foreign_keys=[citizen_id],
        back_populates="grievances",
    )
    department: Mapped["Department"] = relationship(
        "Department",
        back_populates="grievances",
    )
    assigned_officer: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[assigned_officer_id],
        back_populates="assigned_grievances",
    )
    embedding: Mapped[Optional["GrievanceEmbedding"]] = relationship(
        "GrievanceEmbedding",
        back_populates="grievance",
        uselist=False,
        cascade="all, delete-orphan",
    )
    evidence: Mapped[List["GrievanceEvidence"]] = relationship(
        "GrievanceEvidence",
        back_populates="grievance",
        cascade="all, delete-orphan",
    )
    timeline: Mapped[List["GrievanceTimeline"]] = relationship(
        "GrievanceTimeline",
        back_populates="grievance",
        cascade="all, delete-orphan",
        order_by="GrievanceTimeline.created_at.asc()",
    )
    resolution_report: Mapped[Optional["ResolutionReport"]] = relationship(
        "ResolutionReport",
        back_populates="grievance",
        uselist=False,
        cascade="all, delete-orphan",
    )
    cluster_memberships: Mapped[List["ClusterMembership"]] = relationship(
        "ClusterMembership",
        back_populates="grievance",
        cascade="all, delete-orphan",
    )
