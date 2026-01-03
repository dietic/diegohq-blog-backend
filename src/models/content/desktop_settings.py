"""
DesktopSettings model for desktop configuration.

Stores global desktop settings like grid size and icon spacing.
"""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin, UUIDMixin


class DesktopSettings(Base, UUIDMixin, TimestampMixin):
    """DesktopSettings model for desktop configuration."""

    __tablename__ = "desktop_settings"

    # Unique key for settings (singleton pattern)
    key: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        default="default",
    )

    # Grid settings
    grid_size: Mapped[int] = mapped_column(
        Integer,
        default=80,
        nullable=False,
    )
    icon_spacing: Mapped[int] = mapped_column(
        Integer,
        default=16,
        nullable=False,
    )

    # Start position
    start_position_x: Mapped[int] = mapped_column(
        Integer,
        default=20,
        nullable=False,
    )
    start_position_y: Mapped[int] = mapped_column(
        Integer,
        default=20,
        nullable=False,
    )

    def __repr__(self) -> str:
        """Return string representation of DesktopSettings."""
        return f"<DesktopSettings(key={self.key}, grid_size={self.grid_size})>"
