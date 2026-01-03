"""Schemas package for Pydantic validation models."""

from src.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    TokenPayload,
)
from src.schemas.contact import (
    ContactReplyRequest,
    ContactSubmissionCreate,
    ContactSubmissionListResponse,
    ContactSubmissionResponse,
)
from src.schemas.content import (
    DesktopIconCreate,
    DesktopIconResponse,
    DesktopIconUpdate,
    DesktopSettingsResponse,
    DesktopSettingsUpdate,
    ItemCreate,
    ItemResponse,
    ItemUpdate,
    PostCreate,
    PostResponse,
    PostSummaryResponse,
    PostUpdate,
    QuestCreate,
    QuestResponse,
    QuestUpdate,
    ReorderIconsRequest,
    WindowContentCreate,
    WindowContentResponse,
    WindowContentUpdate,
)
from src.schemas.game import (
    AccessCheckRequest,
    AccessCheckResponse,
    DailyRewardResponse,
    LevelProgressResponse,
    ReadPostRequest,
    ReadPostResponse,
    UseItemRequest,
    UseItemResponse,
)
from src.schemas.quest import (
    QuestProgressResponse,
    QuestSubmitRequest,
    QuestSubmitResponse,
)
from src.schemas.user import (
    UserCreate,
    UserProfileResponse,
    UserResponse,
    UserUpdate,
)

__all__ = [
    # Auth
    "RegisterRequest",
    "LoginRequest",
    "LoginResponse",
    "RefreshRequest",
    "RefreshResponse",
    "TokenPayload",
    # Contact
    "ContactSubmissionCreate",
    "ContactSubmissionResponse",
    "ContactSubmissionListResponse",
    "ContactReplyRequest",
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserProfileResponse",
    # Game
    "ReadPostRequest",
    "ReadPostResponse",
    "DailyRewardResponse",
    "UseItemRequest",
    "UseItemResponse",
    "AccessCheckRequest",
    "AccessCheckResponse",
    "LevelProgressResponse",
    # Quest
    "QuestSubmitRequest",
    "QuestSubmitResponse",
    "QuestProgressResponse",
    # Content - Post
    "PostCreate",
    "PostUpdate",
    "PostResponse",
    "PostSummaryResponse",
    # Content - Quest
    "QuestCreate",
    "QuestUpdate",
    "QuestResponse",
    # Content - Item
    "ItemCreate",
    "ItemUpdate",
    "ItemResponse",
    # Content - Desktop
    "DesktopIconCreate",
    "DesktopIconUpdate",
    "DesktopIconResponse",
    "DesktopSettingsUpdate",
    "DesktopSettingsResponse",
    "ReorderIconsRequest",
    # Content - Window
    "WindowContentCreate",
    "WindowContentUpdate",
    "WindowContentResponse",
]
