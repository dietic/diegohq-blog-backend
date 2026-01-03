"""
Public content API endpoints.

Read-only endpoints for content (no authentication required).
"""

from fastapi import APIRouter

from src.dependencies import AsyncSessionDep
from src.schemas.content import (
    DesktopIconResponse,
    DesktopSettingsResponse,
    ItemResponse,
    PostResponse,
    PostSummaryResponse,
    QuestResponse,
    WindowContentResponse,
)
from src.services.content import (
    DesktopService,
    ItemService,
    PostService,
    QuestContentService,
    WindowService,
)

router = APIRouter()


# ===== Posts =====
@router.get("/posts", response_model=list[PostSummaryResponse])
async def list_published_posts(
    db: AsyncSessionDep,
    skip: int = 0,
    limit: int = 100,
) -> list[PostSummaryResponse]:
    """List all published posts."""
    service = PostService(db)
    posts = await service.get_published(skip, limit)
    return [PostSummaryResponse.model_validate(p) for p in posts]


@router.get("/posts/featured", response_model=list[PostSummaryResponse])
async def list_featured_posts(
    db: AsyncSessionDep,
    limit: int = 10,
) -> list[PostSummaryResponse]:
    """List featured published posts."""
    service = PostService(db)
    posts = await service.get_featured(limit)
    return [PostSummaryResponse.model_validate(p) for p in posts]


@router.get("/posts/pillar/{pillar}", response_model=list[PostSummaryResponse])
async def list_posts_by_pillar(
    db: AsyncSessionDep,
    pillar: str,
    skip: int = 0,
    limit: int = 100,
) -> list[PostSummaryResponse]:
    """List published posts by content pillar."""
    service = PostService(db)
    posts = await service.get_by_content_pillar(pillar, skip, limit)
    return [PostSummaryResponse.model_validate(p) for p in posts]


@router.get("/posts/tag/{tag}", response_model=list[PostSummaryResponse])
async def list_posts_by_tag(
    db: AsyncSessionDep,
    tag: str,
    skip: int = 0,
    limit: int = 100,
) -> list[PostSummaryResponse]:
    """List published posts by tag."""
    service = PostService(db)
    posts = await service.get_by_tag(tag, skip, limit)
    return [PostSummaryResponse.model_validate(p) for p in posts]


@router.get("/posts/{slug}", response_model=PostResponse)
async def get_published_post(
    db: AsyncSessionDep,
    slug: str,
) -> PostResponse:
    """Get a published post by slug."""
    service = PostService(db)
    post = await service.get_by_slug_published(slug)
    return PostResponse.model_validate(post)


# ===== Quests =====
@router.get("/quests", response_model=list[QuestResponse])
async def list_quests(
    db: AsyncSessionDep,
    skip: int = 0,
    limit: int = 100,
) -> list[QuestResponse]:
    """List all quests."""
    service = QuestContentService(db)
    quests = await service.get_all(skip, limit)
    return [QuestResponse.model_validate(q) for q in quests]


@router.get("/quests/{quest_id}", response_model=QuestResponse)
async def get_quest(
    db: AsyncSessionDep,
    quest_id: str,
) -> QuestResponse:
    """Get a quest by ID."""
    service = QuestContentService(db)
    quest = await service.get_by_quest_id(quest_id)
    return QuestResponse.model_validate(quest)


@router.get("/quests/post/{post_slug}", response_model=list[QuestResponse])
async def get_quests_by_post(
    db: AsyncSessionDep,
    post_slug: str,
) -> list[QuestResponse]:
    """Get quests for a specific post."""
    service = QuestContentService(db)
    quests = await service.get_by_post_slug(post_slug)
    return [QuestResponse.model_validate(q) for q in quests]


# ===== Items =====
@router.get("/items", response_model=list[ItemResponse])
async def list_items(
    db: AsyncSessionDep,
    skip: int = 0,
    limit: int = 100,
) -> list[ItemResponse]:
    """List all items."""
    service = ItemService(db)
    items = await service.get_all(skip, limit)
    return [ItemResponse.model_validate(i) for i in items]


@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(
    db: AsyncSessionDep,
    item_id: str,
) -> ItemResponse:
    """Get an item by ID."""
    service = ItemService(db)
    item = await service.get_by_item_id(item_id)
    return ItemResponse.model_validate(item)


@router.get("/items/rarity/{rarity}", response_model=list[ItemResponse])
async def get_items_by_rarity(
    db: AsyncSessionDep,
    rarity: str,
) -> list[ItemResponse]:
    """Get items by rarity."""
    service = ItemService(db)
    items = await service.get_by_rarity(rarity)
    return [ItemResponse.model_validate(i) for i in items]


# ===== Desktop =====
@router.get("/desktop/icons", response_model=list[DesktopIconResponse])
async def list_visible_desktop_icons(
    db: AsyncSessionDep,
) -> list[DesktopIconResponse]:
    """List visible desktop icons."""
    service = DesktopService(db)
    icons = await service.get_visible_icons()
    return [DesktopIconResponse.model_validate(i) for i in icons]


@router.get("/desktop/icons/{icon_id}", response_model=DesktopIconResponse)
async def get_desktop_icon(
    db: AsyncSessionDep,
    icon_id: str,
) -> DesktopIconResponse:
    """Get a desktop icon by ID."""
    service = DesktopService(db)
    icon = await service.get_icon_by_id(icon_id)
    return DesktopIconResponse.model_validate(icon)


@router.get("/desktop/settings", response_model=DesktopSettingsResponse)
async def get_desktop_settings(
    db: AsyncSessionDep,
) -> DesktopSettingsResponse:
    """Get desktop settings."""
    service = DesktopService(db)
    settings = await service.get_settings()
    return DesktopSettingsResponse.model_validate(settings)


# ===== Windows =====
@router.get("/windows", response_model=list[WindowContentResponse])
async def list_windows(
    db: AsyncSessionDep,
    skip: int = 0,
    limit: int = 100,
) -> list[WindowContentResponse]:
    """List all window contents."""
    service = WindowService(db)
    windows = await service.get_all(skip, limit)
    return [WindowContentResponse.model_validate(w) for w in windows]


@router.get("/windows/{window_id}", response_model=WindowContentResponse)
async def get_window(
    db: AsyncSessionDep,
    window_id: str,
) -> WindowContentResponse:
    """Get window content by ID."""
    service = WindowService(db)
    window = await service.get_by_window_id(window_id)
    return WindowContentResponse.model_validate(window)
