"""
CivicMind AI — Phase 2 Role-Based Access Control (RBAC) & IDOR Security Test Suite
Tests role enforcement, cross-role denials, object-level user isolation (IDOR protection),
department jurisdiction boundaries, and deactivated account handling.
"""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.officer import Officer
from app.models.department import Department


@pytest.fixture(scope="session")
async def auth_tokens(client: AsyncClient):
    """
    Acquires authentication tokens for the seeded accounts:
    admin, officer, and citizen.
    """
    # 1. Admin login
    admin_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@civicmind.gov", "password": "admin123"},
    )
    assert admin_resp.status_code == 200, f"Admin login failed: {admin_resp.text}"
    admin_data = admin_resp.json()

    # 2. Officer login (assigned to dept_pwd)
    officer_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "officer@civicmind.gov", "password": "officer123"},
    )
    assert officer_resp.status_code == 200, f"Officer login failed: {officer_resp.text}"
    officer_data = officer_resp.json()

    # 3. Citizen login
    citizen_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "citizen@civicmind.gov", "password": "citizen123"},
    )
    assert citizen_resp.status_code == 200, f"Citizen login failed: {citizen_resp.text}"
    citizen_data = citizen_resp.json()

    return {
        "admin": {
            "token": admin_data["token"],
            "user": admin_data["user"],
            "headers": {"Authorization": f"Bearer {admin_data['token']}"},
        },
        "officer": {
            "token": officer_data["token"],
            "user": officer_data["user"],
            "headers": {"Authorization": f"Bearer {officer_data['token']}"},
        },
        "citizen": {
            "token": citizen_data["token"],
            "user": citizen_data["user"],
            "headers": {"Authorization": f"Bearer {citizen_data['token']}"},
        },
    }


# ==============================================================================
# Role Gate Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_citizen_only_gate(client: AsyncClient, auth_tokens: dict):
    """Verify citizen role gate allows citizen and denies officer and admin."""
    # 1. Citizen -> 200 OK
    resp_citizen = await client.get(
        "/api/v1/rbac/citizen-only",
        headers=auth_tokens["citizen"]["headers"],
    )
    assert resp_citizen.status_code == 200
    assert resp_citizen.json()["role"] == "citizen"

    # 2. Officer -> 403 Forbidden
    resp_officer = await client.get(
        "/api/v1/rbac/citizen-only",
        headers=auth_tokens["officer"]["headers"],
    )
    assert resp_officer.status_code == 403
    assert "access denied" in resp_officer.json()["detail"].lower()

    # 3. Admin -> 403 Forbidden
    resp_admin = await client.get(
        "/api/v1/rbac/citizen-only",
        headers=auth_tokens["admin"]["headers"],
    )
    assert resp_admin.status_code == 403


@pytest.mark.asyncio
async def test_officer_only_gate(client: AsyncClient, auth_tokens: dict):
    """Verify officer role gate allows officer and denies citizen and admin."""
    # 1. Officer -> 200 OK
    resp_officer = await client.get(
        "/api/v1/rbac/officer-only",
        headers=auth_tokens["officer"]["headers"],
    )
    assert resp_officer.status_code == 200
    assert resp_officer.json()["role"] == "officer"

    # 2. Citizen -> 403 Forbidden
    resp_citizen = await client.get(
        "/api/v1/rbac/officer-only",
        headers=auth_tokens["citizen"]["headers"],
    )
    assert resp_citizen.status_code == 403

    # 3. Admin -> 403 Forbidden
    resp_admin = await client.get(
        "/api/v1/rbac/officer-only",
        headers=auth_tokens["admin"]["headers"],
    )
    assert resp_admin.status_code == 403


@pytest.mark.asyncio
async def test_admin_only_gate(client: AsyncClient, auth_tokens: dict):
    """Verify admin role gate allows admin and denies citizen and officer."""
    # 1. Admin -> 200 OK
    resp_admin = await client.get(
        "/api/v1/rbac/admin-only",
        headers=auth_tokens["admin"]["headers"],
    )
    assert resp_admin.status_code == 200
    assert resp_admin.json()["role"] == "admin"

    # 2. Citizen -> 403 Forbidden
    resp_citizen = await client.get(
        "/api/v1/rbac/admin-only",
        headers=auth_tokens["citizen"]["headers"],
    )
    assert resp_citizen.status_code == 403

    # 3. Officer -> 403 Forbidden
    resp_officer = await client.get(
        "/api/v1/rbac/admin-only",
        headers=auth_tokens["officer"]["headers"],
    )
    assert resp_officer.status_code == 403


# ==============================================================================
# Object-Level Authorization & IDOR Protection Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_object_level_user_access_idor_protection(
    client: AsyncClient,
    auth_tokens: dict,
    db_session: AsyncSession,
):
    """
    CRITICAL SECURITY CHECK: Insecure Direct Object Reference (IDOR) Protection.
    - Citizen A accessing Citizen A's records: ALLOW (200)
    - Citizen A accessing Citizen B's records: FORBIDDEN (403)
    - Officer accessing Citizen A's records: FORBIDDEN (403)
    - Admin accessing Citizen A's records: ALLOW (200) - elevated supervisor
    """
    citizen_a_id = auth_tokens["citizen"]["user"]["id"]
    random_other_user_id = str(uuid.uuid4())

    # 1. Citizen A accessing own record -> 200 OK
    resp_own = await client.get(
        f"/api/v1/rbac/users/{citizen_a_id}/records",
        headers=auth_tokens["citizen"]["headers"],
    )
    assert resp_own.status_code == 200
    assert citizen_a_id in resp_own.json()["message"]

    # 2. Citizen A attempting to access Citizen B's record (IDOR attempt) -> 403 Forbidden
    resp_idor = await client.get(
        f"/api/v1/rbac/users/{random_other_user_id}/records",
        headers=auth_tokens["citizen"]["headers"],
    )
    assert resp_idor.status_code == 403
    assert "access forbidden" in resp_idor.json()["detail"].lower()

    # 3. Officer attempting to access Citizen A's personal record -> 403 Forbidden
    resp_officer_idor = await client.get(
        f"/api/v1/rbac/users/{citizen_a_id}/records",
        headers=auth_tokens["officer"]["headers"],
    )
    assert resp_officer_idor.status_code == 403

    # 4. Admin accessing Citizen A's record -> 200 OK (Supervisory privilege)
    resp_admin = await client.get(
        f"/api/v1/rbac/users/{citizen_a_id}/records",
        headers=auth_tokens["admin"]["headers"],
    )
    assert resp_admin.status_code == 200
    assert resp_admin.json()["caller_role"] == "admin"


# ==============================================================================
# Department Jurisdiction Guard Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_department_jurisdiction_guards(client: AsyncClient, auth_tokens: dict):
    """
    CRITICAL SECURITY CHECK: Departmental Silo Isolation.
    - Officer in 'dept_pwd' accessing 'dept_pwd': ALLOW (200)
    - Officer in 'dept_pwd' attempting to access 'dept_sanitation': FORBIDDEN (403)
    - Citizen attempting to access any department: FORBIDDEN (403)
    - Admin accessing any department: ALLOW (200) - citywide jurisdiction
    """
    assigned_dept = "dept_pwd"
    unassigned_dept = "dept_sanitation"

    # 1. Officer accessing their own assigned department -> 200 OK
    resp_assigned = await client.get(
        f"/api/v1/rbac/departments/{assigned_dept}/confidential",
        headers=auth_tokens["officer"]["headers"],
    )
    assert resp_assigned.status_code == 200
    assert assigned_dept in resp_assigned.json()["message"]

    # 2. Officer attempting to inspect unassigned department -> 403 Forbidden
    resp_unassigned = await client.get(
        f"/api/v1/rbac/departments/{unassigned_dept}/confidential",
        headers=auth_tokens["officer"]["headers"],
    )
    assert resp_unassigned.status_code == 403
    assert "access forbidden" in resp_unassigned.json()["detail"].lower()

    # 3. Citizen attempting to access department confidential data -> 403 Forbidden
    resp_citizen = await client.get(
        f"/api/v1/rbac/departments/{assigned_dept}/confidential",
        headers=auth_tokens["citizen"]["headers"],
    )
    assert resp_citizen.status_code == 403

    # 4. Admin accessing any department -> 200 OK (Global oversight)
    resp_admin = await client.get(
        f"/api/v1/rbac/departments/{unassigned_dept}/confidential",
        headers=auth_tokens["admin"]["headers"],
    )
    assert resp_admin.status_code == 200
    assert unassigned_dept in resp_admin.json()["message"]


# ==============================================================================
# Deactivated Account Security Test
# ==============================================================================

@pytest.mark.asyncio
async def test_deactivated_user_token_rejection(
    client: AsyncClient,
    db_session: AsyncSession,
):
    """
    Verify that if a user account is deactivated in the database,
    all subsequent requests with an existing valid JWT return 403 Forbidden.
    """
    # Clean up previous run if any
    existing = await db_session.execute(
        select(User).where(User.email == "deactivate.test@civicmind.gov")
    )
    u = existing.scalar_one_or_none()
    if u:
        await db_session.delete(u)
        await db_session.commit()

    # 1. Register a test user
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "deactivate.test@civicmind.gov",
            "password": "Password123!",
            "name": "To Be Deactivated",
        },
    )
    assert reg_resp.status_code == 201
    user_id = reg_resp.json()["user"]["id"]
    token = reg_resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Verify token works initially
    check1 = await client.get("/api/v1/auth/me", headers=headers)
    assert check1.status_code == 200

    # 3. Deactivate user in database
    result = await db_session.execute(
        select(User).where(User.id == uuid.UUID(user_id))
    )
    user = result.scalar_one()
    user.is_active = False
    await db_session.commit()

    # 4. Subsequent request must be rejected with 403 Forbidden
    check2 = await client.get("/api/v1/auth/me", headers=headers)
    assert check2.status_code == 403
    assert "deactivated" in check2.json()["detail"].lower()
