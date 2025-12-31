"""
User repository for user-related database operations.

Handles CRUD operations and queries for User model.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the user repository.

        Args:
            db: The async database session.
        """
        super().__init__(db, User)

    async def get_by_email(self, email: str) -> User | None:
        """
        Get a user by email address.

        Args:
            email: The email address to search for.

        Returns:
            The User if found, None otherwise.
        """
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """
        Get a user by username.

        Args:
            username: The username to search for.

        Returns:
            The User if found, None otherwise.
        """
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """
        Check if an email is already registered.

        Args:
            email: The email to check.

        Returns:
            True if the email exists, False otherwise.
        """
        result = await self.db.execute(
            select(User.id).where(User.email == email)
        )
        return result.scalar_one_or_none() is not None

    async def username_exists(self, username: str) -> bool:
        """
        Check if a username is already taken.

        Args:
            username: The username to check.

        Returns:
            True if the username exists, False otherwise.
        """
        result = await self.db.execute(
            select(User.id).where(User.username == username)
        )
        return result.scalar_one_or_none() is not None

    async def update_xp(self, user_id: UUID, new_xp: int, new_level: int) -> User | None:
        """
        Update a user's XP and level.

        Args:
            user_id: The user's UUID.
            new_xp: The new XP value.
            new_level: The new level value.

        Returns:
            The updated User if found, None otherwise.
        """
        user = await self.get_by_id(user_id)
        if user:
            user.xp = new_xp
            user.level = new_level
            await self.db.flush()
            await self.db.refresh(user)
        return user

    async def update_streak(
        self,
        user_id: UUID,
        current_streak: int,
        longest_streak: int,
    ) -> User | None:
        """
        Update a user's streak values.

        Args:
            user_id: The user's UUID.
            current_streak: The new current streak value.
            longest_streak: The new longest streak value.

        Returns:
            The updated User if found, None otherwise.
        """
        user = await self.get_by_id(user_id)
        if user:
            user.current_streak = current_streak
            user.longest_streak = longest_streak
            await self.db.flush()
            await self.db.refresh(user)
        return user
