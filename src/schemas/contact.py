"""Schemas for contact form submissions."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class ContactSubmissionCreate(BaseModel):
    """Schema for creating a contact submission."""

    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    message: str = Field(..., min_length=10, max_length=5000)


class ContactSubmissionResponse(BaseModel):
    """Schema for contact submission response."""

    id: UUID
    name: str
    email: str
    message: str
    is_read: bool
    is_replied: bool
    reply_message: Optional[str] = None
    replied_at: Optional[datetime] = None
    replied_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ContactReplyRequest(BaseModel):
    """Schema for replying to a contact submission."""

    reply_message: str = Field(..., min_length=1, max_length=10000)


class ContactSubmissionListResponse(BaseModel):
    """Schema for listing contact submissions."""

    items: list[ContactSubmissionResponse]
    total: int
    unread_count: int
