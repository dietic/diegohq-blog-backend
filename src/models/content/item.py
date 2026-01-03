"""
Item model for gamification items.

Stores item definitions for inventory and content gating.
"""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin, UUIDMixin


class Item(Base, UUIDMixin, TimestampMixin):
    """Item model for gamification items."""

    __tablename__ = "items"

    # Unique identifier (used for references)
    item_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    # Display
    icon: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    rarity: Mapped[str] = mapped_column(
        String(20),
        default="common",
        nullable=False,
    )  # common, uncommon, rare, legendary

    # Flavor
    flavor_text: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    def __repr__(self) -> str:
        """Return string representation of Item."""
        return f"<Item(item_id={self.item_id}, name={self.name})>"
