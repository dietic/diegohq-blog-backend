"""
Quest progress repository for quest tracking.

Handles CRUD operations and queries for QuestProgress model.
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.quest_progress import QuestProgress
from src.repositories.base import BaseRepository


class QuestProgressRepository(BaseRepository[QuestProgress]):
    """Repository for QuestProgress model operations."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the quest progress repository.

        Args:
            db: The async database session.
        """
        super().__init__(db, QuestProgress)

    async def get_user_quest(self, user_id: UUID, quest_id: str) -> QuestProgress | None:
        """
        Get a user's progress on a specific quest.

        Args:
            user_id: The user's UUID.
            quest_id: The quest ID.

        Returns:
            The QuestProgress if found, None otherwise.
        """
        result = await self.db.execute(
            select(QuestProgress).where(
                and_(
                    QuestProgress.user_id == user_id,
                    QuestProgress.quest_id == quest_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_user_quests(self, user_id: UUID) -> list[QuestProgress]:
        """
        Get all quest progress for a user.

        Args:
            user_id: The user's UUID.

        Returns:
            List of QuestProgress instances.
        """
        result = await self.db.execute(
            select(QuestProgress).where(QuestProgress.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_completed_quests(self, user_id: UUID) -> list[QuestProgress]:
        """
        Get all completed quests for a user.

        Args:
            user_id: The user's UUID.

        Returns:
            List of completed QuestProgress instances.
        """
        result = await self.db.execute(
            select(QuestProgress).where(
                and_(
                    QuestProgress.user_id == user_id,
                    QuestProgress.completed == True,  # noqa: E712
                )
            )
        )
        return list(result.scalars().all())

    async def is_quest_completed(self, user_id: UUID, quest_id: str) -> bool:
        """
        Check if a user has completed a specific quest.

        Args:
            user_id: The user's UUID.
            quest_id: The quest ID.

        Returns:
            True if the quest is completed, False otherwise.
        """
        result = await self.db.execute(
            select(QuestProgress.id).where(
                and_(
                    QuestProgress.user_id == user_id,
                    QuestProgress.quest_id == quest_id,
                    QuestProgress.completed == True,  # noqa: E712
                )
            )
        )
        return result.scalar_one_or_none() is not None

    async def increment_attempts(
        self,
        user_id: UUID,
        quest_id: str,
        answer: str,
    ) -> QuestProgress:
        """
        Increment attempts for a quest and record the answer.

        Args:
            user_id: The user's UUID.
            quest_id: The quest ID.
            answer: The answer given.

        Returns:
            The updated or created QuestProgress.
        """
        progress = await self.get_user_quest(user_id, quest_id)
        if progress:
            progress.attempts += 1
            progress.answer_given = answer
            await self.db.flush()
            await self.db.refresh(progress)
        else:
            progress = QuestProgress(
                user_id=user_id,
                quest_id=quest_id,
                attempts=1,
                answer_given=answer,
            )
            progress = await self.create(progress)
        return progress

    async def mark_completed(
        self,
        user_id: UUID,
        quest_id: str,
        answer: str,
    ) -> QuestProgress:
        """
        Mark a quest as completed.

        Args:
            user_id: The user's UUID.
            quest_id: The quest ID.
            answer: The correct answer given.

        Returns:
            The updated QuestProgress.
        """
        progress = await self.get_user_quest(user_id, quest_id)
        if progress:
            progress.completed = True
            progress.completed_at = datetime.now(UTC)
            progress.answer_given = answer
            progress.attempts += 1
            await self.db.flush()
            await self.db.refresh(progress)
        else:
            progress = QuestProgress(
                user_id=user_id,
                quest_id=quest_id,
                completed=True,
                completed_at=datetime.now(UTC),
                answer_given=answer,
                attempts=1,
                started_at=datetime.now(UTC),
            )
            progress = await self.create(progress)
        return progress

    async def start_quest(
        self,
        user_id: UUID,
        quest_id: str,
    ) -> tuple[QuestProgress, bool]:
        """
        Start a quest for a user.

        Args:
            user_id: The user's UUID.
            quest_id: The quest ID.

        Returns:
            Tuple of (QuestProgress, already_started: bool).
        """
        progress = await self.get_user_quest(user_id, quest_id)
        if progress:
            return progress, True

        progress = QuestProgress(
            user_id=user_id,
            quest_id=quest_id,
            started_at=datetime.now(UTC),
            attempts=0,
        )
        progress = await self.create(progress)
        return progress, False

    async def update_last_attempt(
        self,
        user_id: UUID,
        quest_id: str,
    ) -> QuestProgress | None:
        """
        Update the last attempt timestamp for cooldown tracking.

        Args:
            user_id: The user's UUID.
            quest_id: The quest ID.

        Returns:
            The updated QuestProgress if found.
        """
        progress = await self.get_user_quest(user_id, quest_id)
        if progress:
            progress.last_attempt_at = datetime.now(UTC)
            progress.attempts += 1
            await self.db.flush()
            await self.db.refresh(progress)
        return progress

    async def get_in_progress_quests(self, user_id: UUID) -> list[QuestProgress]:
        """
        Get all in-progress (started but not completed) quests for a user.

        Args:
            user_id: The user's UUID.

        Returns:
            List of in-progress QuestProgress instances.
        """
        result = await self.db.execute(
            select(QuestProgress).where(
                and_(
                    QuestProgress.user_id == user_id,
                    QuestProgress.started_at.isnot(None),
                    QuestProgress.completed == False,  # noqa: E712
                )
            )
        )
        return list(result.scalars().all())
