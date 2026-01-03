"""
Admin content API endpoints.

CRUD operations for content management (requires admin authentication).
"""

from fastapi import APIRouter

from src.dependencies import AsyncSessionDep, CurrentAdminUser
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
    PostUpdate,
    QuestCreate,
    QuestResponse,
    QuestUpdate,
    ReorderIconsRequest,
    WindowContentCreate,
    WindowContentResponse,
    WindowContentUpdate,
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
@router.get("/posts", response_model=list[PostResponse])
async def list_posts(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    skip: int = 0,
    limit: int = 100,
) -> list[PostResponse]:
    """List all posts (admin view includes unpublished)."""
    service = PostService(db)
    posts = await service.get_all(skip, limit)
    return [PostResponse.model_validate(p) for p in posts]


@router.post("/posts", response_model=PostResponse, status_code=201)
async def create_post(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    data: PostCreate,
) -> PostResponse:
    """Create a new post."""
    service = PostService(db)
    post = await service.create(**data.model_dump())
    await db.commit()
    return PostResponse.model_validate(post)


@router.get("/posts/{slug}", response_model=PostResponse)
async def get_post(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    slug: str,
) -> PostResponse:
    """Get a post by slug."""
    service = PostService(db)
    post = await service.get_by_slug(slug)
    return PostResponse.model_validate(post)


@router.patch("/posts/{slug}", response_model=PostResponse)
async def update_post(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    slug: str,
    data: PostUpdate,
) -> PostResponse:
    """Update a post."""
    service = PostService(db)
    updates = data.model_dump(exclude_unset=True)
    updates.pop("slug", None)  # Remove slug from updates to avoid duplicate argument
    new_slug = data.slug  # Get new slug separately if provided
    post = await service.update(slug, new_slug=new_slug, **updates)
    await db.commit()
    return PostResponse.model_validate(post)


@router.delete("/posts/{slug}", status_code=204)
async def delete_post(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    slug: str,
) -> None:
    """Delete a post."""
    service = PostService(db)
    await service.delete(slug)
    await db.commit()


@router.post("/posts/{slug}/publish", response_model=PostResponse)
async def publish_post(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    slug: str,
) -> PostResponse:
    """Publish a post."""
    service = PostService(db)
    post = await service.publish(slug)
    await db.commit()
    return PostResponse.model_validate(post)


@router.post("/posts/{slug}/unpublish", response_model=PostResponse)
async def unpublish_post(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    slug: str,
) -> PostResponse:
    """Unpublish a post."""
    service = PostService(db)
    post = await service.unpublish(slug)
    await db.commit()
    return PostResponse.model_validate(post)


# ===== Quests =====
@router.get("/quests", response_model=list[QuestResponse])
async def list_quests(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    skip: int = 0,
    limit: int = 100,
) -> list[QuestResponse]:
    """List all quests."""
    service = QuestContentService(db)
    quests = await service.get_all(skip, limit)
    return [QuestResponse.model_validate(q) for q in quests]


@router.post("/quests", response_model=QuestResponse, status_code=201)
async def create_quest(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    data: QuestCreate,
) -> QuestResponse:
    """Create a new quest."""
    service = QuestContentService(db)
    quest = await service.create(**data.model_dump())
    await db.commit()
    return QuestResponse.model_validate(quest)


@router.get("/quests/{quest_id}", response_model=QuestResponse)
async def get_quest(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    quest_id: str,
) -> QuestResponse:
    """Get a quest by ID."""
    service = QuestContentService(db)
    quest = await service.get_by_quest_id(quest_id)
    return QuestResponse.model_validate(quest)


@router.patch("/quests/{quest_id}", response_model=QuestResponse)
async def update_quest(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    quest_id: str,
    data: QuestUpdate,
) -> QuestResponse:
    """Update a quest."""
    service = QuestContentService(db)
    quest = await service.update(quest_id, **data.model_dump(exclude_unset=True))
    await db.commit()
    return QuestResponse.model_validate(quest)


@router.delete("/quests/{quest_id}", status_code=204)
async def delete_quest(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    quest_id: str,
) -> None:
    """Delete a quest."""
    service = QuestContentService(db)
    await service.delete(quest_id)
    await db.commit()


# ===== Items =====
@router.get("/items", response_model=list[ItemResponse])
async def list_items(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    skip: int = 0,
    limit: int = 100,
) -> list[ItemResponse]:
    """List all items."""
    service = ItemService(db)
    items = await service.get_all(skip, limit)
    return [ItemResponse.model_validate(i) for i in items]


@router.post("/items", response_model=ItemResponse, status_code=201)
async def create_item(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    data: ItemCreate,
) -> ItemResponse:
    """Create a new item."""
    service = ItemService(db)
    item = await service.create(**data.model_dump())
    await db.commit()
    return ItemResponse.model_validate(item)


@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    item_id: str,
) -> ItemResponse:
    """Get an item by ID."""
    service = ItemService(db)
    item = await service.get_by_item_id(item_id)
    return ItemResponse.model_validate(item)


@router.patch("/items/{item_id}", response_model=ItemResponse)
async def update_item(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    item_id: str,
    data: ItemUpdate,
) -> ItemResponse:
    """Update an item."""
    service = ItemService(db)
    item = await service.update(item_id, **data.model_dump(exclude_unset=True))
    await db.commit()
    return ItemResponse.model_validate(item)


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    item_id: str,
) -> None:
    """Delete an item."""
    service = ItemService(db)
    await service.delete(item_id)
    await db.commit()


# ===== Desktop Icons =====
@router.get("/desktop/icons", response_model=list[DesktopIconResponse])
async def list_desktop_icons(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
) -> list[DesktopIconResponse]:
    """List all desktop icons."""
    service = DesktopService(db)
    icons = await service.get_all_icons()
    return [DesktopIconResponse.model_validate(i) for i in icons]


@router.post("/desktop/icons", response_model=DesktopIconResponse, status_code=201)
async def create_desktop_icon(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    data: DesktopIconCreate,
) -> DesktopIconResponse:
    """Create a new desktop icon."""
    service = DesktopService(db)
    icon = await service.create_icon(**data.model_dump())
    await db.commit()
    return DesktopIconResponse.model_validate(icon)


@router.get("/desktop/icons/{icon_id}", response_model=DesktopIconResponse)
async def get_desktop_icon(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    icon_id: str,
) -> DesktopIconResponse:
    """Get a desktop icon by ID."""
    service = DesktopService(db)
    icon = await service.get_icon_by_id(icon_id)
    return DesktopIconResponse.model_validate(icon)


@router.patch("/desktop/icons/{icon_id}", response_model=DesktopIconResponse)
async def update_desktop_icon(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    icon_id: str,
    data: DesktopIconUpdate,
) -> DesktopIconResponse:
    """Update a desktop icon."""
    service = DesktopService(db)
    icon = await service.update_icon(icon_id, **data.model_dump(exclude_unset=True))
    await db.commit()
    return DesktopIconResponse.model_validate(icon)


@router.delete("/desktop/icons/{icon_id}", status_code=204)
async def delete_desktop_icon(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    icon_id: str,
) -> None:
    """Delete a desktop icon."""
    service = DesktopService(db)
    await service.delete_icon(icon_id)
    await db.commit()


@router.post("/desktop/icons/reorder", response_model=list[DesktopIconResponse])
async def reorder_desktop_icons(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    data: ReorderIconsRequest,
) -> list[DesktopIconResponse]:
    """Reorder desktop icons."""
    service = DesktopService(db)
    icons = await service.reorder_icons(data.icon_ids)
    await db.commit()
    return [DesktopIconResponse.model_validate(i) for i in icons]


# ===== Desktop Settings =====
@router.get("/desktop/settings", response_model=DesktopSettingsResponse)
async def get_desktop_settings(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
) -> DesktopSettingsResponse:
    """Get desktop settings."""
    service = DesktopService(db)
    settings = await service.get_settings()
    return DesktopSettingsResponse.model_validate(settings)


@router.patch("/desktop/settings", response_model=DesktopSettingsResponse)
async def update_desktop_settings(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    data: DesktopSettingsUpdate,
) -> DesktopSettingsResponse:
    """Update desktop settings."""
    service = DesktopService(db)
    settings = await service.update_settings(**data.model_dump(exclude_unset=True))
    await db.commit()
    return DesktopSettingsResponse.model_validate(settings)


# ===== Windows =====
@router.get("/windows", response_model=list[WindowContentResponse])
async def list_windows(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    skip: int = 0,
    limit: int = 100,
) -> list[WindowContentResponse]:
    """List all window contents."""
    service = WindowService(db)
    windows = await service.get_all(skip, limit)
    return [WindowContentResponse.model_validate(w) for w in windows]


@router.post("/windows", response_model=WindowContentResponse, status_code=201)
async def create_window(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    data: WindowContentCreate,
) -> WindowContentResponse:
    """Create new window content."""
    service = WindowService(db)
    window = await service.create(**data.model_dump())
    await db.commit()
    return WindowContentResponse.model_validate(window)


@router.get("/windows/{window_id}", response_model=WindowContentResponse)
async def get_window(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    window_id: str,
) -> WindowContentResponse:
    """Get window content by ID."""
    service = WindowService(db)
    window = await service.get_by_window_id(window_id)
    return WindowContentResponse.model_validate(window)


@router.patch("/windows/{window_id}", response_model=WindowContentResponse)
async def update_window(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    window_id: str,
    data: WindowContentUpdate,
) -> WindowContentResponse:
    """Update window content."""
    service = WindowService(db)
    window = await service.update(window_id, **data.model_dump(exclude_unset=True))
    await db.commit()
    return WindowContentResponse.model_validate(window)


@router.delete("/windows/{window_id}", status_code=204)
async def delete_window(
    db: AsyncSessionDep,
    admin: CurrentAdminUser,
    window_id: str,
) -> None:
    """Delete window content."""
    service = WindowService(db)
    await service.delete(window_id)
    await db.commit()
