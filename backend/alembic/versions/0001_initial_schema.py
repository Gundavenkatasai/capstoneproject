"""Initial baseline schema with 15 entities and pgvector support

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-11-19 20:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable required PostgreSQL extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    # 2. Table: users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=30), nullable=False, server_default='citizen'),
        sa.Column('phone', sa.String(length=25), nullable=True),
        sa.Column('ward', sa.String(length=100), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('badge', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("role IN ('citizen', 'officer', 'admin')", name='chk_user_role_valid'),
        sa.UniqueConstraint('email', name='uq_users_email')
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_role', 'users', ['role'])

    # 3. Table: departments
    op.create_table(
        'departments',
        sa.Column('id', sa.String(length=50), primary_key=True),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('head_name', sa.String(length=150), nullable=False),
        sa.Column('officer_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('zone', sa.String(length=100), nullable=False, server_default='All Zones'),
        sa.Column('workload_status', sa.String(length=30), nullable=False, server_default='optimal'),
        sa.Column('sla_compliance_rate', sa.Numeric(precision=5, scale=2), nullable=False, server_default='90.00'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('code', name='uq_departments_code')
    )
    op.create_index('idx_departments_code', 'departments', ['code'], unique=True)

    # 4. Table: officers
    op.create_table(
        'officers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('department_id', sa.String(length=50), nullable=False),
        sa.Column('assigned_ward', sa.String(length=100), nullable=False),
        sa.Column('active_cases', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('resolved_mtd', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_resolution_hours', sa.Numeric(precision=6, scale=1), nullable=False, server_default='48.0'),
        sa.Column('rating', sa.Numeric(precision=3, scale=2), nullable=False, server_default='5.00'),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='active'),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='RESTRICT', name='fk_officers_department_id'),
        sa.ForeignKeyConstraint(['id'], ['users.id'], ondelete='CASCADE', name='fk_officers_id_users')
    )
    op.create_index('idx_officers_department_id', 'officers', ['department_id'])

    # 5. Table: grievances
    op.create_table(
        'grievances',
        sa.Column('id', sa.String(length=30), primary_key=True),
        sa.Column('title', sa.String(length=300), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('citizen_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('department_id', sa.String(length=50), nullable=False),
        sa.Column('assigned_officer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('category', sa.String(length=150), nullable=False),
        sa.Column('subcategory', sa.String(length=150), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='medium'),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='submitted'),
        sa.Column('address', sa.String(length=350), nullable=False),
        sa.Column('ward', sa.String(length=100), nullable=False),
        sa.Column('zone', sa.String(length=100), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('ai_confidence', sa.Numeric(precision=4, scale=3), nullable=False, server_default='0.900'),
        sa.Column('is_anonymous', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('language', sa.String(length=10), nullable=False, server_default='en'),
        sa.Column('predicted_duration_days', sa.Numeric(precision=4, scale=2), nullable=False, server_default='3.0'),
        sa.Column('expected_resolution_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('sla_deadline', sa.DateTime(timezone=True), nullable=False),
        sa.Column('sla_breached', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('sla_breach_risk', sa.String(length=20), nullable=False, server_default='low'),
        sa.Column('duplicate_probability', sa.Numeric(precision=4, scale=3), nullable=False, server_default='0.000'),
        sa.Column('duplicate_cluster_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('actual_resolution_date', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("priority IN ('critical', 'high', 'medium', 'low')", name='chk_grievance_priority'),
        sa.CheckConstraint(
            "status IN ('submitted', 'analyzed', 'assigned', 'in_progress', "
            "'resolution_submitted', 'citizen_verified', 'closed', 'escalated', 'reopened')",
            name='chk_grievance_status'
        ),
        sa.ForeignKeyConstraint(['assigned_officer_id'], ['users.id'], ondelete='SET NULL', name='fk_grievances_assigned_officer'),
        sa.ForeignKeyConstraint(['citizen_id'], ['users.id'], ondelete='RESTRICT', name='fk_grievances_citizen_id'),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='RESTRICT', name='fk_grievances_department_id')
    )
    op.create_index('idx_grievances_citizen_id', 'grievances', ['citizen_id'])
    op.create_index('idx_grievances_department_id', 'grievances', ['department_id'])
    op.create_index('idx_grievances_status', 'grievances', ['status'])
    op.create_index('idx_grievances_category', 'grievances', ['category'])
    op.create_index('idx_grievances_ward', 'grievances', ['ward'])
    op.create_index('idx_grievances_zone', 'grievances', ['zone'])
    op.create_index('idx_grievances_dept_status_priority', 'grievances', ['department_id', 'status', 'priority'])
    op.create_index('idx_grievances_lat_lng', 'grievances', ['latitude', 'longitude'])
    op.create_index('idx_grievances_sla_deadline', 'grievances', ['sla_deadline'])

    # GIN Trigram index for full text search
    op.execute(
        "CREATE INDEX idx_grievances_title_desc_gin ON grievances "
        "USING GIN (to_tsvector('english', title || ' ' || description));"
    )

    # 6. Table: grievance_embeddings
    op.create_table(
        'grievance_embeddings',
        sa.Column('grievance_id', sa.String(length=30), primary_key=True),
        sa.Column('embedding', Vector(768), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False, server_default='paraphrase-multilingual-mpnet-base-v2'),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['grievance_id'], ['grievances.id'], ondelete='CASCADE', name='fk_embeddings_grievance_id')
    )
    # HNSW Index for cosine distance vector search
    op.execute(
        "CREATE INDEX idx_embeddings_hnsw ON grievance_embeddings "
        "USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);"
    )

    # 7. Table: grievance_evidence
    op.create_table(
        'grievance_evidence',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('grievance_id', sa.String(length=30), nullable=False),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=20), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('storage_url', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("file_type IN ('image', 'document', 'audio')", name='chk_evidence_file_type'),
        sa.ForeignKeyConstraint(['grievance_id'], ['grievances.id'], ondelete='CASCADE', name='fk_evidence_grievance_id'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='RESTRICT', name='fk_evidence_uploaded_by')
    )
    op.create_index('idx_evidence_grievance_id', 'grievance_evidence', ['grievance_id'])

    # 8. Table: grievance_timeline
    op.create_table(
        'grievance_timeline',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('grievance_id', sa.String(length=30), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('actor_name', sa.String(length=150), nullable=False),
        sa.Column('actor_role', sa.String(length=50), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['grievance_id'], ['grievances.id'], ondelete='CASCADE', name='fk_timeline_grievance_id')
    )
    op.create_index('idx_timeline_grievance_id', 'grievance_timeline', ['grievance_id'])
    op.create_index('idx_timeline_created_at', 'grievance_timeline', ['created_at'])

    # 9. Table: resolution_reports
    op.create_table(
        'resolution_reports',
        sa.Column('grievance_id', sa.String(length=30), primary_key=True),
        sa.Column('officer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('report_text', sa.Text(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('officer_evidence_urls', postgresql.ARRAY(sa.Text()), nullable=False, server_default='{}'),
        sa.Column('ai_verification_confidence', sa.Numeric(precision=4, scale=3), nullable=False, server_default='0.950'),
        sa.Column('citizen_rating', sa.SmallInteger(), nullable=True),
        sa.Column('citizen_comment', sa.Text(), nullable=True),
        sa.Column('verified_by_admin', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.CheckConstraint('citizen_rating IS NULL OR (citizen_rating >= 1 AND citizen_rating <= 5)', name='chk_resolution_citizen_rating'),
        sa.ForeignKeyConstraint(['grievance_id'], ['grievances.id'], ondelete='CASCADE', name='fk_resolution_grievance_id'),
        sa.ForeignKeyConstraint(['officer_id'], ['users.id'], ondelete='RESTRICT', name='fk_resolution_officer_id')
    )
    op.create_index('idx_resolution_officer_id', 'resolution_reports', ['officer_id'])

    # 10. Table: duplicate_clusters
    op.create_table(
        'duplicate_clusters',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('cluster_code', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=300), nullable=False),
        sa.Column('category', sa.String(length=150), nullable=False),
        sa.Column('master_grievance_id', sa.String(length=30), nullable=False),
        sa.Column('similarity_score', sa.Numeric(precision=4, scale=3), nullable=False),
        sa.Column('proximity_meters', sa.Integer(), nullable=False),
        sa.Column('time_span_hours', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='pending_review'),
        sa.Column('ai_recommendation', sa.Text(), nullable=False),
        sa.Column('reasons', postgresql.ARRAY(sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('pending_review', 'merged', 'rejected', 'split')", name='chk_duplicate_cluster_status'),
        sa.ForeignKeyConstraint(['master_grievance_id'], ['grievances.id'], ondelete='RESTRICT', name='fk_clusters_master_grievance'),
        sa.UniqueConstraint('cluster_code', name='uq_duplicate_clusters_code')
    )
    op.create_index('idx_duplicate_clusters_code', 'duplicate_clusters', ['cluster_code'], unique=True)
    op.create_index('idx_duplicate_clusters_category', 'duplicate_clusters', ['category'])

    # 11. Table: cluster_memberships
    op.create_table(
        'cluster_memberships',
        sa.Column('cluster_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('grievance_id', sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(['cluster_id'], ['duplicate_clusters.id'], ondelete='CASCADE', name='fk_memberships_cluster_id'),
        sa.ForeignKeyConstraint(['grievance_id'], ['grievances.id'], ondelete='CASCADE', name='fk_memberships_grievance_id'),
        sa.PrimaryKeyConstraint('cluster_id', 'grievance_id', name='pk_cluster_memberships')
    )
    op.create_index('idx_cluster_memberships_cluster', 'cluster_memberships', ['cluster_id'])
    op.create_index('idx_cluster_memberships_grievance', 'cluster_memberships', ['grievance_id'])

    # 12. Table: hotspots
    op.create_table(
        'hotspots',
        sa.Column('id', sa.String(length=50), primary_key=True),
        sa.Column('title', sa.String(length=250), nullable=False),
        sa.Column('category', sa.String(length=150), nullable=False),
        sa.Column('zone', sa.String(length=100), nullable=False),
        sa.Column('ward', sa.String(length=100), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('radius_meters', sa.Integer(), nullable=False),
        sa.Column('complaint_count', sa.Integer(), nullable=False),
        sa.Column('risk_level', sa.String(length=20), nullable=False),
        sa.Column('risk_score', sa.Integer(), nullable=False),
        sa.Column('trend', sa.String(length=20), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('recommended_action', sa.Text(), nullable=False),
        sa.Column('historical_velocity', postgresql.ARRAY(sa.Integer()), nullable=False, server_default='{}'),
        sa.Column('is_acknowledged', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("risk_level IN ('critical', 'high', 'medium', 'low')", name='chk_hotspot_risk_level'),
        sa.CheckConstraint('risk_score >= 0 AND risk_score <= 100', name='chk_hotspot_risk_score'),
        sa.CheckConstraint("trend IN ('increasing', 'stable', 'decreasing')", name='chk_hotspot_trend')
    )
    op.create_index('idx_hotspots_category', 'hotspots', ['category'])
    op.create_index('idx_hotspots_zone', 'hotspots', ['zone'])
    op.create_index('idx_hotspots_ward', 'hotspots', ['ward'])
    op.create_index('idx_hotspots_detected_at', 'hotspots', ['detected_at'])

    # 13. Table: knowledge_nodes
    op.create_table(
        'knowledge_nodes',
        sa.Column('id', sa.String(length=100), primary_key=True),
        sa.Column('label', sa.String(length=200), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('group_code', sa.String(length=50), nullable=False),
        sa.Column('color_hex', sa.String(length=10), nullable=False, server_default='#1E6BE6'),
        sa.Column('properties', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.CheckConstraint("type IN ('department', 'category', 'asset', 'jurisdiction', 'procedure', 'officer')", name='chk_knowledge_node_type')
    )
    op.create_index('idx_knowledge_nodes_type', 'knowledge_nodes', ['type'])

    # 14. Table: knowledge_edges
    op.create_table(
        'knowledge_edges',
        sa.Column('id', sa.String(length=100), primary_key=True),
        sa.Column('source_node', sa.String(length=100), nullable=False),
        sa.Column('target_node', sa.String(length=100), nullable=False),
        sa.Column('label', sa.String(length=100), nullable=False),
        sa.Column('relation', sa.String(length=50), nullable=False),
        sa.CheckConstraint("relation IN ('handles', 'located_in', 'related_to', 'escalates_to', 'resolves', 'belongs_to')", name='chk_knowledge_edge_relation'),
        sa.ForeignKeyConstraint(['source_node'], ['knowledge_nodes.id'], ondelete='CASCADE', name='fk_edges_source_node'),
        sa.ForeignKeyConstraint(['target_node'], ['knowledge_nodes.id'], ondelete='CASCADE', name='fk_edges_target_node')
    )
    op.create_index('idx_knowledge_edges_source', 'knowledge_edges', ['source_node'])
    op.create_index('idx_knowledge_edges_target', 'knowledge_edges', ['target_node'])

    # 15. Table: audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.String(length=100), nullable=False),
        sa.Column('performed_by', sa.String(length=150), nullable=False),
        sa.Column('user_role', sa.String(length=30), nullable=False),
        sa.Column('details', sa.Text(), nullable=False),
        sa.Column('ip_address', sa.String(length=50), nullable=False, server_default='127.0.0.1')
    )
    op.create_index('idx_audit_logs_timestamp', 'audit_logs', ['timestamp'])
    op.create_index('idx_audit_logs_entity', 'audit_logs', ['entity_type', 'entity_id'])

    # 16. Table: refresh_tokens (15th entity: Auth session persistence)
    op.create_table(
        'refresh_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='fk_refresh_tokens_user_id'),
        sa.UniqueConstraint('token_hash', name='uq_refresh_tokens_hash')
    )
    op.create_index('idx_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    op.create_index('idx_refresh_tokens_hash', 'refresh_tokens', ['token_hash'], unique=True)


def downgrade() -> None:
    # Drop in reverse foreign-key order
    op.drop_table('refresh_tokens')
    op.drop_table('audit_logs')
    op.drop_table('knowledge_edges')
    op.drop_table('knowledge_nodes')
    op.drop_table('hotspots')
    op.drop_table('cluster_memberships')
    op.drop_table('duplicate_clusters')
    op.drop_table('resolution_reports')
    op.drop_table('grievance_timeline')
    op.drop_table('grievance_evidence')
    op.drop_table('grievance_embeddings')
    op.drop_table('grievances')
    op.drop_table('officers')
    op.drop_table('departments')
    op.drop_table('users')
