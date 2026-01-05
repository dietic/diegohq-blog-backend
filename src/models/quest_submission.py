"""
QuestSubmission model for tracking quest submission history.

Stores each submission attempt for analytics and debugging.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.models.user import User


class QuestSubmission(Base, UUIDMixin, TimestampMixin):
    """Quest submission model for tracking submission history."""

    __tablename__ = "quest_submissions"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quest_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    submission_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # "code" or "multiple-choice"
    code_submitted: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    answer_submitted: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    passed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    ai_feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="quest_submissions",
    )

    def __repr__(self) -> str:
        """Return string representation of QuestSubmission."""
        return f"<QuestSubmission(id={self.id}, user_id={self.user_id}, quest_id={self.quest_id}, passed={self.passed})>"
