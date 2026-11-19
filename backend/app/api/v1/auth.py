"""
CivicMind AI — Authentication API Endpoints
Implements register, login, rotating refresh tokens, logout revocation, /auth/me,
forgot-password, and reset-password.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, http_bearer
from app.models.user import User
from app.schemas.auth import (
    UserPublic,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    LogoutRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    UserProfileUpdateRequest,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication & Access Control"])


def _extract_client_ip(request: Request) -> str:
    """Extract client IP respecting X-Forwarded-For reverse proxy header."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Authenticate User & Issue Tokens",
    description="Validates user credentials via Argon2id, enforces rate limiting, and issues a JWT access token and rotating refresh token.",
)
async def login(
    creds: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    client_ip = _extract_client_ip(request)
    user_agent = request.headers.get("user-agent")
    return await auth_service.login(db, creds, client_ip=client_ip, user_agent=user_agent)


@router.post(
    "/register",
    response_model=LoginResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Citizen Registration",
    description="Creates a new citizen account with Argon2id password hashing, and returns active authentication tokens.",
)
async def register(
    data: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    client_ip = _extract_client_ip(request)
    user_agent = request.headers.get("user-agent")
    return await auth_service.register(db, data, client_ip=client_ip, user_agent=user_agent)


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Rotate Refresh Token & Issue Access Token",
    description="Rotates the refresh token while tracking the rotation family. Detects token reuse and terminates compromised sessions.",
)
async def refresh_token(
    payload: RefreshTokenRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> RefreshTokenResponse:
    client_ip = _extract_client_ip(request)
    user_agent = request.headers.get("user-agent")
    return await auth_service.refresh_tokens(
        db, payload.refresh_token, client_ip=client_ip, user_agent=user_agent
    )


@router.post(
    "/logout",
    summary="Sign Out & Revoke Session",
    description="Revokes the active refresh token in PostgreSQL and blacklists the JWT access token in Redis.",
)
async def logout(
    payload: Optional[LogoutRequest] = None,
    auth_header: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    current_user: User = Depends(get_current_user),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    client_ip = _extract_client_ip(request) if request else "127.0.0.1"
    raw_refresh = payload.refresh_token if payload else None
    bearer = auth_header.credentials if auth_header else None

    await auth_service.logout(
        db,
        current_user=current_user,
        raw_refresh_token=raw_refresh,
        bearer_token=bearer,
        client_ip=client_ip,
    )
    return {"message": "Successfully signed out. Session has been revoked."}


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Get Current User Profile",
    description="Returns the profile object of the currently authenticated user based on the Bearer JWT.",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserPublic:
    return auth_service._serialize_user(current_user)


@router.put(
    "/me",
    response_model=UserPublic,
    summary="Update Current User Profile",
    description="Updates contact information, ward, and avatar for the authenticated user.",
)
async def update_me(
    data: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserPublic:
    return await auth_service.update_user_profile(db, current_user, data)


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    summary="Request Password Reset",
    description="Initiates password reset flow. In development mode, surfaces dev_reset_token for automated testing.",
)
async def forgot_password(
    data: ForgotPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> ForgotPasswordResponse:
    client_ip = _extract_client_ip(request)
    return await auth_service.forgot_password(db, data.email, client_ip=client_ip)


@router.post(
    "/reset-password",
    summary="Complete Password Reset",
    description="Verifies the single-use reset token, updates account password hash, and invalidates previous refresh tokens.",
)
async def reset_password(
    data: ResetPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    client_ip = _extract_client_ip(request)
    await auth_service.reset_password(db, data.token, data.new_password, client_ip=client_ip)
    return {"message": "Password has been successfully updated. Please log in with your new password."}
