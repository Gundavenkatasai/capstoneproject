"""
CivicMind AI — FastAPI Authentication & Role-Based Authorization Dependencies
Implements token parsing, user resolution, role gates, and object-level IDOR protections.
"""

import uuid
from typing import List, Callable, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import decode_access_token, is_token_blacklisted
from app.models.user import User
from app.models.officer import Officer
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

# HTTP Bearer scheme for Swagger / OpenAPI token injection
http_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    auth_header: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Extracts Bearer token from request Authorization header, decodes JWT,
    checks Redis blacklist, and fetches user from database with officer profile.
    Raises:
        401 Unauthorized: If token is missing, expired, blacklisted, or user not found.
    """
    if not auth_header or not auth_header.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.credentials

    try:
        payload = decode_access_token(token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or malformed authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token is not in Redis revocation blacklist
    jti = payload.get("jti")
    if jti and await is_token_blacklisted(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject claim is missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identifier format in token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database with officer_profile loaded
    result = await db.execute(
        select(User)
        .options(selectinload(User.officer_profile))
        .where(User.id == user_uuid)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated. Please contact an administrator.",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Alias ensuring the current user is active.
    """
    return current_user


def require_role(allowed_roles: List[str]) -> Callable:
    """
    Dependency factory enforcing role-based access control (RBAC).
    Usage: Depends(require_role(["admin", "officer"]))
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role in {allowed_roles}, but user has role '{current_user.role}'.",
            )
        return current_user

    return role_checker


def require_any_role(*roles: str) -> Callable:
    """
    Syntactic sugar for require_role.
    Usage: Depends(require_any_role("admin", "officer"))
    """
    return require_role(list(roles))


# ==============================================================================
# Object-Level Authorization & Insecure Direct Object Reference (IDOR) Guards
# ==============================================================================

def verify_user_access(current_user: User, target_user_id: uuid.UUID | str) -> None:
    """
    Object-level security check:
    Ensures that citizens can only inspect or modify their own user record,
    while administrators have elevated cross-user privileges.
    """
    target_id_str = str(target_user_id)
    current_id_str = str(current_user.id)

    if current_user.role == "admin":
        return

    if current_id_str != target_id_str:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not have permission to access another user's private data.",
        )


def verify_department_access(current_user: User, target_department_id: str) -> None:
    """
    Object-level security check:
    Ensures officers can only access workloads and records belonging to their assigned department,
    while administrators maintain global citywide jurisdiction.
    """
    if current_user.role == "admin":
        return

    if current_user.role == "officer":
        if current_user.officer_profile and current_user.officer_profile.department_id == target_department_id:
            return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Access forbidden: your officer roster does not permit access to department '{target_department_id}'.",
    )
