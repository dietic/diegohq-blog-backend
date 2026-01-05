"""
Post repository for blog post data access.

Provides database operations for Post model.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.content.post import Post
from src.repositories.base import BaseRepository


class PostRepository(BaseRepository[Post]):
    """Repository for Post model operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the repository."""
        super().__init__(db, Post)

    async def get_by_slug(self, slug: str) -> Post | None:
        """Get a post by its slug."""
        result = await self.db.execute(
            select(Post).where(Post.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_published(self, skip: int = 0, limit: int = 100) -> list[Post]:
        """Get all published posts."""
        result = await self.db.execute(
            select(Post)
            .where(Post.published == True)
            .order_by(Post.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_featured(self, limit: int = 10) -> list[Post]:
        """Get featured published posts."""
        result = await self.db.execute(
            select(Post)
            .where(Post.published == True, Post.featured == True)
            .order_by(Post.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_content_pillar(
        self, pillar: str, skip: int = 0, limit: int = 100
    ) -> list[Post]:
        """Get posts by content pillar."""
        result = await self.db.execute(
            select(Post)
            .where(Post.published == True, Post.content_pillar == pillar)
            .order_by(Post.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_tag(self, tag: str, skip: int = 0, limit: int = 100) -> list[Post]:
        """Get posts that contain a specific tag."""
        result = await self.db.execute(
            select(Post)
            .where(Post.published == True, Post.tags.any(tag))
            .order_by(Post.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def slug_exists(self, slug: str, exclude_id: str | None = None) -> bool:
        """Check if a slug already exists."""
        query = select(Post.id).where(Post.slug == slug)
        if exclude_id:
            query = query.where(Post.id != exclude_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_all_ordered(self, skip: int = 0, limit: int = 100) -> list[Post]:
        """Get all posts ordered by creation date."""
        result = await self.db.execute(
            select(Post)
            .order_by(Post.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_quest_id(self, quest_id: str) -> Post | None:
        """Get a post by its associated quest ID."""
        result = await self.db.execute(
            select(Post).where(Post.quest_id == quest_id)
        )
        return result.scalar_one_or_none()
