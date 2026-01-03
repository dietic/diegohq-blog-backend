"""
Pydantic schemas for quest content operations.

Defines request/response schemas for quest content endpoints.
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


QuestType = Literal["multiple-choice", "text-input", "call-to-action"]
QuestDifficulty = Literal["easy", "medium", "hard"]


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
        description="Correct answer for validation",
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
    host_post_slug: str = Field(
        ...,
        max_length=255,
        description="Host post slug",
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
        description="Correct answer for validation",
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
    host_post_slug: str | None = Field(
        default=None,
        max_length=255,
        description="Host post slug",
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
    options: list[str] | None = None
    correct_answer: str | None = None
    xp_reward: int
    item_reward: str | None = None
    host_post_slug: str
    difficulty: str
    created_at: datetime
    updated_at: datetime
