"""
Test pgvector extension, 768-dimensional vector storage, and HNSW cosine distance indexing.
"""

import pytest
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import check_pgvector_extension
from app.models import User, Department, Grievance, GrievanceEmbedding


@pytest.mark.asyncio
async def test_pgvector_extension_active():
    """Verify pgvector extension query succeeds."""
    is_ok, msg = await check_pgvector_extension()
    assert is_ok is True
    assert "pgvector extension enabled" in msg


@pytest.mark.asyncio
async def test_vector_column_definition(db_session: AsyncSession):
    """Verify the embedding column in PostgreSQL has type vector(768)."""
    query = text("""
        SELECT data_type, udt_name 
        FROM information_schema.columns 
        WHERE table_name = 'grievance_embeddings' AND column_name = 'embedding';
    """)
    result = await db_session.execute(query)
    row = result.fetchone()
    assert row is not None
    assert row[1] == "vector"


@pytest.mark.asyncio
async def test_hnsw_index_exists(db_session: AsyncSession):
    """Verify that idx_embeddings_hnsw is created as an HNSW index in PostgreSQL."""
    query = text("""
        SELECT indexname, indexdef 
        FROM pg_indexes 
        WHERE tablename = 'grievance_embeddings' AND indexname = 'idx_embeddings_hnsw';
    """)
    result = await db_session.execute(query)
    row = result.fetchone()
    assert row is not None
    assert "hnsw" in row[1].lower()
    assert "vector_cosine_ops" in row[1].lower()


@pytest.mark.asyncio
async def test_vector_insert_and_cosine_distance(db_session: AsyncSession):
    """
    Test inserting a 768-dimensional vector via SQLAlchemy ORM and querying nearest neighbors via cosine distance.
    """
    test_user_id = uuid.uuid4()
    test_dept_id = f"test_dept_{uuid.uuid4().hex[:6]}"
    test_grv_id = f"TEST-{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc)
    vec_768 = [0.05] * 768

    try:
        # Create records using SQLAlchemy ORM models
        user = User(
            id=test_user_id,
            name="Vector Tester",
            email=f"vector_{test_user_id.hex[:6]}@example.com",
            password_hash="hash",
            role="citizen",
        )
        dept = Department(
            id=test_dept_id,
            code=test_dept_id[:10],
            name="Vector Testing Dept",
            head_name="Test Head",
        )
        grv = Grievance(
            id=test_grv_id,
            title="Vector Test Issue",
            description="Description for vector verification",
            citizen_id=test_user_id,
            department_id=test_dept_id,
            category="Testing",
            subcategory="Vector Check",
            priority="low",
            status="submitted",
            address="Test Address",
            ward="Ward 1",
            zone="North",
            latitude=28.6139,
            longitude=77.2090,
            expected_resolution_date=now + timedelta(days=2),
            sla_deadline=now + timedelta(days=5),
        )
        emb = GrievanceEmbedding(
            grievance_id=test_grv_id,
            embedding=vec_768,
            model_version="test-model-v1",
        )

        db_session.add_all([user, dept, grv, emb])
        await db_session.commit()

        # Query cosine distance using the pgvector cosine distance operator (<=>)
        res = await db_session.execute(
            select(
                GrievanceEmbedding.grievance_id,
                GrievanceEmbedding.embedding.cosine_distance(vec_768).label("distance"),
            ).where(GrievanceEmbedding.grievance_id == test_grv_id)
        )
        match = res.fetchone()
        assert match is not None
        assert match[0] == test_grv_id
        # Identical vector -> cosine distance should be 0.0 (similarity 1.0)
        assert match[1] < 0.001

    finally:
        # Cleanup
        await db_session.rollback()
        await db_session.execute(text("DELETE FROM grievances WHERE id = :gid;"), {"gid": test_grv_id})
        await db_session.execute(text("DELETE FROM departments WHERE id = :did;"), {"did": test_dept_id})
        await db_session.execute(text("DELETE FROM users WHERE id = :uid;"), {"uid": test_user_id})
        await db_session.commit()
