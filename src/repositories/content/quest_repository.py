"""
Quest repository for gamification quest data access.

Provides database operations for Quest model.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.content.quest import Quest
from src.repositories.base import BaseRepository


class QuestRepository(BaseRepository[Quest]):
    """Repository for Quest model operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the repository."""
        super().__init__(db, Quest)

    async def get_by_quest_id(self, quest_id: str) -> Quest | None:
        """Get a quest by its quest_id."""
        result = await self.db.execute(
            select(Quest).where(Quest.quest_id == quest_id)
        )
        return result.scalar_one_or_none()

    async def get_by_item_reward(self, item_id: str) -> list[Quest]:
        """Get quests that reward a specific item."""
        result = await self.db.execute(
            select(Quest).where(Quest.item_reward == item_id)
        )
        return list(result.scalars().all())

    async def quest_id_exists(self, quest_id: str, exclude_id: str | None = None) -> bool:
        """Check if a quest_id already exists."""
        query = select(Quest.id).where(Quest.quest_id == quest_id)
        if exclude_id:
            query = query.where(Quest.id != exclude_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_all_ordered(self, skip: int = 0, limit: int = 100) -> list[Quest]:
        """Get all quests ordered by creation date."""
        result = await self.db.execute(
            select(Quest)
            .order_by(Quest.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
