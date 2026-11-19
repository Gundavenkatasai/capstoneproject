"""
CivicMind AI — User Model
"""

import uuid
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Boolean, Text, DateTime, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.officer import Officer
    from app.models.grievance import Grievance
    from app.models.evidence import GrievanceEvidence
    from app.models.resolution import ResolutionReport
    from app.models.token import RefreshToken


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('citizen', 'officer', 'admin')",
            name="chk_user_role_valid"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False, default="citizen")
    phone: Mapped[Optional[str]] = mapped_column(String(25), nullable=True)
    ward: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    badge: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
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

    # Relationships
    officer_profile: Mapped[Optional["Officer"]] = relationship(
        "Officer",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    grievances: Mapped[List["Grievance"]] = relationship(
        "Grievance",
        back_populates="citizen",
        foreign_keys="Grievance.citizen_id",
    )
    assigned_grievances: Mapped[List["Grievance"]] = relationship(
        "Grievance",
        back_populates="assigned_officer",
        foreign_keys="Grievance.assigned_officer_id",
    )
    evidence_uploads: Mapped[List["GrievanceEvidence"]] = relationship(
        "GrievanceEvidence",
        back_populates="uploader",
    )
    resolution_reports: Mapped[List["ResolutionReport"]] = relationship(
        "ResolutionReport",
        back_populates="officer",
    )
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
