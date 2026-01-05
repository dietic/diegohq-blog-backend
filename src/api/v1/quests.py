"""
Quest endpoints.

Provides quest submission and progress tracking.
"""

from fastapi import APIRouter, Query

from src.dependencies import AsyncSessionDep, CurrentUser
from src.schemas.quest import (
    CodeSubmitRequest,
    CodeSubmitResponse,
    QuestProgressResponse,
    QuestSubmitRequest,
    QuestSubmitResponse,
    StartQuestResponse,
)
from src.services.quest_service import QuestService

router = APIRouter()


@router.post("/{quest_id}/start", response_model=StartQuestResponse)
async def start_quest(
    quest_id: str,
    current_user: CurrentUser,
    db: AsyncSessionDep,
) -> StartQuestResponse:
    """
    Start a quest.

    Args:
        quest_id: The quest identifier.
        current_user: The authenticated user.
        db: Database session.

    Returns:
        Start result.
    """
    quest_service = QuestService(db)
    return await quest_service.start_quest(current_user, quest_id)


@router.post("/{quest_id}/submit", response_model=QuestSubmitResponse)
async def submit_quest_answer(
    quest_id: str,
    data: QuestSubmitRequest,
    current_user: CurrentUser,
    db: AsyncSessionDep,
) -> QuestSubmitResponse:
    """
    Submit an answer for a multiple-choice quest.

    Args:
        quest_id: The quest identifier.
        data: The answer submission.
        current_user: The authenticated user.
        db: Database session.

    Returns:
        Submission result with feedback.
    """
    quest_service = QuestService(db)
    return await quest_service.submit_answer(current_user, quest_id, data.answer)


@router.post("/{quest_id}/submit-code", response_model=CodeSubmitResponse)
async def submit_quest_code(
    quest_id: str,
    data: CodeSubmitRequest,
    current_user: CurrentUser,
    db: AsyncSessionDep,
) -> CodeSubmitResponse:
    """
    Submit code for a code quest.

    Args:
        quest_id: The quest identifier.
        data: The code submission.
        current_user: The authenticated user.
        db: Database session.

    Returns:
        Submission result with AI feedback.
    """
    quest_service = QuestService(db)
    return await quest_service.submit_code(current_user, quest_id, data.code)


@router.get("/{quest_id}/progress", response_model=QuestProgressResponse | None)
async def get_quest_progress(
    quest_id: str,
    current_user: CurrentUser,
    db: AsyncSessionDep,
) -> QuestProgressResponse | None:
    """
    Get progress on a specific quest.

    Args:
        quest_id: The quest identifier.
        current_user: The authenticated user.
        db: Database session.

    Returns:
        Quest progress if exists.
    """
    quest_service = QuestService(db)
    return await quest_service.get_quest_progress(current_user, quest_id)


@router.get("/progress", response_model=list[QuestProgressResponse])
async def get_all_quest_progress(
    current_user: CurrentUser,
    db: AsyncSessionDep,
    include_in_progress: bool = Query(
        default=False,
        description="Include in-progress quests in the response",
    ),
) -> list[QuestProgressResponse]:
    """
    Get all quest progress for the current user.

    Args:
        current_user: The authenticated user.
        db: Database session.
        include_in_progress: Whether to include in-progress quests.

    Returns:
        List of quest progress.
    """
    quest_service = QuestService(db)
    return await quest_service.get_all_user_progress(current_user, include_in_progress)
