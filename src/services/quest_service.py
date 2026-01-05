"""
Quest service for quest submission and validation.

Handles quest answer validation and XP rewards.
"""

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import BadRequestException, NotFoundException
from src.models.user import User
from src.repositories.content.post_repository import PostRepository
from src.repositories.content.quest_repository import QuestRepository
from src.repositories.quest_progress_repository import QuestProgressRepository
from src.repositories.quest_submission_repository import QuestSubmissionRepository
from src.repositories.user_repository import UserRepository
from src.repositories.xp_transaction_repository import XPTransactionRepository
from src.schemas.quest import (
    CodeSubmitResponse,
    QuestProgressResponse,
    QuestSubmitResponse,
    StartQuestResponse,
)
from src.services.ai_service import get_ai_service
from src.services.game_service import GameService


# Quest XP rewards by difficulty
QUEST_XP_REWARDS = {
    "easy": 30,
    "medium": 50,
    "hard": 100,
}

# Cooldown in seconds between code submissions
CODE_SUBMISSION_COOLDOWN = 10

# Number of failed attempts before showing hint
HINT_THRESHOLD = 3


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
        self.quest_content_repo = QuestRepository(db)
        self.quest_submission_repo = QuestSubmissionRepository(db)
        self.post_repo = PostRepository(db)
        self.user_repo = UserRepository(db)
        self.xp_transaction_repo = XPTransactionRepository(db)
        self.game_service = GameService(db)
        self.ai_service = get_ai_service()

    async def start_quest(
        self,
        user: User,
        quest_id: str,
    ) -> StartQuestResponse:
        """
        Start a quest for a user.

        Args:
            user: The user starting the quest.
            quest_id: The quest ID.

        Returns:
            StartQuestResponse with result.

        Raises:
            NotFoundException: If quest doesn't exist.
        """
        # Check if quest exists
        quest = await self.quest_content_repo.get_by_quest_id(quest_id)
        if not quest:
            raise NotFoundException(f"Quest {quest_id} not found")

        # Check if already completed
        existing = await self.quest_progress_repo.get_user_quest(user.id, quest_id)
        if existing and existing.completed:
            return StartQuestResponse(
                success=True,
                quest_id=quest_id,
                already_started=True,
                already_completed=True,
            )

        # Start the quest
        progress, already_started = await self.quest_progress_repo.start_quest(
            user_id=user.id,
            quest_id=quest_id,
        )

        return StartQuestResponse(
            success=True,
            quest_id=quest_id,
            already_started=already_started,
            already_completed=False,
        )

    async def submit_answer(
        self,
        user: User,
        quest_id: str,
        answer: str,
    ) -> QuestSubmitResponse:
        """
        Submit an answer for a multiple-choice quest.

        Args:
            user: The user submitting.
            quest_id: The quest ID.
            answer: The submitted answer.

        Returns:
            QuestSubmitResponse with result.

        Raises:
            BadRequestException: If quest already completed or wrong type.
            NotFoundException: If quest doesn't exist.
        """
        # Check if quest exists
        quest = await self.quest_content_repo.get_by_quest_id(quest_id)
        if not quest:
            raise NotFoundException(f"Quest {quest_id} not found")

        if quest.quest_type != "multiple-choice":
            raise BadRequestException("This quest requires code submission")

        # Check if already completed
        existing = await self.quest_progress_repo.get_user_quest(user.id, quest_id)
        if existing and existing.completed:
            raise BadRequestException("Quest already completed")

        # Normalize answer for comparison
        normalized_answer = answer.strip().lower()
        correct_answer = (quest.correct_answer or "").strip().lower()
        is_correct = normalized_answer == correct_answer

        # Record submission
        await self.quest_submission_repo.create_submission(
            user_id=user.id,
            quest_id=quest_id,
            submission_type="multiple-choice",
            passed=is_correct,
            answer=answer,
        )

        if is_correct:
            # Mark as completed
            progress = await self.quest_progress_repo.mark_completed(
                user_id=user.id,
                quest_id=quest_id,
                answer=answer,
            )

            # Award XP
            xp_amount = quest.xp_reward

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

    async def submit_code(
        self,
        user: User,
        quest_id: str,
        code: str,
    ) -> CodeSubmitResponse:
        """
        Submit code for a code quest.

        Args:
            user: The user submitting.
            quest_id: The quest ID.
            code: The submitted code.

        Returns:
            CodeSubmitResponse with result.

        Raises:
            BadRequestException: If quest already completed, wrong type, or on cooldown.
            NotFoundException: If quest doesn't exist.
        """
        # Check if quest exists
        quest = await self.quest_content_repo.get_by_quest_id(quest_id)
        if not quest:
            raise NotFoundException(f"Quest {quest_id} not found")

        if quest.quest_type != "code":
            raise BadRequestException("This quest requires a multiple-choice answer")

        # Check if already completed
        existing = await self.quest_progress_repo.get_user_quest(user.id, quest_id)
        if existing and existing.completed:
            raise BadRequestException("Quest already completed")

        # Check cooldown
        if existing and existing.last_attempt_at:
            elapsed = (datetime.now(UTC) - existing.last_attempt_at).total_seconds()
            if elapsed < CODE_SUBMISSION_COOLDOWN:
                remaining = int(CODE_SUBMISSION_COOLDOWN - elapsed)
                return CodeSubmitResponse(
                    passed=False,
                    feedback=f"Please wait {remaining} seconds before submitting again.",
                    attempts=existing.attempts,
                    show_hint=False,
                    hint=None,
                    cooldown_seconds=remaining,
                    xp_awarded=0,
                    new_xp=user.xp,
                    new_level=user.level,
                    leveled_up=False,
                )

        # Review code with AI
        passed, feedback = await self.ai_service.review_code(
            code=code,
            language=quest.language or "javascript",
            quest_prompt=quest.prompt,
            ai_criteria=quest.ai_criteria or "",
        )

        # Update last attempt timestamp
        await self.quest_progress_repo.update_last_attempt(
            user_id=user.id,
            quest_id=quest_id,
        )

        # Get updated progress
        progress = await self.quest_progress_repo.get_user_quest(user.id, quest_id)
        attempts = progress.attempts if progress else 1

        # Record submission
        await self.quest_submission_repo.create_submission(
            user_id=user.id,
            quest_id=quest_id,
            submission_type="code",
            passed=passed,
            code=code,
            ai_feedback=feedback,
        )

        # Count failed attempts for hint logic
        failed_count = await self.quest_submission_repo.count_failed_submissions(
            user_id=user.id,
            quest_id=quest_id,
        )
        show_hint = failed_count >= HINT_THRESHOLD and quest.hint is not None

        if passed:
            # Mark as completed
            await self.quest_progress_repo.mark_completed(
                user_id=user.id,
                quest_id=quest_id,
                answer=code[:500],  # Store truncated code as answer
            )

            # Award XP
            xp_amount = quest.xp_reward

            new_xp, new_level, leveled_up = await self.game_service.award_xp(
                user=user,
                amount=xp_amount,
                source="quest",
                source_id=quest_id,
                description=f"Completed code quest: {quest_id}",
            )

            return CodeSubmitResponse(
                passed=True,
                feedback=feedback,
                attempts=attempts,
                show_hint=False,
                hint=None,
                cooldown_seconds=0,
                xp_awarded=xp_amount,
                new_xp=new_xp,
                new_level=new_level,
                leveled_up=leveled_up,
            )
        else:
            return CodeSubmitResponse(
                passed=False,
                feedback=feedback,
                attempts=attempts,
                show_hint=show_hint,
                hint=quest.hint if show_hint else None,
                cooldown_seconds=CODE_SUBMISSION_COOLDOWN,
                xp_awarded=0,
                new_xp=user.xp,
                new_level=user.level,
                leveled_up=False,
            )

    async def get_quest_progress(
        self,
        user: User,
        quest_id: str,
    ) -> QuestProgressResponse | None:
        """
        Get user's progress on a specific quest with quest details.

        Args:
            user: The user.
            quest_id: The quest ID.

        Returns:
            QuestProgressResponse if progress exists, None otherwise.
        """
        progress = await self.quest_progress_repo.get_user_quest(user.id, quest_id)
        if not progress:
            return None

        # Get quest content details
        quest = await self.quest_content_repo.get_by_quest_id(quest_id)
        if not quest:
            return None

        # Get post that references this quest
        post = await self.post_repo.get_by_quest_id(quest_id)
        post_slug = post.slug if post else ""
        post_title = post.title if post else None

        return QuestProgressResponse(
            quest_id=progress.quest_id,
            quest_name=quest.name,
            quest_type=quest.quest_type,
            xp_reward=quest.xp_reward,
            xp_earned=quest.xp_reward if progress.completed else 0,
            host_post_slug=post_slug,
            host_post_title=post_title,
            in_progress=progress.started_at is not None and not progress.completed,
            completed=progress.completed,
            started_at=progress.started_at,
            completed_at=progress.completed_at,
            attempts=progress.attempts,
        )

    async def get_all_user_progress(
        self,
        user: User,
        include_in_progress: bool = False,
    ) -> list[QuestProgressResponse]:
        """
        Get all quest progress for a user with quest details.

        Args:
            user: The user.
            include_in_progress: Whether to include in-progress quests.

        Returns:
            List of QuestProgressResponse.
        """
        progress_list = await self.quest_progress_repo.get_user_quests(user.id)

        results = []
        for p in progress_list:
            # Filter based on include_in_progress
            is_in_progress = p.started_at is not None and not p.completed
            if not p.completed and not (include_in_progress and is_in_progress):
                continue

            # Get quest content details
            quest = await self.quest_content_repo.get_by_quest_id(p.quest_id)
            if not quest:
                continue

            # Get post that references this quest
            post = await self.post_repo.get_by_quest_id(p.quest_id)
            post_slug = post.slug if post else ""
            post_title = post.title if post else None

            results.append(
                QuestProgressResponse(
                    quest_id=p.quest_id,
                    quest_name=quest.name,
                    quest_type=quest.quest_type,
                    xp_reward=quest.xp_reward,
                    xp_earned=quest.xp_reward if p.completed else 0,
                    host_post_slug=post_slug,
                    host_post_title=post_title,
                    in_progress=is_in_progress,
                    completed=p.completed,
                    started_at=p.started_at,
                    completed_at=p.completed_at,
                    attempts=p.attempts,
                )
            )

        # Sort: in-progress first (by started_at), then completed (by completed_at)
        def sort_key(x: QuestProgressResponse) -> tuple[int, datetime]:
            if x.in_progress:
                return (0, x.started_at or datetime.min)
            return (1, x.completed_at or datetime.min)

        results.sort(key=sort_key, reverse=True)
        return results
