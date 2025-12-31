"""
User service for user profile management.

Handles user profile updates and queries.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ConflictException, NotFoundException
from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.schemas.user import UserUpdate


class UserService:
    """Service for user operations."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the user service.

        Args:
            db: The async database session.
        """
        self.db = db
        self.user_repo = UserRepository(db)

    async def get_by_id(self, user_id: UUID) -> User:
        """
        Get a user by their ID.

        Args:
            user_id: The user's UUID.

        Returns:
            The User.

        Raises:
            NotFoundException: If user not found.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User {user_id} not found")
        return user

    async def get_by_username(self, username: str) -> User:
        """
        Get a user by their username.

        Args:
            username: The username.

        Returns:
            The User.

        Raises:
            NotFoundException: If user not found.
        """
        user = await self.user_repo.get_by_username(username)
        if not user:
            raise NotFoundException(f"User {username} not found")
        return user

    async def update_profile(self, user: User, update_data: UserUpdate) -> User:
        """
        Update a user's profile.

        Args:
            user: The user to update.
            update_data: The fields to update.

        Returns:
            The updated User.

        Raises:
            ConflictException: If username is already taken.
        """
        if update_data.username and update_data.username != user.username:
            if await self.user_repo.username_exists(update_data.username):
                raise ConflictException("Username already taken")
            user.username = update_data.username

        if update_data.avatar_url is not None:
            user.avatar_url = update_data.avatar_url

        return await self.user_repo.update(user)

    async def get_all_users(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """
        Get all users with pagination.

        Args:
            skip: Number of users to skip.
            limit: Maximum number of users to return.

        Returns:
            List of Users.
        """
        return await self.user_repo.get_all(skip=skip, limit=limit)

    async def deactivate_user(self, user_id: UUID) -> User:
        """
        Deactivate a user account.

        Args:
            user_id: The user's UUID.

        Returns:
            The deactivated User.

        Raises:
            NotFoundException: If user not found.
        """
        user = await self.get_by_id(user_id)
        user.is_active = False
        return await self.user_repo.update(user)

    async def activate_user(self, user_id: UUID) -> User:
        """
        Activate a user account.

        Args:
            user_id: The user's UUID.

        Returns:
            The activated User.

        Raises:
            NotFoundException: If user not found.
        """
        user = await self.get_by_id(user_id)
        user.is_active = True
        return await self.user_repo.update(user)
