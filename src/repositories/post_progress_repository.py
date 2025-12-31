"""
Post progress repository for tracking post reads.

Handles CRUD operations and queries for PostProgress model.
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.post_progress import PostProgress
from src.repositories.base import BaseRepository


class PostProgressRepository(BaseRepository[PostProgress]):
    """Repository for PostProgress model operations."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the post progress repository.

        Args:
            db: The async database session.
        """
        super().__init__(db, PostProgress)

    async def get_user_post(self, user_id: UUID, post_slug: str) -> PostProgress | None:
        """
        Get a user's progress on a specific post.

        Args:
            user_id: The user's UUID.
            post_slug: The post slug.

        Returns:
            The PostProgress if found, None otherwise.
        """
        result = await self.db.execute(
            select(PostProgress).where(
                and_(
                    PostProgress.user_id == user_id,
                    PostProgress.post_slug == post_slug,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_user_posts(self, user_id: UUID) -> list[PostProgress]:
        """
        Get all post progress for a user.

        Args:
            user_id: The user's UUID.

        Returns:
            List of PostProgress instances.
        """
        result = await self.db.execute(
            select(PostProgress).where(PostProgress.user_id == user_id)
        )
        return list(result.scalars().all())

    async def has_read_post(self, user_id: UUID, post_slug: str) -> bool:
        """
        Check if a user has read a specific post.

        Args:
            user_id: The user's UUID.
            post_slug: The post slug.

        Returns:
            True if the post has been read, False otherwise.
        """
        result = await self.db.execute(
            select(PostProgress.id).where(
                and_(
                    PostProgress.user_id == user_id,
                    PostProgress.post_slug == post_slug,
                    PostProgress.has_read == True,  # noqa: E712
                )
            )
        )
        return result.scalar_one_or_none() is not None

    async def mark_as_read(self, user_id: UUID, post_slug: str) -> PostProgress:
        """
        Mark a post as read by a user.

        Args:
            user_id: The user's UUID.
            post_slug: The post slug.

        Returns:
            The updated or created PostProgress.
        """
        progress = await self.get_user_post(user_id, post_slug)
        if progress:
            if not progress.has_read:
                progress.has_read = True
                progress.read_at = datetime.now(UTC)
                await self.db.flush()
                await self.db.refresh(progress)
        else:
            progress = PostProgress(
                user_id=user_id,
                post_slug=post_slug,
                has_read=True,
                read_at=datetime.now(UTC),
            )
            progress = await self.create(progress)
        return progress

    async def unlock_post(
        self,
        user_id: UUID,
        post_slug: str,
        item_id: str | None = None,
    ) -> PostProgress:
        """
        Unlock a post for a user.

        Args:
            user_id: The user's UUID.
            post_slug: The post slug.
            item_id: Optional item used to unlock.

        Returns:
            The updated or created PostProgress.
        """
        progress = await self.get_user_post(user_id, post_slug)
        if progress:
            progress.is_unlocked = True
            progress.unlocked_at = datetime.now(UTC)
            progress.unlocked_with_item = item_id
            await self.db.flush()
            await self.db.refresh(progress)
        else:
            progress = PostProgress(
                user_id=user_id,
                post_slug=post_slug,
                is_unlocked=True,
                unlocked_at=datetime.now(UTC),
                unlocked_with_item=item_id,
            )
            progress = await self.create(progress)
        return progress

    async def is_post_unlocked(self, user_id: UUID, post_slug: str) -> bool:
        """
        Check if a post is unlocked for a user.

        Args:
            user_id: The user's UUID.
            post_slug: The post slug.

        Returns:
            True if the post is unlocked, False otherwise.
        """
        result = await self.db.execute(
            select(PostProgress.id).where(
                and_(
                    PostProgress.user_id == user_id,
                    PostProgress.post_slug == post_slug,
                    PostProgress.is_unlocked == True,  # noqa: E712
                )
            )
        )
        return result.scalar_one_or_none() is not None
