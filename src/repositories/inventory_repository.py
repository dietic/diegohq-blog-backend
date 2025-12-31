"""
Inventory repository for user inventory operations.

Handles CRUD operations and queries for InventoryItem model.
"""

from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.inventory_item import InventoryItem
from src.repositories.base import BaseRepository


class InventoryRepository(BaseRepository[InventoryItem]):
    """Repository for InventoryItem model operations."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the inventory repository.

        Args:
            db: The async database session.
        """
        super().__init__(db, InventoryItem)

    async def get_user_inventory(self, user_id: UUID) -> list[InventoryItem]:
        """
        Get all items in a user's inventory.

        Args:
            user_id: The user's UUID.

        Returns:
            List of InventoryItem instances.
        """
        result = await self.db.execute(
            select(InventoryItem).where(InventoryItem.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_user_item(self, user_id: UUID, item_id: str) -> InventoryItem | None:
        """
        Get a specific item from a user's inventory.

        Args:
            user_id: The user's UUID.
            item_id: The item ID.

        Returns:
            The InventoryItem if found, None otherwise.
        """
        result = await self.db.execute(
            select(InventoryItem).where(
                and_(
                    InventoryItem.user_id == user_id,
                    InventoryItem.item_id == item_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def user_has_item(self, user_id: UUID, item_id: str) -> bool:
        """
        Check if a user has a specific item.

        Args:
            user_id: The user's UUID.
            item_id: The item ID.

        Returns:
            True if the user has the item, False otherwise.
        """
        result = await self.db.execute(
            select(InventoryItem.id).where(
                and_(
                    InventoryItem.user_id == user_id,
                    InventoryItem.item_id == item_id,
                )
            )
        )
        return result.scalar_one_or_none() is not None

    async def add_item_to_user(self, user_id: UUID, item_id: str) -> InventoryItem:
        """
        Add an item to a user's inventory.

        Args:
            user_id: The user's UUID.
            item_id: The item ID.

        Returns:
            The created InventoryItem.
        """
        item = InventoryItem(user_id=user_id, item_id=item_id)
        return await self.create(item)

    async def remove_item_from_user(self, user_id: UUID, item_id: str) -> bool:
        """
        Remove an item from a user's inventory.

        Args:
            user_id: The user's UUID.
            item_id: The item ID.

        Returns:
            True if the item was removed, False if not found.
        """
        item = await self.get_user_item(user_id, item_id)
        if item:
            await self.delete(item)
            return True
        return False
