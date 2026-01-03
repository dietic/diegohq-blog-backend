"""
Window content repository for custom window data access.

Provides database operations for WindowContent model.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.content.window_content import WindowContent
from src.repositories.base import BaseRepository


class WindowContentRepository(BaseRepository[WindowContent]):
    """Repository for WindowContent model operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the repository."""
        super().__init__(db, WindowContent)

    async def get_by_window_id(self, window_id: str) -> WindowContent | None:
        """Get window content by its window_id."""
        result = await self.db.execute(
            select(WindowContent).where(WindowContent.window_id == window_id)
        )
        return result.scalar_one_or_none()

    async def window_id_exists(self, window_id: str, exclude_id: str | None = None) -> bool:
        """Check if a window_id already exists."""
        query = select(WindowContent.id).where(WindowContent.window_id == window_id)
        if exclude_id:
            query = query.where(WindowContent.id != exclude_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_all_ordered(self, skip: int = 0, limit: int = 100) -> list[WindowContent]:
        """Get all window contents ordered by title."""
        result = await self.db.execute(
            select(WindowContent)
            .order_by(WindowContent.title)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
