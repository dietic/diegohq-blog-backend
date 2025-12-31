"""
Pydantic schemas for authentication operations.

Defines request/response schemas for auth endpoints.
"""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    """Schema for user registration request."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Username (alphanumeric and underscores only)",
    )
    email: EmailStr = Field(
        ...,
        description="User email address",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password (minimum 8 characters)",
    )


class LoginRequest(BaseModel):
    """Schema for user login request."""

    email: EmailStr = Field(
        ...,
        description="User email address",
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User password",
    )


class LoginResponse(BaseModel):
    """Schema for login response with tokens."""

    access_token: str = Field(
        ...,
        alias="accessToken",
        description="JWT access token",
    )
    refresh_token: str = Field(
        ...,
        alias="refreshToken",
        description="JWT refresh token",
    )
    token_type: str = Field(
        default="bearer",
        alias="tokenType",
        description="Token type",
    )

    model_config = ConfigDict(populate_by_name=True)


class RefreshRequest(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str = Field(
        ...,
        alias="refreshToken",
        description="JWT refresh token",
    )

    model_config = ConfigDict(populate_by_name=True)


class RefreshResponse(BaseModel):
    """Schema for token refresh response."""

    access_token: str = Field(
        ...,
        alias="accessToken",
        description="New JWT access token",
    )
    refresh_token: str = Field(
        ...,
        alias="refreshToken",
        description="New JWT refresh token",
    )
    token_type: str = Field(
        default="bearer",
        alias="tokenType",
        description="Token type",
    )

    model_config = ConfigDict(populate_by_name=True)


class TokenPayload(BaseModel):
    """Schema for JWT token payload."""

    sub: str = Field(..., description="Subject (user ID)")
    exp: int = Field(..., description="Expiration timestamp")
    type: str = Field(..., description="Token type (access/refresh)")
