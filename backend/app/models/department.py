"""
CivicMind AI — Department Model
"""

from typing import List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Integer, Numeric, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.officer import Officer
    from app.models.grievance import Grievance


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    head_name: Mapped[str] = mapped_column(String(150), nullable=False)
    officer_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    zone: Mapped[str] = mapped_column(String(100), default="All Zones", nullable=False)
    workload_status: Mapped[str] = mapped_column(String(30), default="optimal", nullable=False)
    sla_compliance_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=90.00, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    officers: Mapped[List["Officer"]] = relationship(
        "Officer",
        back_populates="department",
        cascade="all, delete-orphan",
    )
    grievances: Mapped[List["Grievance"]] = relationship(
        "Grievance",
        back_populates="department",
    )
