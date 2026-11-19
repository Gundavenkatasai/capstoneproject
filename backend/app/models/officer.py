"""
CivicMind AI — Officer Profile Extension Model
"""

import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.department import Department


class Officer(Base):
    __tablename__ = "officers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    department_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    assigned_ward: Mapped[str] = mapped_column(String(100), nullable=False)
    active_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    resolved_mtd: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_resolution_hours: Mapped[float] = mapped_column(Numeric(6, 1), default=48.0, nullable=False)
    rating: Mapped[float] = mapped_column(Numeric(3, 2), default=5.00, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="officer_profile")
    department: Mapped["Department"] = relationship("Department", back_populates="officers")
