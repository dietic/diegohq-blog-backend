"""Repositories package for data access layer."""

from src.repositories.content import (
    DesktopIconRepository,
    DesktopSettingsRepository,
    ItemRepository,
    PostRepository,
    QuestRepository,
    WindowContentRepository,
)
from src.repositories.daily_reward_repository import DailyRewardRepository
from src.repositories.inventory_repository import InventoryRepository
from src.repositories.post_progress_repository import PostProgressRepository
from src.repositories.quest_progress_repository import QuestProgressRepository
from src.repositories.refresh_token_repository import RefreshTokenRepository
from src.repositories.user_repository import UserRepository
from src.repositories.xp_transaction_repository import XPTransactionRepository

__all__ = [
    "UserRepository",
    "RefreshTokenRepository",
    "InventoryRepository",
    "QuestProgressRepository",
    "PostProgressRepository",
    "DailyRewardRepository",
    "XPTransactionRepository",
    # Content repositories
    "PostRepository",
    "QuestRepository",
    "ItemRepository",
    "DesktopIconRepository",
    "DesktopSettingsRepository",
    "WindowContentRepository",
]
