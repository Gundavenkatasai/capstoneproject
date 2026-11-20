"""
Test SQLAlchemy 2.0 model metadata, constraints, and relational schemas.
"""

import pytest
from app.models import (
    Base,
    User,
    Department,
    Officer,
    Grievance,
    GrievanceEmbedding,
    GrievanceEvidence,
    GrievanceTimeline,
    ResolutionReport,
    DuplicateCluster,
    ClusterMembership,
    Hotspot,
    KnowledgeNode,
    KnowledgeEdge,
    AuditLog,
    RefreshToken,
    OutboxEvent,
)

EXPECTED_TABLES = {
    "users",
    "departments",
    "officers",
    "grievances",
    "grievance_embeddings",
    "grievance_evidence",
    "grievance_timeline",
    "resolution_reports",
    "duplicate_clusters",
    "cluster_memberships",
    "hotspots",
    "knowledge_nodes",
    "knowledge_edges",
    "audit_logs",
    "refresh_tokens",
    "outbox_events",
}


def test_table_registration_count():
    """Verify exactly 16 relational, vector, and outbox tables are registered."""
    registered = set(Base.metadata.tables.keys())
    assert registered == EXPECTED_TABLES
    assert len(registered) == 16


def test_user_table_schema():
    """Verify users table columns and constraints."""
    table = Base.metadata.tables["users"]
    assert "id" in table.c
    assert "email" in table.c
    assert "role" in table.c
    assert "password_hash" in table.c
    assert table.c.email.unique or any(idx.unique for idx in table.indexes if "email" in idx.columns)


def test_department_table_schema():
    """Verify departments table columns."""
    table = Base.metadata.tables["departments"]
    assert "id" in table.c
    assert "code" in table.c
    assert "name" in table.c
    assert "sla_compliance_rate" in table.c


def test_grievance_table_schema():
    """Verify grievances table columns and foreign keys."""
    table = Base.metadata.tables["grievances"]
    assert "id" in table.c
    assert "citizen_id" in table.c
    assert "department_id" in table.c
    assert "priority" in table.c
    assert "status" in table.c
    assert "sla_deadline" in table.c
    assert "latitude" in table.c
    assert "longitude" in table.c

    # Verify foreign keys
    fk_targets = {fk.target_fullname for fk in table.foreign_keys}
    assert "users.id" in fk_targets
    assert "departments.id" in fk_targets


def test_embedding_table_schema():
    """Verify grievance_embeddings table definition and vector column."""
    table = Base.metadata.tables["grievance_embeddings"]
    assert "grievance_id" in table.c
    assert "embedding" in table.c
    assert "model_version" in table.c


def test_knowledge_graph_schema():
    """Verify knowledge_nodes and knowledge_edges tables."""
    nodes = Base.metadata.tables["knowledge_nodes"]
    edges = Base.metadata.tables["knowledge_edges"]
    assert "id" in nodes.c
    assert "type" in nodes.c
    assert "properties" in nodes.c
    assert "source_node" in edges.c
    assert "target_node" in edges.c
    assert "relation" in edges.c


def test_audit_logs_schema():
    """Verify immutable audit_logs table."""
    table = Base.metadata.tables["audit_logs"]
    assert "id" in table.c
    assert "action" in table.c
    assert "entity_type" in table.c


def test_outbox_table_schema():
    """Verify transactional outbox_events table."""
    table = Base.metadata.tables["outbox_events"]
    assert "id" in table.c
    assert "event_type" in table.c
    assert "aggregate_type" in table.c
    assert "aggregate_id" in table.c
    assert "payload" in table.c
    assert "status" in table.c
    assert "attempts" in table.c
    assert "max_attempts" in table.c
    assert "correlation_id" in table.c
    assert "scheduled_for" in table.c
    assert "processed_at" in table.c
    assert "created_at" in table.c
    assert "error_details" in table.c
