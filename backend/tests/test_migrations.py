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
    assert rev == "0001_initial_schema"


@pytest.mark.asyncio
async def test_all_15_tables_exist_in_database(db_session: AsyncSession):
    """Verify all 15 application tables exist in the PostgreSQL information_schema."""
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
    }

    assert expected_tables.issubset(existing_tables)
