"""
User endpoints.

Provides user profile management.
"""

from fastapi import APIRouter

from src.dependencies import AsyncSessionDep, CurrentUser
from src.schemas.user import UserProfileResponse, UserUpdate
from src.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: CurrentUser,
) -> UserProfileResponse:
    """
    Get the current user's profile.

    Args:
        current_user: The authenticated user.

    Returns:
        The user's profile.
    """
    return UserProfileResponse.model_validate(current_user)


@router.patch("/me", response_model=UserProfileResponse)
async def update_current_user_profile(
    current_user: CurrentUser,
    data: UserUpdate,
    db: AsyncSessionDep,
) -> UserProfileResponse:
    """
    Update the current user's profile.

    Args:
        current_user: The authenticated user.
        data: The fields to update.
        db: Database session.

    Returns:
        The updated user profile.
    """
    user_service = UserService(db)
    updated_user = await user_service.update_profile(current_user, data)
    return UserProfileResponse.model_validate(updated_user)
