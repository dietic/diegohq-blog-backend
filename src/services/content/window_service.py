"""
Window service for window content management.

Handles CRUD operations for window contents.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ConflictException, NotFoundException
from src.models.content.window_content import WindowContent
from src.repositories.content.window_content_repository import WindowContentRepository


class WindowService:
    """Service for window content operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the window service."""
        self.db = db
        self.repo = WindowContentRepository(db)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[WindowContent]:
        """Get all window contents."""
        return await self.repo.get_all_ordered(skip, limit)

    async def get_by_window_id(self, window_id: str) -> WindowContent:
        """Get window content by its window_id."""
        window = await self.repo.get_by_window_id(window_id)
        if not window:
            raise NotFoundException(f"Window with id '{window_id}' not found")
        return window

    async def create(
        self,
        window_id: str,
        title: str,
        content: str,
        icon: str | None = None,
        default_width: int = 600,
        default_height: int = 400,
        singleton: bool = True,
        closable: bool = True,
        minimizable: bool = True,
        maximizable: bool = True,
        required_level: int | None = None,
        required_item: str | None = None,
    ) -> WindowContent:
        """Create a new window content."""
        # Check if window_id already exists
        if await self.repo.window_id_exists(window_id):
            raise ConflictException(f"Window with id '{window_id}' already exists")

        window = WindowContent(
            window_id=window_id,
            title=title,
            content=content,
            icon=icon,
            default_width=default_width,
            default_height=default_height,
            singleton=singleton,
            closable=closable,
            minimizable=minimizable,
            maximizable=maximizable,
            required_level=required_level,
            required_item=required_item,
        )
        return await self.repo.create(window)

    async def update(
        self,
        window_id: str,
        **updates: dict,
    ) -> WindowContent:
        """Update an existing window content."""
        window = await self.get_by_window_id(window_id)

        # Check new window_id if being changed
        new_window_id = updates.get("window_id")
        if new_window_id and new_window_id != window_id:
            if await self.repo.window_id_exists(new_window_id, str(window.id)):
                raise ConflictException(f"Window with id '{new_window_id}' already exists")

        # Update fields
        for key, value in updates.items():
            if hasattr(window, key) and value is not None:
                setattr(window, key, value)

        return await self.repo.update(window)

    async def delete(self, window_id: str) -> None:
        """Delete a window content."""
        window = await self.get_by_window_id(window_id)
        await self.repo.delete(window)
