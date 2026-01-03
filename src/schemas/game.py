"""
Pydantic schemas for game mechanics operations.

Defines request/response schemas for game-related endpoints.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReadPostRequest(BaseModel):
    """Schema for marking a post as read."""

    model_config = ConfigDict(populate_by_name=True)

    post_slug: str = Field(
        ...,
        alias="postSlug",
        min_length=1,
        max_length=255,
        description="The slug of the post that was read",
    )
    read_xp: int = Field(
        default=15,
        alias="readXp",
        ge=0,
        le=1000,
        description="XP to award for reading this post",
    )


class ReadPostResponse(BaseModel):
    """Schema for read post response."""

    model_config = ConfigDict(populate_by_name=True)

    success: bool = Field(..., description="Whether the operation was successful")
    xp_awarded: int = Field(
        ...,
        alias="xpAwarded",
        description="Amount of XP awarded for reading",
    )
    already_read: bool = Field(
        ...,
        alias="alreadyRead",
        description="Whether the post was already read",
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


class DailyRewardResponse(BaseModel):
    """Schema for daily reward claim response."""

    model_config = ConfigDict(populate_by_name=True)

    success: bool = Field(..., description="Whether the reward was claimed")
    xp_awarded: int = Field(
        ...,
        alias="xpAwarded",
        description="Amount of XP awarded",
    )
    streak_day: int = Field(
        ...,
        alias="streakDay",
        description="Current streak day",
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
    already_claimed: bool = Field(
        ...,
        alias="alreadyClaimed",
        description="Whether already claimed today",
    )
    next_claim_at: datetime | None = Field(
        None,
        alias="nextClaimAt",
        description="When the next reward can be claimed",
    )


class UseItemRequest(BaseModel):
    """Schema for using an inventory item."""

    model_config = ConfigDict(populate_by_name=True)

    item_id: str = Field(
        ...,
        alias="itemId",
        min_length=1,
        max_length=100,
        description="ID of the item to use",
    )
    target_slug: str | None = Field(
        None,
        alias="targetSlug",
        max_length=255,
        description="Optional target (e.g., post slug to unlock)",
    )


class UseItemResponse(BaseModel):
    """Schema for use item response."""

    model_config = ConfigDict(populate_by_name=True)

    success: bool = Field(..., description="Whether the item was used")
    item_id: str = Field(
        ...,
        alias="itemId",
        description="ID of the item used",
    )
    effect: str = Field(
        ...,
        description="Description of the item's effect",
    )
    target_unlocked: str | None = Field(
        None,
        alias="targetUnlocked",
        description="The target that was unlocked, if any",
    )


class AccessCheckRequest(BaseModel):
    """Schema for checking content access."""

    model_config = ConfigDict(populate_by_name=True)

    post_slug: str = Field(
        ...,
        alias="postSlug",
        min_length=1,
        max_length=255,
        description="The slug of the post to check access for",
    )
    required_level: int | None = Field(
        None,
        alias="requiredLevel",
        ge=1,
        description="Required level for access",
    )
    required_item: str | None = Field(
        None,
        alias="requiredItem",
        max_length=100,
        description="Required item for access",
    )


class AccessCheckResponse(BaseModel):
    """Schema for access check response."""

    model_config = ConfigDict(populate_by_name=True)

    has_access: bool = Field(
        ...,
        alias="hasAccess",
        description="Whether the user has access",
    )
    reason: str | None = Field(
        None,
        description="Reason for denied access",
    )
    user_level: int = Field(
        ...,
        alias="userLevel",
        description="User's current level",
    )
    required_level: int | None = Field(
        None,
        alias="requiredLevel",
        description="Required level if level-gated",
    )
    has_required_item: bool | None = Field(
        None,
        alias="hasRequiredItem",
        description="Whether user has required item",
    )


class LevelProgressResponse(BaseModel):
    """Schema for level progress response."""

    model_config = ConfigDict(populate_by_name=True)

    current_level: int = Field(
        ...,
        alias="currentLevel",
        description="User's current level",
    )
    current_xp: int = Field(
        ...,
        alias="currentXp",
        description="User's current total XP",
    )
    xp_for_current_level: int = Field(
        ...,
        alias="xpForCurrentLevel",
        description="XP required for current level",
    )
    xp_for_next_level: int = Field(
        ...,
        alias="xpForNextLevel",
        description="XP required for next level",
    )
    xp_progress: int = Field(
        ...,
        alias="xpProgress",
        description="XP progress toward next level",
    )
    progress_percentage: float = Field(
        ...,
        alias="progressPercentage",
        description="Progress percentage toward next level (0-100)",
    )
