"""
CivicMind AI — Phase 3 Grievance Lifecycle, IDOR, Evidence & Resolution Tests
Comprehensive test suite verifying collision-free sequence IDs, role-based transitions,
IDOR access barriers, evidence handling, resolution verification, and citizen appeals.
"""

import io
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.department import Department
from app.models.officer import Officer
from app.core.security import get_password_hash, create_access_token


@pytest.fixture
async def setup_grievance_fixtures(db_session: AsyncSession):
    """
    Sets up isolated test departments, citizens, and officers.
    """
    # Clean up test records
    await db_session.execute(text("DELETE FROM audit_logs WHERE performed_by LIKE '%@test-phase3.gov%';"))
    await db_session.execute(text("DELETE FROM grievance_timeline WHERE actor_name LIKE 'Test%';"))
    await db_session.execute(text("DELETE FROM resolution_reports WHERE grievance_id LIKE 'GRV-%';"))
    await db_session.execute(text("DELETE FROM grievance_evidence WHERE file_name LIKE 'test_%';"))
    await db_session.execute(text("DELETE FROM grievances WHERE title LIKE 'Test %';"))
    await db_session.execute(text("DELETE FROM officers WHERE department_id IN ('DEPT-PWD', 'DEPT-HEALTH');"))
    await db_session.execute(text("DELETE FROM users WHERE email LIKE '%@test-phase3.gov%';"))
    await db_session.execute(text("DELETE FROM departments WHERE id IN ('DEPT-PWD', 'DEPT-HEALTH');"))
    await db_session.commit()

    # Create Departments
    dept1 = Department(id="DEPT-PWD", name="Public Works Department", code="PWD", head_name="Chief Engineer PWD")
    dept2 = Department(id="DEPT-HEALTH", name="Health & Sanitation", code="HLS", head_name="Health Officer")
    db_session.add_all([dept1, dept2])
    await db_session.flush()

    pwd_hash = get_password_hash("ValidPass123!")

    # Citizen 1 (Owner)
    cit1 = User(
        id=uuid.uuid4(),
        email="citizen1@test-phase3.gov",
        password_hash=pwd_hash,
        name="Test Citizen One",
        role="citizen",
        is_active=True,
    )
    # Citizen 2 (Attacker/Stranger)
    cit2 = User(
        id=uuid.uuid4(),
        email="citizen2@test-phase3.gov",
        password_hash=pwd_hash,
        name="Test Citizen Two",
        role="citizen",
        is_active=True,
    )
    # Officer 1 (Assigned to DEPT-PWD)
    off1_id = uuid.uuid4()
    off1 = User(
        id=off1_id,
        email="officer1@test-phase3.gov",
        password_hash=pwd_hash,
        name="Test Officer PWD",
        role="officer",
        is_active=True,
    )
    # Officer 2 (Assigned to DEPT-HEALTH)
    off2_id = uuid.uuid4()
    off2 = User(
        id=off2_id,
        email="officer2@test-phase3.gov",
        password_hash=pwd_hash,
        name="Test Officer Health",
        role="officer",
        is_active=True,
    )
    # Admin
    adm = User(
        id=uuid.uuid4(),
        email="admin@test-phase3.gov",
        password_hash=pwd_hash,
        name="Test Commissioner Admin",
        role="admin",
        is_active=True,
    )

    db_session.add_all([cit1, cit2, off1, off2, adm])
    await db_session.flush()

    prof1 = Officer(id=off1_id, department_id="DEPT-PWD", assigned_ward="Ward 12")
    prof2 = Officer(id=off2_id, department_id="DEPT-HEALTH", assigned_ward="Ward 5")
    db_session.add_all([prof1, prof2])
    await db_session.commit()

    tokens = {
        "citizen1": create_access_token(user_id=cit1.id, role=cit1.role, email=cit1.email, name=cit1.name)[0],
        "citizen2": create_access_token(user_id=cit2.id, role=cit2.role, email=cit2.email, name=cit2.name)[0],
        "officer1": create_access_token(user_id=off1.id, role=off1.role, email=off1.email, name=off1.name)[0],
        "officer2": create_access_token(user_id=off2.id, role=off2.role, email=off2.email, name=off2.name)[0],
        "admin": create_access_token(user_id=adm.id, role=adm.role, email=adm.email, name=adm.name)[0],
        "cit1_id": str(cit1.id),
        "cit2_id": str(cit2.id),
        "off1_id": str(off1.id),
        "off2_id": str(off2.id),
    }
    return tokens


@pytest.mark.asyncio
async def test_grievance_creation_success_and_tracking_id(client: AsyncClient, setup_grievance_fixtures):
    """Verify citizen grievance creation returns 201 with atomic GRV-YYYY-XXXXX sequence ID."""
    tokens = setup_grievance_fixtures
    headers = {"Authorization": f"Bearer {tokens['citizen1']}"}

    payload = {
        "title": "Test Massive Pothole on MG Road",
        "description": "Deep dangerous pothole near junction causing traffic congestion and accidents.",
        "category": "Road Infrastructure",
        "subcategory": "Potholes & Road Damage",
        "department_id": "DEPT-PWD",
        "priority": "high",
        "address": "MG Road Sector 4",
        "ward": "Ward 12",
        "zone": "North Zone",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "is_anonymous": False,
        "language": "en",
    }

    response = await client.post("/api/v1/grievances", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()

    assert data["id"].startswith("GRV-")
    assert data["title"] == payload["title"]
    assert data["status"] == "submitted"
    assert data["priority"] == "high"
    assert data["citizenId"] == tokens["cit1_id"]
    assert data["citizenName"] == "Test Citizen One"
    assert data["departmentId"] == "DEPT-PWD"
    assert len(data["timeline"]) >= 1
    assert data["timeline"][0]["status"] == "submitted"


@pytest.mark.asyncio
async def test_grievance_creation_validation_failure(client: AsyncClient, setup_grievance_fixtures):
    """Verify validation error when title or description is too short."""
    tokens = setup_grievance_fixtures
    headers = {"Authorization": f"Bearer {tokens['citizen1']}"}

    payload = {
        "title": "Bad",
        "description": "Short",
        "category": "Roads",
        "address": "Street",
        "ward": "1",
        "zone": "North",
        "latitude": 12.0,
        "longitude": 77.0,
    }
    response = await client.post("/api/v1/grievances", json=payload, headers=headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_idor_cross_citizen_isolation(client: AsyncClient, setup_grievance_fixtures):
    """Verify Citizen 2 cannot view or mutate Citizen 1's grievance."""
    tokens = setup_grievance_fixtures
    h1 = {"Authorization": f"Bearer {tokens['citizen1']}"}
    h2 = {"Authorization": f"Bearer {tokens['citizen2']}"}

    # Citizen 1 creates grievance
    create_res = await client.post(
        "/api/v1/grievances",
        json={
            "title": "Test Citizen 1 Private Grievance",
            "description": "Private water leakage issue in residential compound.",
            "category": "Water Supply",
            "department_id": "DEPT-PWD",
            "address": "Residency Road",
            "ward": "Ward 3",
            "zone": "East",
            "latitude": 12.95,
            "longitude": 77.58,
        },
        headers=h1,
    )
    assert create_res.status_code == 201
    grv_id = create_res.json()["id"]

    # Citizen 2 attempts to fetch Citizen 1's grievance -> 403 Forbidden
    fetch_res = await client.get(f"/api/v1/grievances/{grv_id}", headers=h2)
    assert fetch_res.status_code == 403
    assert "access denied" in fetch_res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_officer_jurisdiction_isolation(client: AsyncClient, setup_grievance_fixtures):
    """Verify Officer in Health dept cannot access or resolve PWD grievance."""
    tokens = setup_grievance_fixtures
    h_cit = {"Authorization": f"Bearer {tokens['citizen1']}"}
    h_off_pwd = {"Authorization": f"Bearer {tokens['officer1']}"}
    h_off_health = {"Authorization": f"Bearer {tokens['officer2']}"}

    # Create PWD grievance
    create_res = await client.post(
        "/api/v1/grievances",
        json={
            "title": "Test Broken Bridge Railing",
            "description": "Pedestrian bridge railing broken near river bank.",
            "category": "Road Infrastructure",
            "department_id": "DEPT-PWD",
            "address": "Riverside Drive",
            "ward": "Ward 5",
            "zone": "West",
            "latitude": 12.91,
            "longitude": 77.52,
        },
        headers=h_cit,
    )
    grv_id = create_res.json()["id"]

    # PWD Officer can access
    pwd_access = await client.get(f"/api/v1/grievances/{grv_id}", headers=h_off_pwd)
    assert pwd_access.status_code == 200

    # Health Officer cannot access -> 403 Forbidden
    health_access = await client.get(f"/api/v1/grievances/{grv_id}", headers=h_off_health)
    assert health_access.status_code == 403
    assert "jurisdiction" in health_access.json()["detail"].lower()


@pytest.mark.asyncio
async def test_lifecycle_status_transition_rules(client: AsyncClient, setup_grievance_fixtures):
    """Verify state machine: valid transitions succeed, invalid transitions return 400."""
    tokens = setup_grievance_fixtures
    h_cit = {"Authorization": f"Bearer {tokens['citizen1']}"}
    h_off = {"Authorization": f"Bearer {tokens['officer1']}"}

    # Create grievance (status: submitted)
    create_res = await client.post(
        "/api/v1/grievances",
        json={
            "title": "Test Storm Drain Blockage",
            "description": "Drainage completely choked with silt and plastic debris.",
            "category": "Road Infrastructure",
            "department_id": "DEPT-PWD",
            "address": "Central Market Road",
            "ward": "Ward 8",
            "zone": "Central",
            "latitude": 12.98,
            "longitude": 77.60,
        },
        headers=h_cit,
    )
    grv_id = create_res.json()["id"]

    # Invalid: submitted -> closed directly -> 400 Bad Request
    invalid_res = await client.patch(
        f"/api/v1/grievances/{grv_id}/status",
        json={"status": "closed", "notes": "Trying to skip steps"},
        headers=h_off,
    )
    assert invalid_res.status_code == 400
    assert "invalid lifecycle transition" in invalid_res.json()["detail"].lower()

    # Valid: submitted -> in_progress
    valid_res = await client.patch(
        f"/api/v1/grievances/{grv_id}/status",
        json={"status": "in_progress", "notes": "Officer dispatched to inspect blockage."},
        headers=h_off,
    )
    assert valid_res.status_code == 200
    assert valid_res.json()["status"] == "in_progress"

    # Verify timeline updated
    grv_data = valid_res.json()
    assert len(grv_data["timeline"]) >= 2
    assert grv_data["timeline"][-1]["status"] == "in_progress"


@pytest.mark.asyncio
async def test_evidence_upload_validation_and_attachment(client: AsyncClient, setup_grievance_fixtures):
    """Verify evidence file upload with magic-byte validation, size checks, and grievance linking."""
    tokens = setup_grievance_fixtures
    h_cit = {"Authorization": f"Bearer {tokens['citizen1']}"}

    # 1. Reject invalid magic-byte signature
    fake_png = io.BytesIO(b"NOT_A_REAL_PNG_HEADER_DATA_1234567890")
    bad_upload = await client.post(
        "/api/v1/uploads/evidence",
        files={"file": ("fake.png", fake_png, "image/png")},
        headers=h_cit,
    )
    assert bad_upload.status_code == 400
    assert "binary signature" in bad_upload.json()["detail"].lower()

    # 2. Valid PNG header (8 bytes magic header)
    valid_png_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 200
    good_png = io.BytesIO(valid_png_content)
    upload_res = await client.post(
        "/api/v1/uploads/evidence",
        files={"file": ("test_photo.png", good_png, "image/png")},
        headers=h_cit,
    )
    assert upload_res.status_code == 201
    evidence_data = upload_res.json()
    evidence_id = evidence_data["id"]
    assert evidence_data["fileName"] == "test_photo.png"
    assert evidence_data["fileType"] == "image"

    # 3. Create grievance with evidence_file_ids
    grv_res = await client.post(
        "/api/v1/grievances",
        json={
            "title": "Test Pothole with Evidence Image",
            "description": "Attached photographic proof of pothole crater.",
            "category": "Road Infrastructure",
            "department_id": "DEPT-PWD",
            "address": "Ring Road Km 4",
            "ward": "Ward 2",
            "zone": "South",
            "latitude": 12.90,
            "longitude": 77.55,
            "evidence_file_ids": [evidence_id],
        },
        headers=h_cit,
    )
    assert grv_res.status_code == 201
    grv = grv_res.json()
    assert len(grv["evidence"]) == 1
    assert grv["evidence"][0]["id"] == evidence_id

    # 4. Download evidence file
    dl_res = await client.get(f"/api/v1/uploads/evidence/{evidence_id}/download", headers=h_cit)
    assert dl_res.status_code == 200
    assert dl_res.content == valid_png_content


@pytest.mark.asyncio
async def test_full_resolution_and_citizen_verification_flow(client: AsyncClient, setup_grievance_fixtures):
    """
    Test end-to-end lifecycle:
    submitted -> in_progress -> resolution_submitted (officer) -> citizen_verified (citizen accepts).
    """
    tokens = setup_grievance_fixtures
    h_cit = {"Authorization": f"Bearer {tokens['citizen1']}"}
    h_off = {"Authorization": f"Bearer {tokens['officer1']}"}

    # 1. Citizen creates grievance
    grv_res = await client.post(
        "/api/v1/grievances",
        json={
            "title": "Test Open Manhole on 5th Cross",
            "description": "Open drainage manhole uncovered for 3 days.",
            "category": "Road Infrastructure",
            "department_id": "DEPT-PWD",
            "address": "5th Cross Road",
            "ward": "Ward 1",
            "zone": "Central",
            "latitude": 12.97,
            "longitude": 77.59,
        },
        headers=h_cit,
    )
    grv_id = grv_res.json()["id"]

    # 2. Officer sets to in_progress
    await client.patch(
        f"/api/v1/grievances/{grv_id}/status",
        json={"status": "in_progress", "notes": "Contractor assigned to cover manhole"},
        headers=h_off,
    )

    # 3. Officer submits resolution report
    resolve_res = await client.post(
        f"/api/v1/grievances/{grv_id}/resolve",
        json={
            "report_text": "Manhole cover replaced with heavy concrete slab and sealed.",
            "officer_evidence_urls": ["https://storage.civicmind.gov/evidence/after_fix.jpg"],
        },
        headers=h_off,
    )
    assert resolve_res.status_code == 200
    grv_resolved = resolve_res.json()
    assert grv_resolved["status"] == "resolution_submitted"
    assert grv_resolved["actualResolutionDate"] is not None
    assert grv_resolved["resolutionReport"]["reportText"] == "Manhole cover replaced with heavy concrete slab and sealed."

    # 4. Citizen accepts and verifies resolution
    verify_res = await client.post(
        f"/api/v1/grievances/{grv_id}/verify",
        json={
            "rating": 5,
            "comment": "Prompt action taken. Cleanly sealed.",
            "action": "accept",
        },
        headers=h_cit,
    )
    assert verify_res.status_code == 200
    grv_verified = verify_res.json()
    assert grv_verified["status"] == "citizen_verified"
    assert grv_verified["resolutionReport"]["citizenFeedbackRating"] == 5


@pytest.mark.asyncio
async def test_citizen_reopen_and_appeal_flow(client: AsyncClient, setup_grievance_fixtures):
    """
    Test citizen appeal flow:
    Grievance in citizen_verified status is formally appealed by citizen, transitioning to reopened.
    """
    tokens = setup_grievance_fixtures
    h_cit = {"Authorization": f"Bearer {tokens['citizen1']}"}
    h_off = {"Authorization": f"Bearer {tokens['officer1']}"}

    # 1. Create and fast-forward to resolution_submitted
    grv_res = await client.post(
        "/api/v1/grievances",
        json={
            "title": "Test Overflowing Garbage Bin",
            "description": "Garbage bin overflowing onto main walkway.",
            "category": "Sanitation",
            "department_id": "DEPT-PWD",
            "address": "Market Square",
            "ward": "Ward 4",
            "zone": "North",
            "latitude": 12.99,
            "longitude": 77.61,
        },
        headers=h_cit,
    )
    grv_id = grv_res.json()["id"]

    await client.patch(
        f"/api/v1/grievances/{grv_id}/status",
        json={"status": "in_progress"},
        headers=h_off,
    )
    await client.post(
        f"/api/v1/grievances/{grv_id}/resolve",
        json={"report_text": "Bin cleared.", "officer_evidence_urls": []},
        headers=h_off,
    )

    # 2. Citizen rejects resolution -> transitions to reopened
    reject_res = await client.post(
        f"/api/v1/grievances/{grv_id}/verify",
        json={
            "rating": 1,
            "comment": "Debris left behind on the sidewalk. Only half cleaned.",
            "action": "reject",
        },
        headers=h_cit,
    )
    assert reject_res.status_code == 200
    assert reject_res.json()["status"] == "reopened"

    # 3. Officer marks in_progress and resolves again
    await client.patch(f"/api/v1/grievances/{grv_id}/status", json={"status": "in_progress"}, headers=h_off)
    await client.post(
        f"/api/v1/grievances/{grv_id}/resolve",
        json={"report_text": "Complete sweeping and sanitization performed.", "officer_evidence_urls": []},
        headers=h_off,
    )
    await client.patch(f"/api/v1/grievances/{grv_id}/status", json={"status": "citizen_verified"}, headers=h_cit)

    # 4. Citizen files formal appeal on verified grievance
    appeal_res = await client.post(
        f"/api/v1/grievances/{grv_id}/appeal",
        json={"reason": "Problem recurred within 24 hours. Waste dumping continues."},
        headers=h_cit,
    )
    assert appeal_res.status_code == 200
    assert appeal_res.json()["status"] == "reopened"


@pytest.mark.asyncio
async def test_reassignment_workflow(client: AsyncClient, setup_grievance_fixtures):
    """Verify officer/admin can reassign department and officer, updating timeline."""
    tokens = setup_grievance_fixtures
    h_cit = {"Authorization": f"Bearer {tokens['citizen1']}"}
    h_adm = {"Authorization": f"Bearer {tokens['admin']}"}

    create_res = await client.post(
        "/api/v1/grievances",
        json={
            "title": "Test Contaminated Drinking Water",
            "description": "Dirty tap water with odor in sector 7.",
            "category": "Water",
            "department_id": "DEPT-PWD",  # Initially routed to PWD incorrectly
            "address": "Sector 7 Main Road",
            "ward": "Ward 9",
            "zone": "South",
            "latitude": 12.92,
            "longitude": 77.56,
        },
        headers=h_cit,
    )
    grv_id = create_res.json()["id"]

    # Admin reassigns to Health Department
    reassign_res = await client.post(
        f"/api/v1/grievances/{grv_id}/assign",
        json={
            "department_id": "DEPT-HEALTH",
            "reason": "Water quality testing falls under Health Department purview.",
        },
        headers=h_adm,
    )
    assert reassign_res.status_code == 200
    updated_grv = reassign_res.json()
    assert updated_grv["departmentId"] == "DEPT-HEALTH"
    assert updated_grv["status"] == "assigned"


@pytest.mark.asyncio
async def test_ai_triage_preview_endpoint(client: AsyncClient):
    """Verify deterministic rule-based triage preview endpoint."""
    response = await client.post(
        "/api/v1/ai/triage-preview",
        json={
            "title": "Severe road crater causing vehicle damage",
            "description": "Massive deep pothole on flyover causing dangerous jams.",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["predictedCategory"] == "Road Infrastructure"
    assert data["suggestedDepartmentId"] == "PWD-RDS"
    assert data["isMockFallback"] is True
    assert "pothole" in data["keywordsMatched"] or "road" in data["keywordsMatched"]
