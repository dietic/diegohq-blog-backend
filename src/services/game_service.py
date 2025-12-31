"""
Game service for gamification mechanics.

Handles XP, leveling, daily rewards, and content access.
"""

import math
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import BadRequestException, NotFoundException
from src.models.user import User
from src.repositories.daily_reward_repository import DailyRewardRepository
from src.repositories.inventory_repository import InventoryRepository
from src.repositories.post_progress_repository import PostProgressRepository
from src.repositories.user_repository import UserRepository
from src.repositories.xp_transaction_repository import XPTransactionRepository
from src.schemas.game import (
    AccessCheckResponse,
    DailyRewardResponse,
    LevelProgressResponse,
    ReadPostResponse,
    UseItemResponse,
)


# XP constants
XP_READ_POST = 15  # Base XP for reading a post
XP_DAILY_BASE = 10  # Base XP for daily reward
XP_DAILY_STREAK_BONUS = 5  # Additional XP per streak day (max 7)


class GameService:
    """Service for game mechanics operations."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the game service.

        Args:
            db: The async database session.
        """
        self.db = db
        self.user_repo = UserRepository(db)
        self.post_progress_repo = PostProgressRepository(db)
        self.daily_reward_repo = DailyRewardRepository(db)
        self.inventory_repo = InventoryRepository(db)
        self.xp_transaction_repo = XPTransactionRepository(db)

    @staticmethod
    def calculate_level_from_xp(xp: int) -> int:
        """
        Calculate level from XP using formula: XP = floor(level^1.5 * 100).

        Args:
            xp: The total XP.

        Returns:
            The calculated level.
        """
        if xp <= 0:
            return 1
        # Inverse: level = (XP / 100) ^ (1/1.5)
        level = int((xp / 100) ** (1 / 1.5))
        return max(1, level)

    @staticmethod
    def calculate_xp_for_level(level: int) -> int:
        """
        Calculate XP required for a specific level.

        Args:
            level: The target level.

        Returns:
            The XP required to reach that level.
        """
        if level <= 1:
            return 0
        return int(math.floor((level ** 1.5) * 100))

    def get_level_progress(self, user: User) -> LevelProgressResponse:
        """
        Get detailed level progress for a user.

        Args:
            user: The user.

        Returns:
            LevelProgressResponse with progress details.
        """
        current_xp = user.xp
        current_level = user.level
        xp_for_current = self.calculate_xp_for_level(current_level)
        xp_for_next = self.calculate_xp_for_level(current_level + 1)

        xp_progress = current_xp - xp_for_current
        xp_needed = xp_for_next - xp_for_current

        progress_percentage = (xp_progress / xp_needed * 100) if xp_needed > 0 else 100

        return LevelProgressResponse(
            current_level=current_level,
            current_xp=current_xp,
            xp_for_current_level=xp_for_current,
            xp_for_next_level=xp_for_next,
            xp_progress=xp_progress,
            progress_percentage=round(progress_percentage, 2),
        )

    async def award_xp(
        self,
        user: User,
        amount: int,
        source: str,
        source_id: str | None = None,
        description: str | None = None,
    ) -> tuple[int, int, bool]:
        """
        Award XP to a user and handle leveling.

        Args:
            user: The user to award XP to.
            amount: The XP amount.
            source: The source of the XP.
            source_id: Optional source identifier.
            description: Optional description.

        Returns:
            Tuple of (new_xp, new_level, leveled_up).
        """
        old_level = user.level
        new_xp = user.xp + amount
        new_level = self.calculate_level_from_xp(new_xp)

        # Update user
        await self.user_repo.update_xp(user.id, new_xp, new_level)

        # Record transaction
        await self.xp_transaction_repo.create_transaction(
            user_id=user.id,
            amount=amount,
            source=source,
            source_id=source_id,
            description=description,
        )

        return new_xp, new_level, new_level > old_level

    async def read_post(self, user: User, post_slug: str) -> ReadPostResponse:
        """
        Mark a post as read and award XP if first read.

        Args:
            user: The user.
            post_slug: The post slug.

        Returns:
            ReadPostResponse with XP and level info.
        """
        # Check if already read
        already_read = await self.post_progress_repo.has_read_post(user.id, post_slug)

        if already_read:
            return ReadPostResponse(
                success=True,
                xp_awarded=0,
                already_read=True,
                new_xp=user.xp,
                new_level=user.level,
                leveled_up=False,
            )

        # Mark as read
        await self.post_progress_repo.mark_as_read(user.id, post_slug)

        # Award XP
        new_xp, new_level, leveled_up = await self.award_xp(
            user=user,
            amount=XP_READ_POST,
            source="read_post",
            source_id=post_slug,
            description=f"Read post: {post_slug}",
        )

        return ReadPostResponse(
            success=True,
            xp_awarded=XP_READ_POST,
            already_read=False,
            new_xp=new_xp,
            new_level=new_level,
            leveled_up=leveled_up,
        )

    async def claim_daily_reward(self, user: User) -> DailyRewardResponse:
        """
        Claim the daily reward for a user.

        Args:
            user: The user.

        Returns:
            DailyRewardResponse with reward info.
        """
        # Check if already claimed today
        if await self.daily_reward_repo.has_claimed_today(user.id):
            next_claim = (
                datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
                + timedelta(days=1)
            )
            return DailyRewardResponse(
                success=False,
                xp_awarded=0,
                streak_day=user.current_streak,
                new_xp=user.xp,
                new_level=user.level,
                leveled_up=False,
                already_claimed=True,
                next_claim_at=next_claim,
            )

        # Calculate streak
        last_claim = await self.daily_reward_repo.get_last_claim(user.id)
        if last_claim:
            yesterday = datetime.now(UTC).date() - timedelta(days=1)
            if last_claim.claimed_at.date() == yesterday:
                new_streak = user.current_streak + 1
            else:
                new_streak = 1
        else:
            new_streak = 1

        # Calculate reward
        streak_bonus = min(new_streak - 1, 7) * XP_DAILY_STREAK_BONUS
        xp_amount = XP_DAILY_BASE + streak_bonus

        # Update streak
        longest_streak = max(user.longest_streak, new_streak)
        await self.user_repo.update_streak(user.id, new_streak, longest_streak)

        # Award XP
        new_xp, new_level, leveled_up = await self.award_xp(
            user=user,
            amount=xp_amount,
            source="daily_reward",
            description=f"Daily reward (streak day {new_streak})",
        )

        # Record reward
        await self.daily_reward_repo.claim_reward(
            user_id=user.id,
            reward_type="xp",
            reward_value=xp_amount,
            streak_day=new_streak,
        )

        return DailyRewardResponse(
            success=True,
            xp_awarded=xp_amount,
            streak_day=new_streak,
            new_xp=new_xp,
            new_level=new_level,
            leveled_up=leveled_up,
            already_claimed=False,
            next_claim_at=None,
        )

    async def use_item(
        self,
        user: User,
        item_id: str,
        target_slug: str | None = None,
    ) -> UseItemResponse:
        """
        Use an item from the user's inventory.

        Args:
            user: The user.
            item_id: The item to use.
            target_slug: Optional target (e.g., post to unlock).

        Returns:
            UseItemResponse with result.

        Raises:
            NotFoundException: If item not in inventory.
            BadRequestException: If item cannot be used.
        """
        # Check if user has item
        if not await self.inventory_repo.user_has_item(user.id, item_id):
            raise NotFoundException(f"Item {item_id} not in inventory")

        # Handle different item types
        target_unlocked = None
        effect = "Item used"

        if item_id.startswith("key_") and target_slug:
            # Key items unlock posts
            await self.post_progress_repo.unlock_post(user.id, target_slug, item_id)
            target_unlocked = target_slug
            effect = f"Unlocked post: {target_slug}"
            # Remove consumable key
            await self.inventory_repo.remove_item_from_user(user.id, item_id)
        else:
            # Default: just mark as used (consumable)
            await self.inventory_repo.remove_item_from_user(user.id, item_id)
            effect = f"Used item: {item_id}"

        return UseItemResponse(
            success=True,
            item_id=item_id,
            effect=effect,
            target_unlocked=target_unlocked,
        )

    async def check_access(
        self,
        user: User,
        post_slug: str,
        required_level: int | None = None,
        required_item: str | None = None,
    ) -> AccessCheckResponse:
        """
        Check if a user has access to content.

        Args:
            user: The user.
            post_slug: The post slug.
            required_level: Optional level requirement.
            required_item: Optional item requirement.

        Returns:
            AccessCheckResponse with access status.
        """
        has_access = True
        reason = None
        has_required_item = None

        # Check level requirement
        if required_level and user.level < required_level:
            has_access = False
            reason = f"Requires level {required_level}"

        # Check item requirement
        if required_item:
            has_item = await self.inventory_repo.user_has_item(user.id, required_item)
            has_required_item = has_item

            # Check if already unlocked with item
            is_unlocked = await self.post_progress_repo.is_post_unlocked(
                user.id, post_slug
            )

            if not has_item and not is_unlocked:
                has_access = False
                reason = f"Requires item: {required_item}"

        return AccessCheckResponse(
            has_access=has_access,
            reason=reason,
            user_level=user.level,
            required_level=required_level,
            has_required_item=has_required_item,
        )
