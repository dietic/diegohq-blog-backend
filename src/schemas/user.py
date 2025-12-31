"""
Pydantic schemas for user-related operations.

Defines request/response schemas for user endpoints.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for creating a new user."""

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


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    username: str | None = Field(
        None,
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="New username",
    )
    avatar_url: str | None = Field(
        None,
        max_length=500,
        description="URL to user avatar image",
    )


class UserResponse(BaseModel):
    """Schema for user response (public data)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    avatar_url: str | None = None
    xp: int
    level: int
    current_streak: int
    longest_streak: int
    created_at: datetime


class UserProfileResponse(BaseModel):
    """Schema for full user profile response (includes email)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    email: str
    avatar_url: str | None = None
    role: str
    is_active: bool
    xp: int
    level: int
    current_streak: int
    longest_streak: int
    created_at: datetime
    updated_at: datetime
