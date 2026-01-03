"""
DesktopIcon model for desktop interface icons.

Stores desktop icon definitions with positioning and window configuration.
"""

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin, UUIDMixin


class DesktopIcon(Base, UUIDMixin, TimestampMixin):
    """DesktopIcon model for desktop interface icons."""

    __tablename__ = "desktop_icons"

    # Unique identifier (used for references)
    icon_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    label: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    icon: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Position on desktop (grid-based)
    position_x: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    position_y: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # What happens when double-clicked
    window_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # custom, external
    window_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    external_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Window configuration (JSON)
    window_config: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    # Visibility/Gating
    required_level: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    required_item: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    visible: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Ordering
    order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    def __repr__(self) -> str:
        """Return string representation of DesktopIcon."""
        return f"<DesktopIcon(icon_id={self.icon_id}, label={self.label})>"
