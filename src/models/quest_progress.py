"""
QuestProgress model for tracking user quest completion.

Stores quest attempts and completion status.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.models.user import User


class QuestProgress(Base, UUIDMixin, TimestampMixin):
    """Quest progress model for tracking user quest completion."""

    __tablename__ = "quest_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "quest_id", name="uq_user_quest"),
    )

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
    completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    answer_given: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="quest_progress",
    )

    def __repr__(self) -> str:
        """Return string representation of QuestProgress."""
        return f"<QuestProgress(id={self.id}, user_id={self.user_id}, quest_id={self.quest_id}, completed={self.completed})>"
