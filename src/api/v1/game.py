"""
Game mechanics endpoints.

Provides XP tracking, level progress, daily rewards, and content access.
"""

from fastapi import APIRouter, HTTPException

from src.config import settings
from src.dependencies import AsyncSessionDep, CurrentUser
from src.repositories.post_progress_repository import PostProgressRepository
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
    return await game_service.read_post(current_user, data.post_slug, data.read_xp)


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


@router.get("/post-status/{post_slug}")
async def get_post_status(
    post_slug: str,
    current_user: CurrentUser,
    db: AsyncSessionDep,
) -> dict:
    """
    Check if user has read a specific post.

    Args:
        post_slug: The post slug to check.
        current_user: The authenticated user.
        db: Database session.

    Returns:
        Dict with has_read status.
    """
    game_service = GameService(db)
    has_read = await game_service.has_read_post(current_user, post_slug)
    return {"has_read": has_read, "post_slug": post_slug}


@router.delete("/dev/reset-post-progress")
async def reset_all_post_progress(
    db: AsyncSessionDep,
) -> dict:
    """
    Reset all post progress records (development only).

    Args:
        db: Database session.

    Returns:
        Dict with deleted count.

    Raises:
        HTTPException: If not in development mode.
    """
    if settings.is_production:
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only available in development mode",
        )

    repo = PostProgressRepository(db)
    deleted_count = await repo.delete_all()
    return {"success": True, "deleted_count": deleted_count}
