"""
Daily reward repository for reward tracking.

Handles CRUD operations and queries for DailyReward model.
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.daily_reward import DailyReward
from src.repositories.base import BaseRepository


class DailyRewardRepository(BaseRepository[DailyReward]):
    """Repository for DailyReward model operations."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the daily reward repository.

        Args:
            db: The async database session.
        """
        super().__init__(db, DailyReward)

    async def get_last_claim(self, user_id: UUID) -> DailyReward | None:
        """
        Get the user's most recent daily reward claim.

        Args:
            user_id: The user's UUID.

        Returns:
            The most recent DailyReward if found, None otherwise.
        """
        result = await self.db.execute(
            select(DailyReward)
            .where(DailyReward.user_id == user_id)
            .order_by(DailyReward.claimed_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def has_claimed_today(self, user_id: UUID) -> bool:
        """
        Check if the user has already claimed today's reward.

        Args:
            user_id: The user's UUID.

        Returns:
            True if already claimed today, False otherwise.
        """
        today_start = datetime.now(UTC).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        result = await self.db.execute(
            select(DailyReward.id).where(
                and_(
                    DailyReward.user_id == user_id,
                    DailyReward.claimed_at >= today_start,
                )
            )
        )
        return result.scalar_one_or_none() is not None

    async def claim_reward(
        self,
        user_id: UUID,
        reward_type: str,
        reward_value: int,
        streak_day: int,
    ) -> DailyReward:
        """
        Record a daily reward claim.

        Args:
            user_id: The user's UUID.
            reward_type: The type of reward (e.g., "xp").
            reward_value: The value of the reward.
            streak_day: The current streak day.

        Returns:
            The created DailyReward.
        """
        reward = DailyReward(
            user_id=user_id,
            reward_type=reward_type,
            reward_value=reward_value,
            streak_day=streak_day,
        )
        return await self.create(reward)

    async def get_user_claims(
        self,
        user_id: UUID,
        days: int = 30,
    ) -> list[DailyReward]:
        """
        Get the user's reward claims for the last N days.

        Args:
            user_id: The user's UUID.
            days: Number of days to look back.

        Returns:
            List of DailyReward instances.
        """
        start_date = datetime.now(UTC) - timedelta(days=days)
        result = await self.db.execute(
            select(DailyReward)
            .where(
                and_(
                    DailyReward.user_id == user_id,
                    DailyReward.claimed_at >= start_date,
                )
            )
            .order_by(DailyReward.claimed_at.desc())
        )
        return list(result.scalars().all())

    async def get_total_rewards(self, user_id: UUID) -> int:
        """
        Get the total XP from all daily rewards.

        Args:
            user_id: The user's UUID.

        Returns:
            The total XP from daily rewards.
        """
        result = await self.db.execute(
            select(func.sum(DailyReward.reward_value)).where(
                and_(
                    DailyReward.user_id == user_id,
                    DailyReward.reward_type == "xp",
                )
            )
        )
        total = result.scalar_one_or_none()
        return total or 0
