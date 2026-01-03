"""
Desktop icon repository for desktop icon data access.

Provides database operations for DesktopIcon model.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.content.desktop_icon import DesktopIcon
from src.repositories.base import BaseRepository


class DesktopIconRepository(BaseRepository[DesktopIcon]):
    """Repository for DesktopIcon model operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the repository."""
        super().__init__(db, DesktopIcon)

    async def get_by_icon_id(self, icon_id: str) -> DesktopIcon | None:
        """Get a desktop icon by its icon_id."""
        result = await self.db.execute(
            select(DesktopIcon).where(DesktopIcon.icon_id == icon_id)
        )
        return result.scalar_one_or_none()

    async def get_visible(self) -> list[DesktopIcon]:
        """Get all visible desktop icons ordered by order."""
        result = await self.db.execute(
            select(DesktopIcon)
            .where(DesktopIcon.visible == True)
            .order_by(DesktopIcon.order)
        )
        return list(result.scalars().all())

    async def get_all_ordered(self) -> list[DesktopIcon]:
        """Get all desktop icons ordered by order."""
        result = await self.db.execute(
            select(DesktopIcon).order_by(DesktopIcon.order)
        )
        return list(result.scalars().all())

    async def icon_id_exists(self, icon_id: str, exclude_id: str | None = None) -> bool:
        """Check if an icon_id already exists."""
        query = select(DesktopIcon.id).where(DesktopIcon.icon_id == icon_id)
        if exclude_id:
            query = query.where(DesktopIcon.id != exclude_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_max_order(self) -> int:
        """Get the maximum order value."""
        from sqlalchemy import func
        result = await self.db.execute(
            select(func.max(DesktopIcon.order))
        )
        max_order = result.scalar()
        return max_order if max_order is not None else -1
