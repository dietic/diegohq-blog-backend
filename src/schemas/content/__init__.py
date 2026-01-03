"""Content schemas package for CMS API validation."""

from src.schemas.content.desktop import (
    DesktopIconCreate,
    DesktopIconResponse,
    DesktopIconUpdate,
    DesktopSettingsResponse,
    DesktopSettingsUpdate,
    ReorderIconsRequest,
)
from src.schemas.content.item import (
    ItemCreate,
    ItemResponse,
    ItemUpdate,
)
from src.schemas.content.post import (
    PostCreate,
    PostResponse,
    PostSummaryResponse,
    PostUpdate,
)
from src.schemas.content.quest import (
    QuestCreate,
    QuestResponse,
    QuestUpdate,
)
from src.schemas.content.window import (
    WindowContentCreate,
    WindowContentResponse,
    WindowContentUpdate,
)

__all__ = [
    # Post
    "PostCreate",
    "PostUpdate",
    "PostResponse",
    "PostSummaryResponse",
    # Quest
    "QuestCreate",
    "QuestUpdate",
    "QuestResponse",
    # Item
    "ItemCreate",
    "ItemUpdate",
    "ItemResponse",
    # Desktop
    "DesktopIconCreate",
    "DesktopIconUpdate",
    "DesktopIconResponse",
    "DesktopSettingsUpdate",
    "DesktopSettingsResponse",
    "ReorderIconsRequest",
    # Window
    "WindowContentCreate",
    "WindowContentUpdate",
    "WindowContentResponse",
]
