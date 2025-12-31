"""
PostProgress model for tracking user post interactions.

Stores post read status and content unlocking.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.models.user import User


class PostProgress(Base, UUIDMixin, TimestampMixin):
    """Post progress model for tracking user post interactions."""

    __tablename__ = "post_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "post_slug", name="uq_user_post"),
    )

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    post_slug: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    has_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    is_unlocked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    unlocked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    unlocked_with_item: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="post_progress",
    )

    def __repr__(self) -> str:
        """Return string representation of PostProgress."""
        return f"<PostProgress(id={self.id}, user_id={self.user_id}, post_slug={self.post_slug})>"
