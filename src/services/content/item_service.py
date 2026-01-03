"""
Item service for gamification item management.

Handles CRUD operations for items.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ConflictException, NotFoundException
from src.models.content.item import Item
from src.repositories.content.item_repository import ItemRepository


class ItemService:
    """Service for item operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the item service."""
        self.db = db
        self.repo = ItemRepository(db)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Item]:
        """Get all items."""
        return await self.repo.get_all_ordered(skip, limit)

    async def get_by_item_id(self, item_id: str) -> Item:
        """Get an item by its item_id."""
        item = await self.repo.get_by_item_id(item_id)
        if not item:
            raise NotFoundException(f"Item with id '{item_id}' not found")
        return item

    async def get_by_rarity(self, rarity: str) -> list[Item]:
        """Get all items of a specific rarity."""
        return await self.repo.get_by_rarity(rarity)

    async def create(
        self,
        item_id: str,
        name: str,
        description: str,
        icon: str,
        rarity: str = "common",
        flavor_text: str | None = None,
    ) -> Item:
        """Create a new item."""
        # Check if item_id already exists
        if await self.repo.item_id_exists(item_id):
            raise ConflictException(f"Item with id '{item_id}' already exists")

        item = Item(
            item_id=item_id,
            name=name,
            description=description,
            icon=icon,
            rarity=rarity,
            flavor_text=flavor_text,
        )
        return await self.repo.create(item)

    async def update(
        self,
        item_id: str,
        **updates: dict,
    ) -> Item:
        """Update an existing item."""
        item = await self.get_by_item_id(item_id)

        # Check new item_id if being changed
        new_item_id = updates.get("item_id")
        if new_item_id and new_item_id != item_id:
            if await self.repo.item_id_exists(new_item_id, str(item.id)):
                raise ConflictException(f"Item with id '{new_item_id}' already exists")

        # Update fields
        for key, value in updates.items():
            if hasattr(item, key) and value is not None:
                setattr(item, key, value)

        return await self.repo.update(item)

    async def delete(self, item_id: str) -> None:
        """Delete an item."""
        item = await self.get_by_item_id(item_id)
        await self.repo.delete(item)
