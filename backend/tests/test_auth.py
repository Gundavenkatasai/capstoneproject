"""
CivicMind AI — Phase 2 Authentication & Security Test Suite
Tests registration, login, rate limiting, JWT lifecycle, rotating refresh tokens,
reuse detection, blacklisting, password reset flow, and profile management.
"""

from datetime import timedelta
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, get_redis_client
from app.models.user import User
from app.models.token import RefreshToken


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient, db_session: AsyncSession):
    """Verify new citizen registration generates Argon2id hash, user, and tokens."""
    payload = {
        "email": "test.citizen.reg@civicmind.gov",
        "password": "StrongPassword123!",
        "name": "Arun Kumar",
        "phone": "+919811122233",
        "ward": "Ward 12 - Indiranagar",
    }
    
    # Clean up user if already exists from previous test
    existing = await db_session.execute(
        select(User).where(User.email == payload["email"])
    )
    u = existing.scalar_one_or_none()
    if u:
        await db_session.delete(u)
        await db_session.commit()

    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()

    assert "token" in data
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == payload["email"]
    assert data["user"]["name"] == payload["name"]
    assert data["user"]["role"] == "citizen"
    assert data["user"]["ward"] == payload["ward"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Verify attempting to register with an existing email returns 400 Bad Request."""
    payload = {
        "email": "citizen@civicmind.gov",  # Seeded account
        "password": "Password123!",
        "name": "Duplicate User",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    """Verify passwords shorter than 8 characters are rejected with 422."""
    payload = {
        "email": "weak.password@civicmind.gov",
        "password": "short",
        "name": "Weak Pass User",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    """Verify malformed email formats are rejected with 422."""
    payload = {
        "email": "not-an-email-address",
        "password": "StrongPassword123!",
        "name": "Invalid Email User",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Verify valid credentials return access token, refresh token, and user payload."""
    login_data = {
        "email": "citizen@civicmind.gov",
        "password": "citizen123",
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["token_type"] == "bearer"
    assert len(data["token"]) > 20
    assert len(data["refresh_token"]) > 20
    assert data["user"]["email"] == "citizen@civicmind.gov"
    assert data["user"]["role"] == "citizen"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """Verify incorrect password returns 401 Unauthorized."""
    login_data = {
        "email": "citizen@civicmind.gov",
        "password": "incorrect_password_xyz",
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401
    assert "invalid email or password" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_email(client: AsyncClient):
    """Verify non-existent user returns 401 Unauthorized."""
    login_data = {
        "email": "ghost.user@civicmind.gov",
        "password": "anypassword123",
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401
    assert "invalid email or password" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_rate_limiting(client: AsyncClient):
    """Verify 5 consecutive failed login attempts trigger 429 rate limit lockout."""
    target_email = "ratelimit.test@civicmind.gov"
    redis = get_redis_client()
    key = f"rate_limit:login:{target_email}"
    await redis.delete(key)

    # 5 failed attempts
    for _ in range(5):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": target_email, "password": "wrongpassword123"},
        )
        assert resp.status_code == 401

    # 6th attempt should be blocked by rate limiter
    resp_blocked = await client.post(
        "/api/v1/auth/login",
        json={"email": target_email, "password": "wrongpassword123"},
    )
    assert resp_blocked.status_code == 429
    assert "too many failed login attempts" in resp_blocked.json()["detail"].lower()
    assert "retry-after" in resp_blocked.headers

    # Clean up key
    await redis.delete(key)


@pytest.mark.asyncio
async def test_login_deactivated_account(client: AsyncClient, db_session: AsyncSession):
    """Verify deactivated user account receives 403 Forbidden upon login."""
    from app.core.security import get_password_hash

    # Clean up previous runs if any
    existing = await db_session.execute(
        select(User).where(User.email == "inactive.user@civicmind.gov")
    )
    u = existing.scalar_one_or_none()
    if u:
        await db_session.delete(u)
        await db_session.commit()

    # Create an inactive user with a valid Argon2id hash
    inactive_user = User(
        email="inactive.user@civicmind.gov",
        name="Inactive Account",
        password_hash=get_password_hash("Password123!"),
        role="citizen",
        is_active=False,
    )
    db_session.add(inactive_user)
    await db_session.commit()

    try:
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "inactive.user@civicmind.gov", "password": "Password123!"},
        )
        assert resp.status_code == 403
        assert "deactivated" in resp.json()["detail"].lower()
    finally:
        await db_session.delete(inactive_user)
        await db_session.commit()


@pytest.mark.asyncio
async def test_get_current_user_profile(client: AsyncClient):
    """Verify GET /api/v1/auth/me returns current authenticated user profile."""
    # Login as admin
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@civicmind.gov", "password": "admin123"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["token"]

    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get("/api/v1/auth/me", headers=headers)
    assert resp.status_code == 200
    profile = resp.json()
    assert profile["email"] == "admin@civicmind.gov"
    assert profile["role"] == "admin"


@pytest.mark.asyncio
async def test_get_me_unauthorized_missing_token(client: AsyncClient):
    """Verify GET /api/v1/auth/me without token returns 401 Unauthorized."""
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401
    assert "not provided" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_me_expired_token(client: AsyncClient):
    """Verify expired JWT access token is rejected with 401."""
    # Generate expired token
    expired_token, _ = create_access_token(
        user_id="00000000-0000-0000-0000-000000000001",
        role="citizen",
        email="expired@civicmind.gov",
        name="Expired User",
        expires_delta=timedelta(seconds=-10),
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    resp = await client.get("/api/v1/auth/me", headers=headers)
    assert resp.status_code == 401
    assert "expired" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_me_malformed_token(client: AsyncClient):
    """Verify malformed JWT returns 401 Unauthorized."""
    headers = {"Authorization": "Bearer forged.invalid.token"}
    resp = await client.get("/api/v1/auth/me", headers=headers)
    assert resp.status_code == 401
    assert "invalid or malformed" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_refresh_token_lifecycle_and_rotation(client: AsyncClient):
    """Verify token refresh rotates the refresh token and yields a new access token."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "officer@civicmind.gov", "password": "officer123"},
    )
    assert login_resp.status_code == 200
    first_access = login_resp.json()["access_token"]
    first_refresh = login_resp.json()["refresh_token"]

    # Request refresh
    refresh_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": first_refresh},
    )
    assert refresh_resp.status_code == 200, refresh_resp.text
    refreshed = refresh_resp.json()

    second_access = refreshed["access_token"]
    second_refresh = refreshed["refresh_token"]

    assert second_access != first_access
    assert second_refresh != first_refresh


@pytest.mark.asyncio
async def test_refresh_token_reuse_detection(client: AsyncClient):
    """
    CRITICAL SECURITY CHECK: Refresh token reuse detection.
    When an already-rotated (revoked) refresh token is reused,
    the entire token family must be revoked and all associated tokens invalidated.
    """
    # 1. Login to get initial token pair
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "citizen@civicmind.gov", "password": "citizen123"},
    )
    initial_refresh = login_resp.json()["refresh_token"]

    # 2. Rotate it legitimately
    rot1_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": initial_refresh},
    )
    assert rot1_resp.status_code == 200
    valid_new_refresh = rot1_resp.json()["refresh_token"]

    # 3. Attacker replays the OLD initial_refresh token
    replay_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": initial_refresh},
    )
    assert replay_resp.status_code == 401
    assert "reuse detected" in replay_resp.json()["detail"].lower()

    # 4. Legitimate user tries to use valid_new_refresh -> MUST NOW FAIL because family was revoked!
    subsequent_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": valid_new_refresh},
    )
    assert subsequent_resp.status_code == 401
    detail_msg = subsequent_resp.json()["detail"].lower()
    assert "reuse detected" in detail_msg or "invalid" in detail_msg


@pytest.mark.asyncio
async def test_logout_and_blacklist_revocation(client: AsyncClient):
    """Verify logout blacklists the access token in Redis and invalidates refresh token."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "officer@civicmind.gov", "password": "officer123"},
    )
    assert login_resp.status_code == 200
    access_token = login_resp.json()["token"]
    refresh_token = login_resp.json()["refresh_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    # Verify token works before logout
    me_resp_before = await client.get("/api/v1/auth/me", headers=headers)
    assert me_resp_before.status_code == 200

    # Execute logout
    logout_resp = await client.post(
        "/api/v1/auth/logout",
        headers=headers,
        json={"refresh_token": refresh_token},
    )
    assert logout_resp.status_code == 200
    msg = logout_resp.json()["message"].lower()
    assert "signed out" in msg or "logged out" in msg

    # Verify access token is now blacklisted and rejected
    me_resp_after = await client.get("/api/v1/auth/me", headers=headers)
    assert me_resp_after.status_code == 401
    assert "revoked" in me_resp_after.json()["detail"].lower()

    # Verify refresh token is also revoked
    refresh_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_resp.status_code == 401


@pytest.mark.asyncio
async def test_password_reset_flow(client: AsyncClient, db_session: AsyncSession):
    """Verify forgot-password and reset-password workflow with single-use token consumption."""
    email = "pwdreset.test@civicmind.gov"
    old_pass = "OldPassword123!"
    new_pass = "BrandNewPassword456!"

    # Clean up previous runs
    existing = await db_session.execute(select(User).where(User.email == email))
    u = existing.scalar_one_or_none()
    if u:
        await db_session.delete(u)
        await db_session.commit()

    # Register user
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": old_pass, "name": "Password Reset Tester"},
    )
    assert reg_resp.status_code == 201

    # Request password reset
    forgot_resp = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": email},
    )
    assert forgot_resp.status_code == 200
    reset_token = forgot_resp.json().get("reset_token")
    assert reset_token is not None, "In dev mode reset_token should be returned"

    # Reset password with valid token
    reset_resp = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": reset_token, "new_password": new_pass},
    )
    assert reset_resp.status_code == 200
    assert "successfully" in reset_resp.json()["message"].lower()

    # Attempting to use the SAME reset token again must fail (single-use guarantee)
    replay_resp = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": reset_token, "new_password": "AnotherPassword789!"},
    )
    assert replay_resp.status_code == 400
    assert "invalid" in replay_resp.json()["detail"].lower() or "already been used" in replay_resp.json()["detail"].lower()

    # Verify old password no longer works
    old_login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": old_pass},
    )
    assert old_login.status_code == 401

    # Verify new password succeeds
    new_login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": new_pass},
    )
    assert new_login.status_code == 200


@pytest.mark.asyncio
async def test_update_user_profile(client: AsyncClient, db_session: AsyncSession):
    """Verify PUT /api/v1/auth/me updates contact and ward information."""
    # Clean up previous run if any
    existing = await db_session.execute(
        select(User).where(User.email == "profile.tester@civicmind.gov")
    )
    u = existing.scalar_one_or_none()
    if u:
        await db_session.delete(u)
        await db_session.commit()

    # Register a dedicated user for profile update test
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "profile.tester@civicmind.gov",
            "password": "SecurePassword123!",
            "name": "Original Name",
            "phone": "+919999900001",
            "ward": "Ward 1",
        },
    )
    assert reg_resp.status_code == 201
    token = reg_resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    update_payload = {
        "name": "Updated Profile Name",
        "phone": "+919999988888",
        "ward": "Ward 99 - Cyber Gateway",
        "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb",
    }

    put_resp = await client.put(
        "/api/v1/auth/me",
        headers=headers,
        json=update_payload,
    )
    assert put_resp.status_code == 200, put_resp.text
    updated = put_resp.json()
    assert updated["name"] == update_payload["name"]
    assert updated["phone"] == update_payload["phone"]
    assert updated["ward"] == update_payload["ward"]
    assert updated["avatar"] == update_payload["avatar_url"]

    # Verify subsequent GET /me reflects the new data
    get_resp = await client.get("/api/v1/auth/me", headers=headers)
    assert get_resp.status_code == 200
    profile = get_resp.json()
    assert profile["name"] == update_payload["name"]
    assert profile["phone"] == update_payload["phone"]
    assert profile["ward"] == update_payload["ward"]
