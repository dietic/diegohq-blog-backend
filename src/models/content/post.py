"""
Post model for blog post content.

Stores blog posts with MDX content and gamification metadata.
"""

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin, UUIDMixin


class Post(Base, UUIDMixin, TimestampMixin):
    """Post model for blog content."""

    __tablename__ = "posts"

    # Core metadata
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    excerpt: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )
    author: Mapped[str] = mapped_column(
        String(100),
        default="Diego",
        nullable=False,
    )

    # Content (MDX)
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Content categorization
    content_pillar: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # programming, growth-career, saas-journey
    target_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # beginner, intermediate, advanced
    tags: Mapped[list[str] | None] = mapped_column(
        ARRAY(String(50)),
        nullable=True,
    )

    # Gamification - Gating
    required_level: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    required_item: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    challenge_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Gamification - Rewards
    read_xp: Mapped[int] = mapped_column(
        Integer,
        default=10,
        nullable=False,
    )
    quest_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # SEO
    meta_description: Mapped[str | None] = mapped_column(
        String(160),
        nullable=True,
    )
    og_image: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Publishing
    published: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    featured: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Calculated field
    reading_time: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    def __repr__(self) -> str:
        """Return string representation of Post."""
        return f"<Post(slug={self.slug}, title={self.title})>"
