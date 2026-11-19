"""
CivicMind AI — SQLAlchemy 2.0 Declarative Base
"""

from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy 2.0 ORM models in CivicMind AI.
    """
    pass


class TimestampMixin:
    """
    Reusable mixin providing created_at and updated_at tracking fields.
    """
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
