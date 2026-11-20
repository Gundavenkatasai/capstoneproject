"""
Test Alembic migration tracking and schema integrity.
"""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_alembic_version_table(db_session: AsyncSession):
    """Verify alembic_version table exists and tracks current revision."""
    result = await db_session.execute(text("SELECT version_num FROM alembic_version;"))
    rev = result.scalar()
    assert rev in ("0001_initial_schema", "0002_refresh_token_family", "0003_add_google_auth_fields", "0004_grievance_lifecycle", "0005_outbox_events")
    assert rev == "0005_outbox_events"


@pytest.mark.asyncio
async def test_all_15_tables_exist_in_database(db_session: AsyncSession):
    """Verify all application tables exist in the PostgreSQL information_schema."""
    result = await db_session.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    """))
    existing_tables = {row[0] for row in result.fetchall()}

    expected_tables = {
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

    assert expected_tables.issubset(existing_tables)


@pytest.mark.asyncio
async def test_migration_0002_refresh_tokens_family_columns(db_session: AsyncSession):
    """Verify migration 0002 added family_id, user_agent, and ip_address to refresh_tokens."""
    result = await db_session.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'refresh_tokens';
    """))
    cols = {row[0] for row in result.fetchall()}
    assert "family_id" in cols
    assert "user_agent" in cols
    assert "ip_address" in cols


@pytest.mark.asyncio
async def test_migration_0003_users_google_auth_columns(db_session: AsyncSession):
    """Verify migration 0003 added auth_provider and google_id to users."""
    result = await db_session.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'users';
    """))
    cols = {row[0] for row in result.fetchall()}
    assert "auth_provider" in cols
    assert "google_id" in cols


@pytest.mark.asyncio
async def test_migration_0004_grievance_lifecycle(db_session: AsyncSession):
    """Verify migration 0004 created tracking sequence and made evidence grievance_id nullable."""
    seq_result = await db_session.execute(text("""
        SELECT sequence_name FROM information_schema.sequences WHERE sequence_name = 'grievance_tracking_seq';
    """))
    seq_name = seq_result.scalar()
    assert seq_name == "grievance_tracking_seq"

    col_result = await db_session.execute(text("""
        SELECT is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'grievance_evidence' AND column_name = 'grievance_id';
    """))
    is_nullable = col_result.scalar()
    assert is_nullable == "YES"


@pytest.mark.asyncio
async def test_migration_0005_outbox_events(db_session: AsyncSession):
    """Verify migration 0005 created outbox_events table with all required columns."""
    result = await db_session.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'outbox_events';
    """))
    cols = {row[0] for row in result.fetchall()}
    assert "id" in cols
    assert "event_type" in cols
    assert "aggregate_type" in cols
    assert "aggregate_id" in cols
    assert "payload" in cols
    assert "status" in cols
    assert "attempts" in cols
    assert "max_attempts" in cols
    assert "correlation_id" in cols
    assert "scheduled_for" in cols
    assert "processed_at" in cols


