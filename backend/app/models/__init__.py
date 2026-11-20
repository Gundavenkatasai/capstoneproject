"""
CivicMind AI — SQLAlchemy 2.0 Models Module
Exports Base and all 15 relational and vector entities.
"""

from app.models.base import Base, TimestampMixin
from app.models.user import User
from app.models.department import Department
from app.models.officer import Officer
from app.models.grievance import Grievance
from app.models.embedding import GrievanceEmbedding
from app.models.evidence import GrievanceEvidence
from app.models.timeline import GrievanceTimeline
from app.models.resolution import ResolutionReport
from app.models.duplicate import DuplicateCluster, ClusterMembership
from app.models.hotspot import Hotspot
from app.models.knowledge import KnowledgeNode, KnowledgeEdge
from app.models.audit import AuditLog
from app.models.token import RefreshToken
from app.models.outbox import OutboxEvent

__all__ = [
    "Base",
    "TimestampMixin",
    "User",
    "Department",
    "Officer",
    "Grievance",
    "GrievanceEmbedding",
    "GrievanceEvidence",
    "GrievanceTimeline",
    "ResolutionReport",
    "DuplicateCluster",
    "ClusterMembership",
    "Hotspot",
    "KnowledgeNode",
    "KnowledgeEdge",
    "AuditLog",
    "RefreshToken",
    "OutboxEvent",
]
