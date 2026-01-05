"""
Quest submission repository for tracking submission history.

Handles CRUD operations and queries for QuestSubmission model.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.quest_submission import QuestSubmission
from src.repositories.base import BaseRepository


class QuestSubmissionRepository(BaseRepository[QuestSubmission]):
    """Repository for QuestSubmission model operations."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the quest submission repository.

        Args:
            db: The async database session.
        """
        super().__init__(db, QuestSubmission)

    async def create_submission(
        self,
        user_id: UUID,
        quest_id: str,
        submission_type: str,
        passed: bool,
        code: str | None = None,
        answer: str | None = None,
        ai_feedback: str | None = None,
    ) -> QuestSubmission:
        """
        Create a new quest submission record.

        Args:
            user_id: The user's UUID.
            quest_id: The quest ID.
            submission_type: Type of submission ("code" or "multiple-choice").
            passed: Whether the submission passed.
            code: The code submitted (for code quests).
            answer: The answer submitted (for multiple-choice).
            ai_feedback: AI feedback (for code quests).

        Returns:
            The created QuestSubmission.
        """
        submission = QuestSubmission(
            user_id=user_id,
            quest_id=quest_id,
            submission_type=submission_type,
            passed=passed,
            code_submitted=code,
            answer_submitted=answer,
            ai_feedback=ai_feedback,
            submitted_at=datetime.utcnow(),
        )
        return await self.create(submission)

    async def get_user_submissions(
        self,
        user_id: UUID,
        quest_id: str,
    ) -> list[QuestSubmission]:
        """
        Get all submissions for a user on a specific quest.

        Args:
            user_id: The user's UUID.
            quest_id: The quest ID.

        Returns:
            List of QuestSubmission instances.
        """
        result = await self.db.execute(
            select(QuestSubmission)
            .where(
                and_(
                    QuestSubmission.user_id == user_id,
                    QuestSubmission.quest_id == quest_id,
                )
            )
            .order_by(QuestSubmission.submitted_at.desc())
        )
        return list(result.scalars().all())

    async def count_user_submissions(
        self,
        user_id: UUID,
        quest_id: str,
    ) -> int:
        """
        Count total submissions for a user on a specific quest.

        Args:
            user_id: The user's UUID.
            quest_id: The quest ID.

        Returns:
            Number of submissions.
        """
        result = await self.db.execute(
            select(func.count(QuestSubmission.id)).where(
                and_(
                    QuestSubmission.user_id == user_id,
                    QuestSubmission.quest_id == quest_id,
                )
            )
        )
        return result.scalar() or 0

    async def count_failed_submissions(
        self,
        user_id: UUID,
        quest_id: str,
    ) -> int:
        """
        Count failed submissions for a user on a specific quest.

        Args:
            user_id: The user's UUID.
            quest_id: The quest ID.

        Returns:
            Number of failed submissions.
        """
        result = await self.db.execute(
            select(func.count(QuestSubmission.id)).where(
                and_(
                    QuestSubmission.user_id == user_id,
                    QuestSubmission.quest_id == quest_id,
                    QuestSubmission.passed == False,  # noqa: E712
                )
            )
        )
        return result.scalar() or 0
