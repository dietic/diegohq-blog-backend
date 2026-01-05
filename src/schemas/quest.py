"""
Pydantic schemas for quest operations.

Defines request/response schemas for quest endpoints.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class QuestSubmitRequest(BaseModel):
    """Schema for submitting a quest answer."""

    answer: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The answer to submit",
    )


class QuestSubmitResponse(BaseModel):
    """Schema for quest submission response."""

    model_config = ConfigDict(populate_by_name=True)

    success: bool = Field(..., description="Whether the answer was correct")
    correct: bool = Field(..., description="Whether the answer was correct")
    xp_awarded: int = Field(
        ...,
        alias="xpAwarded",
        description="Amount of XP awarded",
    )
    attempts: int = Field(
        ...,
        description="Number of attempts made",
    )
    new_xp: int = Field(
        ...,
        alias="newXp",
        description="User's new total XP",
    )
    new_level: int = Field(
        ...,
        alias="newLevel",
        description="User's new level",
    )
    leveled_up: bool = Field(
        ...,
        alias="leveledUp",
        description="Whether the user leveled up",
    )
    feedback: str | None = Field(
        None,
        description="Feedback message for the answer",
    )


class QuestProgressResponse(BaseModel):
    """Schema for quest progress response with enriched quest details."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    quest_id: str = Field(
        ...,
        alias="questId",
        description="ID of the quest",
    )
    quest_name: str = Field(
        ...,
        alias="questName",
        description="Name of the quest",
    )
    quest_type: str = Field(
        ...,
        alias="questType",
        description="Type of quest (multiple-choice, code)",
    )
    xp_reward: int = Field(
        ...,
        alias="xpReward",
        description="XP reward for completing the quest",
    )
    xp_earned: int = Field(
        ...,
        alias="xpEarned",
        description="XP earned from completing the quest (0 if not completed)",
    )
    host_post_slug: str = Field(
        ...,
        alias="hostPostSlug",
        description="Slug of the post the quest is attached to",
    )
    host_post_title: str | None = Field(
        None,
        alias="hostPostTitle",
        description="Title of the post the quest is attached to",
    )
    in_progress: bool = Field(
        ...,
        alias="inProgress",
        description="Whether the quest is in progress",
    )
    completed: bool = Field(..., description="Whether the quest is completed")
    started_at: datetime | None = Field(
        None,
        alias="startedAt",
        description="When the quest was started",
    )
    completed_at: datetime | None = Field(
        None,
        alias="completedAt",
        description="When the quest was completed",
    )
    attempts: int = Field(..., description="Number of attempts made")


class CodeSubmitRequest(BaseModel):
    """Schema for submitting code for a code quest."""

    code: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="The code to submit",
    )


class CodeSubmitResponse(BaseModel):
    """Schema for code submission response."""

    model_config = ConfigDict(populate_by_name=True)

    passed: bool = Field(..., description="Whether the code passed review")
    feedback: str = Field(..., description="AI feedback on the submission")
    attempts: int = Field(..., description="Number of attempts made")
    show_hint: bool = Field(
        ...,
        alias="showHint",
        description="Whether to show the hint (after 3 failures)",
    )
    hint: str | None = Field(
        None,
        description="The hint text (if show_hint is true)",
    )
    cooldown_seconds: int = Field(
        ...,
        alias="cooldownSeconds",
        description="Seconds until next attempt allowed",
    )
    xp_awarded: int = Field(
        ...,
        alias="xpAwarded",
        description="XP awarded (0 if not passed)",
    )
    new_xp: int = Field(
        ...,
        alias="newXp",
        description="User's new total XP",
    )
    new_level: int = Field(
        ...,
        alias="newLevel",
        description="User's new level",
    )
    leveled_up: bool = Field(
        ...,
        alias="leveledUp",
        description="Whether the user leveled up",
    )


class StartQuestResponse(BaseModel):
    """Schema for starting a quest."""

    model_config = ConfigDict(populate_by_name=True)

    success: bool = Field(..., description="Whether the quest was started")
    quest_id: str = Field(
        ...,
        alias="questId",
        description="ID of the quest",
    )
    already_started: bool = Field(
        ...,
        alias="alreadyStarted",
        description="Whether the quest was already started",
    )
    already_completed: bool = Field(
        ...,
        alias="alreadyCompleted",
        description="Whether the quest is already completed",
    )
