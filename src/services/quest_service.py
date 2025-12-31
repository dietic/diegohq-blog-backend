"""
Quest service for quest submission and validation.

Handles quest answer validation and XP rewards.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import BadRequestException, NotFoundException
from src.models.user import User
from src.repositories.quest_progress_repository import QuestProgressRepository
from src.repositories.user_repository import UserRepository
from src.repositories.xp_transaction_repository import XPTransactionRepository
from src.schemas.quest import QuestProgressResponse, QuestSubmitResponse
from src.services.game_service import GameService


# Quest XP rewards by difficulty
QUEST_XP_REWARDS = {
    "easy": 30,
    "medium": 50,
    "hard": 100,
}

# Default quest data - in production, this would come from a database or CMS
QUEST_DATA: dict[str, dict[str, str | list[str]]] = {
    # Example quest - this would be expanded based on actual content
    "intro-quest-1": {
        "answer": "hello_world",
        "difficulty": "easy",
        "hint": "A classic first program",
    },
}


class QuestService:
    """Service for quest operations."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the quest service.

        Args:
            db: The async database session.
        """
        self.db = db
        self.quest_progress_repo = QuestProgressRepository(db)
        self.user_repo = UserRepository(db)
        self.xp_transaction_repo = XPTransactionRepository(db)
        self.game_service = GameService(db)

    async def submit_answer(
        self,
        user: User,
        quest_id: str,
        answer: str,
    ) -> QuestSubmitResponse:
        """
        Submit an answer for a quest.

        Args:
            user: The user submitting.
            quest_id: The quest ID.
            answer: The submitted answer.

        Returns:
            QuestSubmitResponse with result.

        Raises:
            BadRequestException: If quest already completed.
        """
        # Check if quest exists
        quest_data = QUEST_DATA.get(quest_id)
        if not quest_data:
            # For unknown quests, we still track but can't validate
            # In production, this would query the CMS
            raise NotFoundException(f"Quest {quest_id} not found")

        # Check if already completed
        existing = await self.quest_progress_repo.get_user_quest(user.id, quest_id)
        if existing and existing.completed:
            raise BadRequestException("Quest already completed")

        # Normalize answer for comparison
        normalized_answer = answer.strip().lower()
        correct_answer = str(quest_data["answer"]).strip().lower()
        is_correct = normalized_answer == correct_answer

        # Get current attempts
        current_attempts = existing.attempts if existing else 0

        if is_correct:
            # Mark as completed
            progress = await self.quest_progress_repo.mark_completed(
                user_id=user.id,
                quest_id=quest_id,
                answer=answer,
            )

            # Award XP based on difficulty
            difficulty = str(quest_data.get("difficulty", "medium"))
            xp_amount = QUEST_XP_REWARDS.get(difficulty, 50)

            new_xp, new_level, leveled_up = await self.game_service.award_xp(
                user=user,
                amount=xp_amount,
                source="quest",
                source_id=quest_id,
                description=f"Completed quest: {quest_id}",
            )

            return QuestSubmitResponse(
                success=True,
                correct=True,
                xp_awarded=xp_amount,
                attempts=progress.attempts,
                new_xp=new_xp,
                new_level=new_level,
                leveled_up=leveled_up,
                feedback="Correct! Quest completed.",
            )
        else:
            # Record failed attempt
            progress = await self.quest_progress_repo.increment_attempts(
                user_id=user.id,
                quest_id=quest_id,
                answer=answer,
            )

            return QuestSubmitResponse(
                success=True,
                correct=False,
                xp_awarded=0,
                attempts=progress.attempts,
                new_xp=user.xp,
                new_level=user.level,
                leveled_up=False,
                feedback="Incorrect. Try again!",
            )

    async def get_quest_progress(
        self,
        user: User,
        quest_id: str,
    ) -> QuestProgressResponse | None:
        """
        Get user's progress on a specific quest.

        Args:
            user: The user.
            quest_id: The quest ID.

        Returns:
            QuestProgressResponse if progress exists, None otherwise.
        """
        progress = await self.quest_progress_repo.get_user_quest(user.id, quest_id)
        if not progress:
            return None

        return QuestProgressResponse(
            quest_id=progress.quest_id,
            completed=progress.completed,
            completed_at=progress.completed_at,
            attempts=progress.attempts,
        )

    async def get_all_user_progress(self, user: User) -> list[QuestProgressResponse]:
        """
        Get all quest progress for a user.

        Args:
            user: The user.

        Returns:
            List of QuestProgressResponse.
        """
        progress_list = await self.quest_progress_repo.get_user_quests(user.id)
        return [
            QuestProgressResponse(
                quest_id=p.quest_id,
                completed=p.completed,
                completed_at=p.completed_at,
                attempts=p.attempts,
            )
            for p in progress_list
        ]
