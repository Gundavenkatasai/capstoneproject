"""
CivicMind AI — Authentication Business Logic Service
Handles login validation, Argon2id verification, rotating refresh tokens with reuse detection,
session blacklisting, password reset token single-use mechanics, and security audit logging.
"""

import uuid
import urllib.parse
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import httpx
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from app.core.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    generate_secure_random_token,
    hash_token,
    create_access_token,
    blacklist_token,
    check_login_rate_limit,
    record_login_attempt,
    create_password_reset_token,
    verify_and_consume_password_reset_token,
)
from app.models.user import User
from app.models.officer import Officer
from app.models.token import RefreshToken
from app.models.audit import AuditLog
from app.schemas.auth import (
    UserPublic,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RefreshTokenResponse,
    ForgotPasswordResponse,
    UserProfileUpdateRequest,
    GoogleAuthRequest,
    GoogleAuthUrlResponse,
)


def _serialize_user(user: User) -> UserPublic:
    """Helper to convert User ORM instance into UserPublic schema."""
    dept_id = None
    if user.role == "officer" and user.officer_profile:
        dept_id = user.officer_profile.department_id

    return UserPublic(
        id=str(user.id),
        name=user.name,
        email=user.email,
        role=user.role,
        department=dept_id,
        phone=user.phone,
        ward=user.ward,
        avatar=user.avatar_url,
        badge=user.badge,
        auth_provider=getattr(user, "auth_provider", "local"),
    )


async def login(
    db: AsyncSession,
    creds: LoginRequest,
    client_ip: str = "127.0.0.1",
    user_agent: Optional[str] = None,
) -> LoginResponse:
    """
    Authenticate user credentials, enforce rate-limiting, issue JWT access token
    and a cryptographically secure refresh token family.
    """
    normalized_email = creds.email.lower().strip()

    # 1. Rate-limiting check: Prevent brute-force password guessing
    allowed, retry_after = await check_login_rate_limit(normalized_email, max_attempts=5, window_seconds=300)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed login attempts. Please try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )

    # 2. Query user from database with officer profile eagerly loaded
    result = await db.execute(
        select(User)
        .options(selectinload(User.officer_profile))
        .where(User.email == normalized_email)
    )
    user = result.scalar_one_or_none()

    # 3. Verify user existence and password hash
    # Note: verify_password is executed even if user is None via dummy hash to mitigate timing attacks
    is_valid_pwd = False
    if user:
        is_valid_pwd = verify_password(creds.password, user.password_hash)

    if not user or not is_valid_pwd:
        await record_login_attempt(normalized_email, success=False, window_seconds=300)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. Check account active status
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated. Please contact an administrator.",
        )

    # 5. Clear rate limit upon successful authentication
    await record_login_attempt(normalized_email, success=True)

    # 6. Issue access token
    access_token_str, expire_dt = create_access_token(
        user_id=user.id,
        role=user.role,
        email=user.email,
        name=user.name,
    )
    expires_in_sec = int((expire_dt - datetime.now(timezone.utc)).total_seconds())

    # 7. Issue rotating refresh token with a new rotation family
    raw_refresh_token = generate_secure_random_token(48)
    refresh_hash = hash_token(raw_refresh_token)

    refresh_days = settings.REFRESH_TOKEN_EXPIRE_DAYS * (4 if creds.rememberMe else 1)
    refresh_expire_dt = datetime.now(timezone.utc) + timedelta(days=refresh_days)
    family_id = uuid.uuid4()

    refresh_token_record = RefreshToken(
        id=uuid.uuid4(),
        user_id=user.id,
        token_hash=refresh_hash,
        family_id=family_id,
        expires_at=refresh_expire_dt,
        is_revoked=False,
        user_agent=user_agent[:255] if user_agent else None,
        ip_address=client_ip[:50] if client_ip else "127.0.0.1",
    )
    db.add(refresh_token_record)

    # 8. Record audit log
    audit_entry = AuditLog(
        id=uuid.uuid4(),
        action="USER_LOGIN",
        entity_type="user",
        entity_id=str(user.id),
        performed_by=user.name,
        user_role=user.role,
        details=f"Successful login for role '{user.role}'. IP: {client_ip}",
        ip_address=client_ip[:50] if client_ip else "127.0.0.1",
    )
    db.add(audit_entry)

    await db.commit()

    return LoginResponse(
        token=access_token_str,
        access_token=access_token_str,
        refresh_token=raw_refresh_token,
        token_type="bearer",
        expires_in=expires_in_sec,
        user=_serialize_user(user),
    )


async def register(
    db: AsyncSession,
    data: RegisterRequest,
    client_ip: str = "127.0.0.1",
    user_agent: Optional[str] = None,
) -> LoginResponse:
    """
    Register a new user account with Argon2id password hashing,
    and return an immediate login session token.
    """
    normalized_email = data.email.lower().strip()

    # Check for existing user
    existing = await db.execute(select(User.id).where(User.email == normalized_email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    # Hash password with Argon2id
    hashed_pwd = get_password_hash(data.password)

    new_user_id = uuid.uuid4()
    new_user = User(
        id=new_user_id,
        name=data.name.strip(),
        email=normalized_email,
        password_hash=hashed_pwd,
        role=data.role,
        phone=data.phone.strip() if data.phone else None,
        ward=data.ward.strip() if data.ward else None,
        is_active=True,
    )
    db.add(new_user)

    # If registering as an officer, initialize roster extension
    if data.role == "officer":
        officer_ext = Officer(
            id=new_user_id,
            department_id="dept_pwd",  # default department allocation
            assigned_ward=data.ward or "Ward 1 (Central)",
            active_cases=0,
            resolved_mtd=0,
            avg_resolution_hours=48.0,
            rating=5.00,
            status="active",
        )
        db.add(officer_ext)

    # Issue tokens
    access_token_str, expire_dt = create_access_token(
        user_id=new_user_id,
        role=data.role,
        email=normalized_email,
        name=data.name.strip(),
    )
    expires_in_sec = int((expire_dt - datetime.now(timezone.utc)).total_seconds())

    raw_refresh_token = generate_secure_random_token(48)
    refresh_hash = hash_token(raw_refresh_token)
    refresh_expire_dt = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    refresh_token_record = RefreshToken(
        id=uuid.uuid4(),
        user_id=new_user_id,
        token_hash=refresh_hash,
        family_id=uuid.uuid4(),
        expires_at=refresh_expire_dt,
        is_revoked=False,
        user_agent=user_agent[:255] if user_agent else None,
        ip_address=client_ip[:50] if client_ip else "127.0.0.1",
    )
    db.add(refresh_token_record)

    # Audit log
    audit_entry = AuditLog(
        id=uuid.uuid4(),
        action="USER_REGISTER",
        entity_type="user",
        entity_id=str(new_user_id),
        performed_by=data.name.strip(),
        user_role=data.role,
        details=f"New citizen registered with email '{normalized_email}'.",
        ip_address=client_ip[:50] if client_ip else "127.0.0.1",
    )
    db.add(audit_entry)

    await db.commit()
    await db.refresh(new_user)
    if data.role == "officer":
        await db.refresh(new_user, attribute_names=["officer_profile"])

    return LoginResponse(
        token=access_token_str,
        access_token=access_token_str,
        refresh_token=raw_refresh_token,
        token_type="bearer",
        expires_in=expires_in_sec,
        user=_serialize_user(new_user),
    )


async def refresh_tokens(
    db: AsyncSession,
    raw_refresh_token: str,
    client_ip: str = "127.0.0.1",
    user_agent: Optional[str] = None,
) -> RefreshTokenResponse:
    """
    Rotate refresh tokens with reuse detection.
    If a revoked token is presented, the entire token family is revoked to prevent theft.
    """
    token_hash_str = hash_token(raw_refresh_token)

    # Find the refresh token record by its SHA-256 hash
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash_str)
    )
    token_record = result.scalar_one_or_none()

    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # REUSE DETECTION:
    # If the token has already been revoked, someone is replaying a spent token!
    if token_record.is_revoked:
        # Invalidate the ENTIRE family to stop session hijacking
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.family_id == token_record.family_id)
            .values(is_revoked=True)
        )
        audit_entry = AuditLog(
            id=uuid.uuid4(),
            action="SECURITY_ALERT_REFRESH_TOKEN_REUSE",
            entity_type="user",
            entity_id=str(token_record.user_id),
            performed_by="SYSTEM_SECURITY_SENTINEL",
            user_role="system",
            details=f"Refresh token reuse detected for family {token_record.family_id}. All family tokens revoked.",
            ip_address=client_ip[:50] if client_ip else "127.0.0.1",
        )
        db.add(audit_entry)
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Security violation: refresh token reuse detected. All sessions in this chain have been revoked.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check natural expiration
    if token_record.expires_at < datetime.now(timezone.utc):
        token_record.is_revoked = True
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Retrieve associated user
    user_result = await db.execute(
        select(User).where(User.id == token_record.user_id)
    )
    user = user_result.scalar_one_or_none()

    if not user or not user.is_active:
        token_record.is_revoked = True
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated or no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ROTATION:
    # 1. Revoke the presented token
    token_record.is_revoked = True

    # 2. Issue new refresh token within the same family
    new_raw_token = generate_secure_random_token(48)
    new_token_hash = hash_token(new_raw_token)
    new_expire_dt = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    new_refresh_record = RefreshToken(
        id=uuid.uuid4(),
        user_id=user.id,
        token_hash=new_token_hash,
        family_id=token_record.family_id,  # Maintain lineage
        expires_at=new_expire_dt,
        is_revoked=False,
        user_agent=user_agent[:255] if user_agent else None,
        ip_address=client_ip[:50] if client_ip else "127.0.0.1",
    )
    db.add(new_refresh_record)

    # 3. Issue new JWT access token
    new_access_token, expire_dt = create_access_token(
        user_id=user.id,
        role=user.role,
        email=user.email,
        name=user.name,
    )
    expires_in_sec = int((expire_dt - datetime.now(timezone.utc)).total_seconds())

    await db.commit()

    return RefreshTokenResponse(
        token=new_access_token,
        access_token=new_access_token,
        refresh_token=new_raw_token,
        token_type="bearer",
        expires_in=expires_in_sec,
    )


async def logout(
    db: AsyncSession,
    current_user: User,
    raw_refresh_token: Optional[str] = None,
    bearer_token: Optional[str] = None,
    client_ip: str = "127.0.0.1",
) -> None:
    """
    Terminate active session. Revokes refresh token in database
    and blacklists JWT access token in Redis.
    """
    # 1. Revoke refresh token if provided
    if raw_refresh_token:
        token_hash_str = hash_token(raw_refresh_token)
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash_str)
            .values(is_revoked=True)
        )

    # 2. Blacklist access token in Redis
    if bearer_token:
        await blacklist_token(bearer_token)

    # 3. Record audit entry
    audit_entry = AuditLog(
        id=uuid.uuid4(),
        action="USER_LOGOUT",
        entity_type="user",
        entity_id=str(current_user.id),
        performed_by=current_user.name,
        user_role=current_user.role,
        details=f"User signed out. Session terminated from IP: {client_ip}",
        ip_address=client_ip[:50] if client_ip else "127.0.0.1",
    )
    db.add(audit_entry)

    await db.commit()


async def forgot_password(
    db: AsyncSession,
    email: str,
    client_ip: str = "127.0.0.1",
) -> ForgotPasswordResponse:
    """
    Initiate password reset. Always returns neutral success message to prevent user enumeration.
    In development mode, surfaces dev_reset_token for automated testing and local workflows.
    """
    normalized_email = email.lower().strip()
    result = await db.execute(select(User).where(User.email == normalized_email))
    user = result.scalar_one_or_none()

    dev_token: Optional[str] = None

    if user and user.is_active:
        # Generate 15-minute reset token stored in Redis
        raw_reset_token = await create_password_reset_token(str(user.id), user.email, ttl_minutes=15)

        # In development mode, provide token in response for testing
        if settings.ENVIRONMENT == "development":
            dev_token = raw_reset_token

        # Audit entry
        audit_entry = AuditLog(
            id=uuid.uuid4(),
            action="PASSWORD_RESET_REQUESTED",
            entity_type="user",
            entity_id=str(user.id),
            performed_by=user.name,
            user_role=user.role,
            details=f"Password reset token requested from IP: {client_ip}",
            ip_address=client_ip[:50] if client_ip else "127.0.0.1",
        )
        db.add(audit_entry)
        await db.commit()

    return ForgotPasswordResponse(
        message="If an account with that email exists, password reset instructions have been generated.",
        dev_reset_token=dev_token,
        reset_token=dev_token,
    )


async def reset_password(
    db: AsyncSession,
    token: str,
    new_password: str,
    client_ip: str = "127.0.0.1",
) -> None:
    """
    Verify reset token and update account password hash with Argon2id.
    Revokes all active refresh tokens for the user upon completion.
    """
    payload = await verify_and_consume_password_reset_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token is invalid, expired, or has already been used.",
        )

    user_uuid = uuid.UUID(payload["user_id"])
    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account no longer exists.",
        )

    # Hash new password with Argon2id
    user.password_hash = get_password_hash(new_password)

    # Revoke all existing refresh tokens for security
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user.id)
        .values(is_revoked=True)
    )

    # Audit entry
    audit_entry = AuditLog(
        id=uuid.uuid4(),
        action="PASSWORD_RESET_COMPLETED",
        entity_type="user",
        entity_id=str(user.id),
        performed_by=user.name,
        user_role=user.role,
        details=f"Password successfully reset. All active refresh tokens revoked from IP: {client_ip}",
        ip_address=client_ip[:50] if client_ip else "127.0.0.1",
    )
    db.add(audit_entry)

    await db.commit()


async def update_user_profile(
    db: AsyncSession,
    current_user: User,
    data: UserProfileUpdateRequest,
) -> UserPublic:
    """
    Update profile preferences for the authenticated user.
    """
    if data.name is not None:
        current_user.name = data.name.strip()
    if data.phone is not None:
        current_user.phone = data.phone.strip()
    if data.ward is not None:
        current_user.ward = data.ward.strip()
    if data.avatar_url is not None:
        current_user.avatar_url = data.avatar_url.strip()

    await db.commit()
    await db.refresh(current_user)
    return _serialize_user(current_user)


# ==============================================================================
# Google OAuth2 Authentication & Account Auto-Provisioning
# ==============================================================================

async def verify_google_identity(data: GoogleAuthRequest) -> Dict[str, Any]:
    """
    Verifies a Google ID token or exchanges a Google Authorization Code.
    Returns the validated profile dictionary containing email, sub, name, and picture.
    """
    token = data.id_token or data.credential

    # If code was submitted (from redirect flow), exchange for tokens
    if data.code:
        redirect_uri = data.redirect_uri or settings.GOOGLE_REDIRECT_URI
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                token_resp = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "code": data.code,
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "redirect_uri": redirect_uri,
                        "grant_type": "authorization_code",
                    },
                )
                if token_resp.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Failed to exchange Google authorization code: {token_resp.text}",
                    )
                token_data = token_resp.json()
                token = token_data.get("id_token")
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Network error connecting to Google token endpoint: {e}",
                )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google id_token, credential, or authorization code must be provided.",
        )

    # 1. Attempt verification with official google-auth library
    id_info: Optional[Dict[str, Any]] = None
    verification_error = None
    try:
        id_info = google_id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except Exception as e:
        verification_error = e

    # 2. If google-auth verification failed or certificates needed online check, query tokeninfo
    if not id_info:
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token}")
                if resp.status_code == 200:
                    data_json = resp.json()
                    # Check audience match
                    if data_json.get("aud") != settings.GOOGLE_CLIENT_ID:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Google token audience (aud) does not match configured Client ID.",
                        )
                    id_info = data_json
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Invalid or expired Google token ({verification_error or resp.text}).",
                    )
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Unable to reach Google verification service: {e}",
                )

    if not id_info or not id_info.get("email"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google identity profile does not contain a verified email address.",
        )

    return id_info


async def login_with_google(
    db: AsyncSession,
    data: GoogleAuthRequest,
    client_ip: str = "127.0.0.1",
    user_agent: Optional[str] = None,
) -> LoginResponse:
    """
    Authenticate user via Google identity, auto-provisioning citizen accounts
    if this is their initial sign-in, and issuing standard JWT access + refresh tokens.
    """
    id_info = await verify_google_identity(data)

    email = id_info["email"].lower().strip()
    google_id = str(id_info.get("sub", ""))
    name = id_info.get("name") or email.split("@")[0]
    picture = id_info.get("picture")

    # 1. Query for existing user matching either google_id or email
    result = await db.execute(
        select(User)
        .options(selectinload(User.officer_profile))
        .where((User.google_id == google_id) | (User.email == email))
    )
    user = result.scalar_one_or_none()

    if user:
        # Check active status
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated. Please contact an administrator.",
            )

        # Link google_id if account was originally registered locally
        if not user.google_id:
            user.google_id = google_id
        if not user.avatar_url and picture:
            user.avatar_url = picture
    else:
        # 2. Auto-provision new citizen account with Google provider
        new_user_id = uuid.uuid4()
        user = User(
            id=new_user_id,
            name=name,
            email=email,
            password_hash=get_password_hash(generate_secure_random_token(32)),
            role="citizen",
            auth_provider="google",
            google_id=google_id,
            avatar_url=picture,
            is_active=True,
        )
        db.add(user)

    # 3. Issue access token
    access_token_str, expire_dt = create_access_token(
        user_id=user.id,
        role=user.role,
        email=user.email,
        name=user.name,
    )
    expires_in_sec = int((expire_dt - datetime.now(timezone.utc)).total_seconds())

    # 4. Issue rotating refresh token
    raw_refresh_token = generate_secure_random_token(48)
    refresh_hash = hash_token(raw_refresh_token)
    refresh_expire_dt = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    refresh_token_record = RefreshToken(
        id=uuid.uuid4(),
        user_id=user.id,
        token_hash=refresh_hash,
        family_id=uuid.uuid4(),
        expires_at=refresh_expire_dt,
        is_revoked=False,
        user_agent=user_agent[:255] if user_agent else None,
        ip_address=client_ip[:50] if client_ip else "127.0.0.1",
    )
    db.add(refresh_token_record)

    # 5. Security audit logging
    audit_entry = AuditLog(
        id=uuid.uuid4(),
        action="USER_LOGIN_GOOGLE",
        entity_type="user",
        entity_id=str(user.id),
        performed_by=user.name,
        user_role=user.role,
        details=f"User authenticated via Google Identity (Google ID: {google_id}) from IP: {client_ip}",
        ip_address=client_ip[:50] if client_ip else "127.0.0.1",
    )
    db.add(audit_entry)

    await db.commit()
    await db.refresh(user)

    user_public = _serialize_user(user)

    return LoginResponse(
        token=access_token_str,
        access_token=access_token_str,
        refresh_token=raw_refresh_token,
        token_type="bearer",
        expires_in=expires_in_sec,
        user=user_public,
    )


def get_google_auth_url(redirect_uri: Optional[str] = None) -> GoogleAuthUrlResponse:
    """
    Constructs the standard Google OAuth2 authorization redirect URL.
    """
    target_uri = redirect_uri or settings.GOOGLE_REDIRECT_URI
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": target_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    }
    query_str = urllib.parse.urlencode(params)
    return GoogleAuthUrlResponse(
        auth_url=f"https://accounts.google.com/o/oauth2/v2/auth?{query_str}",
        client_id=settings.GOOGLE_CLIENT_ID,
    )

