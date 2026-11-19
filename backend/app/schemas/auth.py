"""
CivicMind AI — Authentication & User Profile Pydantic v2 Schemas
Exact data contract matching frontend expectations and API specifications.
"""

from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserPublic(BaseModel):
    id: str = Field(..., description="Unique User identifier (UUID string)")
    name: str = Field(..., description="Legal full name")
    email: EmailStr = Field(..., description="Verified primary email")
    role: Literal["citizen", "officer", "admin"] = Field(..., description="System RBAC role")
    department: Optional[str] = Field(None, description="Assigned department identifier or title")
    phone: Optional[str] = Field(None, description="Contact telephone number")
    ward: Optional[str] = Field(None, description="Residential or assigned administrative ward")
    avatar: Optional[str] = Field(None, description="Profile avatar picture URI")
    badge: Optional[str] = Field(None, description="Designation badge or resident tier")
    auth_provider: Optional[str] = Field("local", description="Authentication provider (local, google)")

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Registered login email")
    password: str = Field(..., min_length=6, description="Account password (min 6 chars)")
    role: Optional[Literal["citizen", "officer", "admin"]] = Field(
        None, description="Role hint selected in login portal"
    )
    rememberMe: Optional[bool] = Field(False, description="Extend session duration flag")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower().strip()


class LoginResponse(BaseModel):
    token: str = Field(..., description="Primary JWT Bearer token consumed by frontend")
    access_token: str = Field(..., description="OAuth2 standard alias for token")
    refresh_token: str = Field(..., description="Long-lived rotation token")
    token_type: str = Field("bearer", description="Token authentication schema")
    expires_in: int = Field(3600, description="Token lifetime in seconds")
    user: UserPublic = Field(..., description="Authenticated user profile object")


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=150, description="User full name")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=6, max_length=128, description="Password (min 6 characters)")
    phone: Optional[str] = Field(None, max_length=25, description="Contact phone number")
    ward: Optional[str] = Field(None, max_length=100, description="Default residential ward")
    role: Literal["citizen", "officer", "admin"] = Field("citizen", description="Registration role")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower().strip()


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Rotating refresh token string")


class RefreshTokenResponse(BaseModel):
    token: str = Field(..., description="New JWT Bearer access token")
    access_token: str = Field(..., description="OAuth2 standard alias")
    refresh_token: str = Field(..., description="Rotated new refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(3600, description="Access token expiration window in seconds")


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = Field(None, description="Optional refresh token to revoke")


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Registered email to receive password reset token")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower().strip()


class ForgotPasswordResponse(BaseModel):
    message: str = Field(..., description="Status message indicating reset initiation")
    dev_reset_token: Optional[str] = Field(
        None, description="Development-mode reset token for immediate verification testing"
    )
    reset_token: Optional[str] = Field(
        None, description="Alias for dev_reset_token for test compatibility"
    )


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., description="Password reset verification token")
    new_password: str = Field(..., min_length=6, max_length=128, description="New account password")


class UserProfileUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    phone: Optional[str] = Field(None, max_length=25)
    ward: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None)


class GoogleAuthRequest(BaseModel):
    id_token: Optional[str] = Field(None, description="Google OpenID Connect JWT ID token")
    credential: Optional[str] = Field(None, description="Alias for id_token from Google Identity Services")
    code: Optional[str] = Field(None, description="Authorization code from OAuth2 redirect flow")
    redirect_uri: Optional[str] = Field(None, description="Redirect URI passed in authorization request")


class GoogleAuthUrlResponse(BaseModel):
    auth_url: str = Field(..., description="Google OAuth2 authorization URL")
    client_id: str = Field(..., description="Configured Google Client ID")

