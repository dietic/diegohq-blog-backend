"""
XPTransaction model for tracking XP changes.

Provides an audit trail of all XP awards and deductions.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, UUIDMixin

if TYPE_CHECKING:
    from src.models.user import User


class XPTransaction(Base, UUIDMixin):
    """XP transaction model for tracking XP changes."""

    __tablename__ = "xp_transactions"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    source_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="xp_transactions",
    )

    def __repr__(self) -> str:
        """Return string representation of XPTransaction."""
        return f"<XPTransaction(id={self.id}, user_id={self.user_id}, amount={self.amount}, source={self.source})>"
