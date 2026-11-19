"""
CivicMind AI — Duplicate Cluster & Membership Models
"""

import uuid
from typing import List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import (
    String,
    Text,
    Integer,
    Numeric,
    DateTime,
    ForeignKey,
    CheckConstraint,
    PrimaryKeyConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.grievance import Grievance


class DuplicateCluster(Base):
    __tablename__ = "duplicate_clusters"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending_review', 'merged', 'rejected', 'split')",
            name="chk_duplicate_cluster_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    cluster_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    category: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    master_grievance_id: Mapped[str] = mapped_column(
        String(30),
        ForeignKey("grievances.id", ondelete="RESTRICT"),
        nullable=False,
    )
    similarity_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    proximity_meters: Mapped[int] = mapped_column(Integer, nullable=False)
    time_span_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="pending_review", nullable=False)
    ai_recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    reasons: Mapped[List[str]] = mapped_column(ARRAY(Text), default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    memberships: Mapped[List["ClusterMembership"]] = relationship(
        "ClusterMembership",
        back_populates="cluster",
        cascade="all, delete-orphan",
    )


class ClusterMembership(Base):
    __tablename__ = "cluster_memberships"
    __table_args__ = (
        PrimaryKeyConstraint("cluster_id", "grievance_id", name="pk_cluster_memberships"),
    )

    cluster_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("duplicate_clusters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    grievance_id: Mapped[str] = mapped_column(
        String(30),
        ForeignKey("grievances.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    cluster: Mapped["DuplicateCluster"] = relationship(
        "DuplicateCluster",
        back_populates="memberships",
    )
    grievance: Mapped["Grievance"] = relationship(
        "Grievance",
        back_populates="cluster_memberships",
    )
