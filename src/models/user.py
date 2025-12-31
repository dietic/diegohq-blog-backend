"""
User model for authentication and game progression.

Stores user credentials, profile information, and gamification data.
"""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.models.daily_reward import DailyReward
    from src.models.inventory_item import InventoryItem
    from src.models.post_progress import PostProgress
    from src.models.quest_progress import QuestProgress
    from src.models.refresh_token import RefreshToken
    from src.models.xp_transaction import XPTransaction


class User(Base, UUIDMixin, TimestampMixin):
    """User model with authentication and gamification fields."""

    __tablename__ = "users"

    # Authentication fields
    username: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Profile fields
    avatar_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    role: Mapped[str] = mapped_column(
        String(20),
        default="user",
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Gamification fields
    xp: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    level: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    current_streak: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    longest_streak: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Relationships
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    inventory_items: Mapped[list["InventoryItem"]] = relationship(
        "InventoryItem",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    quest_progress: Mapped[list["QuestProgress"]] = relationship(
        "QuestProgress",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    post_progress: Mapped[list["PostProgress"]] = relationship(
        "PostProgress",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    daily_rewards: Mapped[list["DailyReward"]] = relationship(
        "DailyReward",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    xp_transactions: Mapped[list["XPTransaction"]] = relationship(
        "XPTransaction",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """Return string representation of User."""
        return f"<User(id={self.id}, username={self.username}, level={self.level})>"
