"""
CivicMind AI — Cryptographic Security & Authentication Subsystem
Production-grade Argon2id password hashing, PyJWT access tokens, refresh token hashing,
and Redis token blacklisting / rate-limiting.
"""

import time
import uuid
import secrets
import hashlib
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timezone, timedelta

import jwt
from jwt.exceptions import PyJWTError, ExpiredSignatureError, InvalidTokenError
from argon2 import PasswordHasher, Type
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

from app.core.config import settings
from app.core.redis import get_redis_client

# Initialize Argon2id password hasher
# Recommended OWASP parameters for high security: time_cost=3, memory_cost=64MB, parallelism=4
password_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    type=Type.ID,
)

JWT_ALGORITHM = "HS256"


# ==============================================================================
# Password Hashing & Verification (Argon2id)
# ==============================================================================

def get_password_hash(password: str) -> str:
    """
    Generate an Argon2id cryptographic hash of the provided plaintext password.
    """
    if not password:
        raise ValueError("Password cannot be empty.")
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against an Argon2id hash.
    Safe against timing attacks. Returns False on mismatch or corrupted hash.
    """
    if not plain_password or not hashed_password:
        return False
    try:
        return password_hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


# ==============================================================================
# Cryptographic Token Generation & Hashing
# ==============================================================================

def generate_secure_random_token(nbytes: int = 48) -> str:
    """
    Generate a cryptographically secure random URL-safe token.
    48 bytes delivers 384 bits of entropy.
    """
    return secrets.token_urlsafe(nbytes)


def hash_token(raw_token: str) -> str:
    """
    Compute the SHA-256 hex digest of a token string.
    Only the hash is persisted in the PostgreSQL database.
    """
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


# ==============================================================================
# JWT Access Token Lifecycle
# ==============================================================================

def create_access_token(
    user_id: uuid.UUID | str,
    role: str,
    email: str,
    name: str,
    expires_delta: Optional[timedelta] = None,
) -> Tuple[str, datetime]:
    """
    Encode a signed JWT access token containing standard RFC claims and role authorization.
    Returns: (signed_token_str, expiration_datetime)
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    jti = uuid.uuid4().hex
    payload: Dict[str, Any] = {
        "sub": str(user_id),
        "role": role,
        "email": email,
        "name": name,
        "type": "access",
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token, expire


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify signature and standard claims of a JWT access token.
    Raises:
        ExpiredSignatureError: Token has expired.
        InvalidTokenError: Token has been forged or token type is invalid.
    """
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
        options={"require": ["exp", "sub", "iat"]},
    )

    if payload.get("type") != "access":
        raise InvalidTokenError("Invalid token type: expected 'access' token.")

    return payload


# ==============================================================================
# Redis Token Revocation & Blacklisting
# ==============================================================================

async def blacklist_token(token: str) -> None:
    """
    Blacklist a JWT access token in Redis until its natural expiration.
    Used for immediate revocation upon logout.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"verify_exp": False},
        )
        jti = payload.get("jti")
        exp = payload.get("exp")
        if not jti or not exp:
            return

        now_ts = int(datetime.now(timezone.utc).timestamp())
        ttl = exp - now_ts
        if ttl > 0:
            redis = get_redis_client()
            await redis.set(f"blacklist:jwt:{jti}", "revoked", ex=ttl)
    except Exception:
        # Ignore errors during best-effort token blacklisting
        pass


async def is_token_blacklisted(jti: str) -> bool:
    """
    Check if a JWT access token's unique ID (jti) has been recorded as blacklisted.
    """
    try:
        redis = get_redis_client()
        val = await redis.get(f"blacklist:jwt:{jti}")
        return val is not None
    except Exception:
        return False


# ==============================================================================
# Login Rate Limiting (Redis Counter)
# ==============================================================================

async def check_login_rate_limit(
    identifier: str,
    max_attempts: int = 5,
    window_seconds: int = 300,
) -> Tuple[bool, int]:
    """
    Check whether the given identifier (IP or email) has exceeded failed login attempts.
    Returns: (is_allowed, remaining_cooldown_seconds)
    """
    try:
        redis = get_redis_client()
        key = f"rate_limit:login:{identifier.lower().strip()}"
        attempts = await redis.get(key)
        if attempts and int(attempts) >= max_attempts:
            ttl = await redis.ttl(key)
            return False, max(ttl, 1)
        return True, 0
    except Exception:
        return True, 0


async def record_login_attempt(
    identifier: str,
    success: bool,
    window_seconds: int = 300,
) -> None:
    """
    Record a login attempt. Clears attempts on success, increments and sets TTL on failure.
    """
    try:
        redis = get_redis_client()
        key = f"rate_limit:login:{identifier.lower().strip()}"
        if success:
            await redis.delete(key)
        else:
            pipe = redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, window_seconds)
            await pipe.execute()
    except Exception:
        pass


# ==============================================================================
# Password Reset Token Helpers (Redis-backed, 15-minute TTL)
# ==============================================================================

async def create_password_reset_token(user_id: str, email: str, ttl_minutes: int = 15) -> str:
    """
    Generate a cryptographically random password reset token and store its SHA-256 hash
    in Redis with an automatic expiration TTL.
    """
    raw_token = generate_secure_random_token(32)
    token_hash_str = hash_token(raw_token)
    redis = get_redis_client()

    payload_json = f"{user_id}:{email}"
    await redis.set(f"pwd_reset:{token_hash_str}", payload_json, ex=ttl_minutes * 60)
    return raw_token


async def verify_and_consume_password_reset_token(raw_token: str) -> Optional[Dict[str, str]]:
    """
    Verify a password reset token from Redis and immediately consume (delete) it
    to guarantee single-use protection.
    Returns: {"user_id": ..., "email": ...} or None if invalid/expired.
    """
    try:
        token_hash_str = hash_token(raw_token)
        redis = get_redis_client()
        key = f"pwd_reset:{token_hash_str}"
        val = await redis.get(key)
        if not val:
            return None

        # Delete immediately to prevent replay
        await redis.delete(key)

        parts = val.split(":", 1)
        if len(parts) == 2:
            return {"user_id": parts[0], "email": parts[1]}
        return None
    except Exception:
        return None
