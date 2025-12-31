"""
InventoryItem model for user inventory management.

Tracks items owned by users for content gating and rewards.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, UUIDMixin

if TYPE_CHECKING:
    from src.models.user import User


class InventoryItem(Base, UUIDMixin):
    """Inventory item model for user items."""

    __tablename__ = "inventory_items"
    __table_args__ = (
        UniqueConstraint("user_id", "item_id", name="uq_user_item"),
    )

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    acquired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="inventory_items",
    )

    def __repr__(self) -> str:
        """Return string representation of InventoryItem."""
        return f"<InventoryItem(id={self.id}, user_id={self.user_id}, item_id={self.item_id})>"
