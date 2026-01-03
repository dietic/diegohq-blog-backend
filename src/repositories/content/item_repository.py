"""
Item repository for gamification item data access.

Provides database operations for Item model.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.content.item import Item
from src.repositories.base import BaseRepository


class ItemRepository(BaseRepository[Item]):
    """Repository for Item model operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the repository."""
        super().__init__(db, Item)

    async def get_by_item_id(self, item_id: str) -> Item | None:
        """Get an item by its item_id."""
        result = await self.db.execute(
            select(Item).where(Item.item_id == item_id)
        )
        return result.scalar_one_or_none()

    async def get_by_rarity(self, rarity: str) -> list[Item]:
        """Get all items of a specific rarity."""
        result = await self.db.execute(
            select(Item).where(Item.rarity == rarity)
        )
        return list(result.scalars().all())

    async def item_id_exists(self, item_id: str, exclude_id: str | None = None) -> bool:
        """Check if an item_id already exists."""
        query = select(Item.id).where(Item.item_id == item_id)
        if exclude_id:
            query = query.where(Item.id != exclude_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_all_ordered(self, skip: int = 0, limit: int = 100) -> list[Item]:
        """Get all items ordered by name."""
        result = await self.db.execute(
            select(Item)
            .order_by(Item.name)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
