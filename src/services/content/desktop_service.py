"""
Desktop service for desktop icon and settings management.

Handles CRUD operations for desktop icons and settings.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ConflictException, NotFoundException
from src.models.content.desktop_icon import DesktopIcon
from src.models.content.desktop_settings import DesktopSettings
from src.repositories.content.desktop_icon_repository import DesktopIconRepository
from src.repositories.content.desktop_settings_repository import DesktopSettingsRepository


class DesktopService:
    """Service for desktop operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the desktop service."""
        self.db = db
        self.icon_repo = DesktopIconRepository(db)
        self.settings_repo = DesktopSettingsRepository(db)

    # Icon operations
    async def get_all_icons(self) -> list[DesktopIcon]:
        """Get all desktop icons."""
        return await self.icon_repo.get_all_ordered()

    async def get_visible_icons(self) -> list[DesktopIcon]:
        """Get visible desktop icons."""
        return await self.icon_repo.get_visible()

    async def get_icon_by_id(self, icon_id: str) -> DesktopIcon:
        """Get a desktop icon by its icon_id."""
        icon = await self.icon_repo.get_by_icon_id(icon_id)
        if not icon:
            raise NotFoundException(f"Desktop icon with id '{icon_id}' not found")
        return icon

    async def create_icon(
        self,
        icon_id: str,
        label: str,
        icon: str,
        position_x: int,
        position_y: int,
        window_type: str,
        window_id: str | None = None,
        external_url: str | None = None,
        window_config: dict | None = None,
        required_level: int | None = None,
        required_item: str | None = None,
        visible: bool = True,
        order: int | None = None,
    ) -> DesktopIcon:
        """Create a new desktop icon."""
        # Check if icon_id already exists
        if await self.icon_repo.icon_id_exists(icon_id):
            raise ConflictException(f"Desktop icon with id '{icon_id}' already exists")

        # Auto-assign order if not provided
        if order is None:
            order = await self.icon_repo.get_max_order() + 1

        desktop_icon = DesktopIcon(
            icon_id=icon_id,
            label=label,
            icon=icon,
            position_x=position_x,
            position_y=position_y,
            window_type=window_type,
            window_id=window_id,
            external_url=external_url,
            window_config=window_config,
            required_level=required_level,
            required_item=required_item,
            visible=visible,
            order=order,
        )
        return await self.icon_repo.create(desktop_icon)

    async def update_icon(
        self,
        icon_id: str,
        **updates: dict,
    ) -> DesktopIcon:
        """Update an existing desktop icon."""
        desktop_icon = await self.get_icon_by_id(icon_id)

        # Check new icon_id if being changed
        new_icon_id = updates.get("icon_id")
        if new_icon_id and new_icon_id != icon_id:
            if await self.icon_repo.icon_id_exists(new_icon_id, str(desktop_icon.id)):
                raise ConflictException(f"Desktop icon with id '{new_icon_id}' already exists")

        # Update fields
        for key, value in updates.items():
            if hasattr(desktop_icon, key) and value is not None:
                setattr(desktop_icon, key, value)

        return await self.icon_repo.update(desktop_icon)

    async def delete_icon(self, icon_id: str) -> None:
        """Delete a desktop icon."""
        desktop_icon = await self.get_icon_by_id(icon_id)
        await self.icon_repo.delete(desktop_icon)

    async def reorder_icons(self, icon_ids: list[str]) -> list[DesktopIcon]:
        """Reorder desktop icons by the given order of IDs."""
        icons = []
        for order, icon_id in enumerate(icon_ids):
            icon = await self.get_icon_by_id(icon_id)
            icon.order = order
            await self.icon_repo.update(icon)
            icons.append(icon)
        return icons

    # Settings operations
    async def get_settings(self) -> DesktopSettings:
        """Get desktop settings."""
        return await self.settings_repo.get_or_create_default()

    async def update_settings(
        self,
        grid_size: int | None = None,
        icon_spacing: int | None = None,
        start_position_x: int | None = None,
        start_position_y: int | None = None,
    ) -> DesktopSettings:
        """Update desktop settings."""
        settings = await self.settings_repo.get_or_create_default()

        if grid_size is not None:
            settings.grid_size = grid_size
        if icon_spacing is not None:
            settings.icon_spacing = icon_spacing
        if start_position_x is not None:
            settings.start_position_x = start_position_x
        if start_position_y is not None:
            settings.start_position_y = start_position_y

        return await self.settings_repo.update(settings)
