"""Content models package for CMS content storage."""

from src.models.content.desktop_icon import DesktopIcon
from src.models.content.desktop_settings import DesktopSettings
from src.models.content.item import Item
from src.models.content.post import Post
from src.models.content.quest import Quest
from src.models.content.window_content import WindowContent

__all__ = [
    "Post",
    "Quest",
    "Item",
    "DesktopIcon",
    "DesktopSettings",
    "WindowContent",
]
