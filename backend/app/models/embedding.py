"""
CivicMind AI — Grievance Dense Vector Embedding Model
Integrates pgvector for 768-dimensional semantic representations and HNSW cosine similarity search.
"""

from typing import List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.models.base import Base
from app.core.config import settings

if TYPE_CHECKING:
    from app.models.grievance import Grievance


class GrievanceEmbedding(Base):
    __tablename__ = "grievance_embeddings"
    __table_args__ = (
        Index(
            "idx_embeddings_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    grievance_id: Mapped[str] = mapped_column(
        String(30),
        ForeignKey("grievances.id", ondelete="CASCADE"),
        primary_key=True,
    )
    embedding: Mapped[List[float]] = mapped_column(
        Vector(settings.EMBEDDING_DIMENSION),
        nullable=False,
    )
    model_version: Mapped[str] = mapped_column(
        String(50),
        default=settings.DEFAULT_EMBEDDING_MODEL,
        nullable=False,
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationship
    grievance: Mapped["Grievance"] = relationship(
        "Grievance",
        back_populates="embedding",
    )
