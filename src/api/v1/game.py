"""
Game mechanics endpoints.

Provides XP tracking, level progress, daily rewards, and content access.
"""

from fastapi import APIRouter

from src.dependencies import AsyncSessionDep, CurrentUser
from src.schemas.game import (
    AccessCheckRequest,
    AccessCheckResponse,
    DailyRewardResponse,
    LevelProgressResponse,
    ReadPostRequest,
    ReadPostResponse,
    UseItemRequest,
    UseItemResponse,
)
from src.services.game_service import GameService

router = APIRouter()


@router.post("/read-post", response_model=ReadPostResponse)
async def read_post(
    current_user: CurrentUser,
    data: ReadPostRequest,
    db: AsyncSessionDep,
) -> ReadPostResponse:
    """
    Mark a post as read and receive XP.

    Args:
        current_user: The authenticated user.
        data: The post slug.
        db: Database session.

    Returns:
        XP awarded and level info.
    """
    game_service = GameService(db)
    return await game_service.read_post(current_user, data.post_slug)


@router.post("/daily-reward", response_model=DailyRewardResponse)
async def claim_daily_reward(
    current_user: CurrentUser,
    db: AsyncSessionDep,
) -> DailyRewardResponse:
    """
    Claim the daily login reward.

    Args:
        current_user: The authenticated user.
        db: Database session.

    Returns:
        Reward info and streak status.
    """
    game_service = GameService(db)
    return await game_service.claim_daily_reward(current_user)


@router.post("/use-item", response_model=UseItemResponse)
async def use_item(
    current_user: CurrentUser,
    data: UseItemRequest,
    db: AsyncSessionDep,
) -> UseItemResponse:
    """
    Use an item from inventory.

    Args:
        current_user: The authenticated user.
        data: The item to use and optional target.
        db: Database session.

    Returns:
        Result of using the item.
    """
    game_service = GameService(db)
    return await game_service.use_item(current_user, data.item_id, data.target_slug)


@router.post("/check-access", response_model=AccessCheckResponse)
async def check_access(
    current_user: CurrentUser,
    data: AccessCheckRequest,
    db: AsyncSessionDep,
) -> AccessCheckResponse:
    """
    Check if user has access to content.

    Args:
        current_user: The authenticated user.
        data: The access requirements.
        db: Database session.

    Returns:
        Access status and requirements info.
    """
    game_service = GameService(db)
    return await game_service.check_access(
        current_user,
        data.post_slug,
        data.required_level,
        data.required_item,
    )


@router.get("/level-progress", response_model=LevelProgressResponse)
async def get_level_progress(
    current_user: CurrentUser,
    db: AsyncSessionDep,
) -> LevelProgressResponse:
    """
    Get detailed level progress.

    Args:
        current_user: The authenticated user.
        db: Database session.

    Returns:
        Level progress details.
    """
    game_service = GameService(db)
    return game_service.get_level_progress(current_user)
