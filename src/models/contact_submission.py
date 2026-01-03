"""
Contact submission model for storing contact form submissions.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin, UUIDMixin


class ContactSubmission(Base, UUIDMixin, TimestampMixin):
    """Model for contact form submissions."""

    __tablename__ = "contact_submissions"

    # Submission info
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    # Status tracking
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_replied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Reply info
    reply_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    replied_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    replied_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    def __repr__(self) -> str:
        return f"<ContactSubmission(id={self.id}, email={self.email}, is_read={self.is_read})>"
