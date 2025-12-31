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
    """Schema for quest progress response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    quest_id: str = Field(
        ...,
        alias="questId",
        description="ID of the quest",
    )
    completed: bool = Field(..., description="Whether the quest is completed")
    completed_at: datetime | None = Field(
        None,
        alias="completedAt",
        description="When the quest was completed",
    )
    attempts: int = Field(..., description="Number of attempts made")
