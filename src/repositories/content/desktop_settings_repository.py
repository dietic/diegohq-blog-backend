"""
Desktop settings repository for desktop configuration data access.

Provides database operations for DesktopSettings model.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.content.desktop_settings import DesktopSettings
from src.repositories.base import BaseRepository


class DesktopSettingsRepository(BaseRepository[DesktopSettings]):
    """Repository for DesktopSettings model operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the repository."""
        super().__init__(db, DesktopSettings)

    async def get_default(self) -> DesktopSettings | None:
        """Get the default desktop settings."""
        result = await self.db.execute(
            select(DesktopSettings).where(DesktopSettings.key == "default")
        )
        return result.scalar_one_or_none()

    async def get_or_create_default(self) -> DesktopSettings:
        """Get the default settings, creating if not exists."""
        settings = await self.get_default()
        if settings is None:
            settings = DesktopSettings(key="default")
            await self.create(settings)
        return settings
