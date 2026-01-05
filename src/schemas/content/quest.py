"""
Pydantic schemas for quest content operations.

Defines request/response schemas for quest content endpoints.
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


QuestType = Literal["multiple-choice", "code"]
QuestDifficulty = Literal["easy", "medium", "hard"]
CodeLanguage = Literal["javascript", "typescript", "python", "html", "css", "jsx", "tsx"]


class QuestCreate(BaseModel):
    """Schema for creating a new quest."""

    quest_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9-]+$",
        description="Unique quest identifier",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Quest name",
    )
    description: str = Field(
        ...,
        max_length=500,
        description="Quest description",
    )
    prompt: str = Field(
        ...,
        description="Quest prompt/question",
    )
    quest_type: QuestType = Field(
        ...,
        description="Type of quest",
    )
    options: list[str] | None = Field(
        default=None,
        description="Options for multiple-choice quests",
    )
    correct_answer: str | None = Field(
        default=None,
        description="Correct answer for validation (multiple-choice)",
    )

    # Code quest fields
    language: CodeLanguage | None = Field(
        default=None,
        description="Programming language for code quests",
    )
    starter_code: str | None = Field(
        default=None,
        description="Starter code for code quests",
    )
    ai_criteria: str | None = Field(
        default=None,
        description="AI review criteria for code quests",
    )
    hint: str | None = Field(
        default=None,
        description="Hint shown after 3 failed attempts",
    )

    xp_reward: int = Field(
        ...,
        ge=1,
        description="XP reward for completion",
    )
    item_reward: str | None = Field(
        default=None,
        max_length=100,
        description="Item reward ID",
    )
    difficulty: QuestDifficulty = Field(
        default="easy",
        description="Quest difficulty",
    )


class QuestUpdate(BaseModel):
    """Schema for updating a quest."""

    quest_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9-]+$",
        description="Unique quest identifier",
    )
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Quest name",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Quest description",
    )
    prompt: str | None = Field(
        default=None,
        description="Quest prompt/question",
    )
    quest_type: QuestType | None = Field(
        default=None,
        description="Type of quest",
    )
    options: list[str] | None = Field(
        default=None,
        description="Options for multiple-choice quests",
    )
    correct_answer: str | None = Field(
        default=None,
        description="Correct answer for validation (multiple-choice)",
    )

    # Code quest fields
    language: CodeLanguage | None = Field(
        default=None,
        description="Programming language for code quests",
    )
    starter_code: str | None = Field(
        default=None,
        description="Starter code for code quests",
    )
    ai_criteria: str | None = Field(
        default=None,
        description="AI review criteria for code quests",
    )
    hint: str | None = Field(
        default=None,
        description="Hint shown after 3 failed attempts",
    )

    xp_reward: int | None = Field(
        default=None,
        ge=1,
        description="XP reward for completion",
    )
    item_reward: str | None = Field(
        default=None,
        max_length=100,
        description="Item reward ID",
    )
    difficulty: QuestDifficulty | None = Field(
        default=None,
        description="Quest difficulty",
    )


class QuestResponse(BaseModel):
    """Schema for quest response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    quest_id: str
    name: str
    description: str
    prompt: str
    quest_type: str

    # Multiple choice fields
    options: list[str] | None = None
    correct_answer: str | None = None

    # Code quest fields
    language: str | None = None
    starter_code: str | None = None
    ai_criteria: str | None = None
    hint: str | None = None

    xp_reward: int
    item_reward: str | None = None
    difficulty: str
    created_at: datetime
    updated_at: datetime
