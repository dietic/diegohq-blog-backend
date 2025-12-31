"""
DailyReward model for tracking daily login rewards.

Stores claimed daily rewards and streak information.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, UUIDMixin

if TYPE_CHECKING:
    from src.models.user import User


class DailyReward(Base, UUIDMixin):
    """Daily reward model for tracking user daily login rewards."""

    __tablename__ = "daily_rewards"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    claimed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    )
    reward_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    reward_value: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    streak_day: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="daily_rewards",
    )

    def __repr__(self) -> str:
        """Return string representation of DailyReward."""
        return f"<DailyReward(id={self.id}, user_id={self.user_id}, reward_type={self.reward_type})>"
