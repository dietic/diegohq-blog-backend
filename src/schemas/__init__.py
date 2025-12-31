"""Schemas package for Pydantic validation models."""

from src.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    TokenPayload,
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
]
