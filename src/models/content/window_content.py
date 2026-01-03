"""
WindowContent model for custom window content.

Stores MDX content for custom windows.
"""

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin, UUIDMixin


class WindowContent(Base, UUIDMixin, TimestampMixin):
    """WindowContent model for custom window content."""

    __tablename__ = "window_contents"

    # Unique identifier (used for references)
    window_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Optional icon for the window header
    icon: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Default window dimensions
    default_width: Mapped[int] = mapped_column(
        Integer,
        default=600,
        nullable=False,
    )
    default_height: Mapped[int] = mapped_column(
        Integer,
        default=400,
        nullable=False,
    )

    # Behavior
    singleton: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    closable: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    minimizable: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    maximizable: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Gating
    required_level: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    required_item: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # MDX content
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    def __repr__(self) -> str:
        """Return string representation of WindowContent."""
        return f"<WindowContent(window_id={self.window_id}, title={self.title})>"
