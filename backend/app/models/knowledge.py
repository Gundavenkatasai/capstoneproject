"""
CivicMind AI — Public Service Knowledge Graph Models
"""

from typing import Dict, Any, List
from sqlalchemy import String, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"
    __table_args__ = (
        CheckConstraint(
            "type IN ('department', 'category', 'asset', 'jurisdiction', 'procedure', 'officer')",
            name="chk_knowledge_node_type",
        ),
    )

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    group_code: Mapped[str] = mapped_column(String(50), nullable=False)
    color_hex: Mapped[str] = mapped_column(String(10), default="#1E6BE6", nullable=False)
    properties: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    outgoing_edges: Mapped[List["KnowledgeEdge"]] = relationship(
        "KnowledgeEdge",
        foreign_keys="KnowledgeEdge.source_node",
        back_populates="source",
        cascade="all, delete-orphan",
    )
    incoming_edges: Mapped[List["KnowledgeEdge"]] = relationship(
        "KnowledgeEdge",
        foreign_keys="KnowledgeEdge.target_node",
        back_populates="target",
        cascade="all, delete-orphan",
    )


class KnowledgeEdge(Base):
    __tablename__ = "knowledge_edges"
    __table_args__ = (
        CheckConstraint(
            "relation IN ('handles', 'located_in', 'related_to', 'escalates_to', 'resolves', 'belongs_to')",
            name="chk_knowledge_edge_relation",
        ),
    )

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    source_node: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("knowledge_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_node: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("knowledge_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    relation: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relationships
    source: Mapped["KnowledgeNode"] = relationship(
        "KnowledgeNode",
        foreign_keys=[source_node],
        back_populates="outgoing_edges",
    )
    target: Mapped["KnowledgeNode"] = relationship(
        "KnowledgeNode",
        foreign_keys=[target_node],
        back_populates="incoming_edges",
    )
