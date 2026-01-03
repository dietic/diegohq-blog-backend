"""Content repositories package for CMS data access."""

from src.repositories.content.desktop_icon_repository import DesktopIconRepository
from src.repositories.content.desktop_settings_repository import DesktopSettingsRepository
from src.repositories.content.item_repository import ItemRepository
from src.repositories.content.post_repository import PostRepository
from src.repositories.content.quest_repository import QuestRepository
from src.repositories.content.window_content_repository import WindowContentRepository

__all__ = [
    "PostRepository",
    "QuestRepository",
    "ItemRepository",
    "DesktopIconRepository",
    "DesktopSettingsRepository",
    "WindowContentRepository",
]
