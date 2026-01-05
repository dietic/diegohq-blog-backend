"""
Quest model for gamification quests.

Stores quest definitions with prompts, answers, and rewards.
"""

from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin, UUIDMixin


class Quest(Base, UUIDMixin, TimestampMixin):
    """Quest model for gamification quests."""

    __tablename__ = "quests"

    # Unique identifier (used for references)
    quest_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    # Quest content
    prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    quest_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # multiple-choice, code

    # Multiple choice fields
    options: Mapped[list[str] | None] = mapped_column(
        ARRAY(String(500)),
        nullable=True,
    )
    correct_answer: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Code quest fields
    language: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )  # javascript, typescript, python, html, css, jsx, tsx
    starter_code: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    ai_criteria: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )  # Instructions for AI reviewer
    hint: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )  # Tip shown after 3 failed attempts

    # Rewards
    xp_reward: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    item_reward: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Metadata
    difficulty: Mapped[str] = mapped_column(
        String(20),
        default="easy",
        nullable=False,
    )  # easy, medium, hard

    # Note: The relationship between posts and quests is defined on the Post model
    # via post.quest_id. Quests no longer reference posts directly.

    def __repr__(self) -> str:
        """Return string representation of Quest."""
        return f"<Quest(quest_id={self.quest_id}, name={self.name})>"
