"""
Quest content service for quest management.

Handles CRUD operations for quests (content management, not user progress).
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ConflictException, NotFoundException
from src.models.content.quest import Quest
from src.repositories.content.quest_repository import QuestRepository


class QuestContentService:
    """Service for quest content operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the quest content service."""
        self.db = db
        self.repo = QuestRepository(db)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Quest]:
        """Get all quests."""
        return await self.repo.get_all_ordered(skip, limit)

    async def get_by_quest_id(self, quest_id: str) -> Quest:
        """Get a quest by its quest_id."""
        quest = await self.repo.get_by_quest_id(quest_id)
        if not quest:
            raise NotFoundException(f"Quest with id '{quest_id}' not found")
        return quest

    async def get_by_item_reward(self, item_id: str) -> list[Quest]:
        """Get quests that reward a specific item."""
        return await self.repo.get_by_item_reward(item_id)

    async def create(
        self,
        quest_id: str,
        name: str,
        description: str,
        prompt: str,
        quest_type: str,
        xp_reward: int,
        options: list[str] | None = None,
        correct_answer: str | None = None,
        item_reward: str | None = None,
        difficulty: str = "easy",
        language: str | None = None,
        starter_code: str | None = None,
        ai_criteria: str | None = None,
        hint: str | None = None,
    ) -> Quest:
        """Create a new quest."""
        # Check if quest_id already exists
        if await self.repo.quest_id_exists(quest_id):
            raise ConflictException(f"Quest with id '{quest_id}' already exists")

        quest = Quest(
            quest_id=quest_id,
            name=name,
            description=description,
            prompt=prompt,
            quest_type=quest_type,
            options=options,
            correct_answer=correct_answer,
            xp_reward=xp_reward,
            item_reward=item_reward,
            difficulty=difficulty,
            language=language,
            starter_code=starter_code,
            ai_criteria=ai_criteria,
            hint=hint,
        )
        return await self.repo.create(quest)

    async def update(
        self,
        quest_id: str,
        **updates: dict,
    ) -> Quest:
        """Update an existing quest."""
        quest = await self.get_by_quest_id(quest_id)

        # Check new quest_id if being changed
        new_quest_id = updates.get("quest_id")
        if new_quest_id and new_quest_id != quest_id:
            if await self.repo.quest_id_exists(new_quest_id, str(quest.id)):
                raise ConflictException(f"Quest with id '{new_quest_id}' already exists")

        # Update fields
        for key, value in updates.items():
            if hasattr(quest, key) and value is not None:
                setattr(quest, key, value)

        return await self.repo.update(quest)

    async def delete(self, quest_id: str) -> None:
        """Delete a quest."""
        quest = await self.get_by_quest_id(quest_id)
        await self.repo.delete(quest)
