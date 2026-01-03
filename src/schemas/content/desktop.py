"""
Pydantic schemas for desktop-related operations.

Defines request/response schemas for desktop icon and settings endpoints.
"""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


WindowType = Literal["custom", "external"]


class DesktopIconCreate(BaseModel):
    """Schema for creating a new desktop icon."""

    icon_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9-]+$",
        description="Unique icon identifier",
    )
    label: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Icon label",
    )
    icon: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Icon image path",
    )
    position_x: int = Field(
        ...,
        ge=0,
        description="X position on grid",
    )
    position_y: int = Field(
        ...,
        ge=0,
        description="Y position on grid",
    )
    window_type: WindowType = Field(
        ...,
        description="Type of window to open (custom or external)",
    )
    window_id: str | None = Field(
        default=None,
        max_length=100,
        description="Window content ID (required for custom type)",
    )
    external_url: str | None = Field(
        default=None,
        description="URL for external links (required for external type)",
    )
    window_config: dict[str, Any] | None = Field(
        default=None,
        description="Window configuration",
    )
    required_level: int | None = Field(
        default=None,
        ge=1,
        description="Required level to see icon",
    )
    required_item: str | None = Field(
        default=None,
        max_length=100,
        description="Required item to see icon",
    )
    visible: bool = Field(
        default=True,
        description="Whether icon is visible",
    )
    order: int | None = Field(
        default=None,
        description="Display order",
    )

    @model_validator(mode="after")
    def validate_window_relation(self) -> "DesktopIconCreate":
        """Ensure window_id or external_url is provided based on window_type."""
        if self.window_type == "custom" and not self.window_id:
            raise ValueError("window_id is required when window_type is 'custom'")
        if self.window_type == "external" and not self.external_url:
            raise ValueError("external_url is required when window_type is 'external'")
        return self


class DesktopIconUpdate(BaseModel):
    """Schema for updating a desktop icon."""

    icon_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9-]+$",
        description="Unique icon identifier",
    )
    label: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
        description="Icon label",
    )
    icon: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Icon image path",
    )
    position_x: int | None = Field(
        default=None,
        ge=0,
        description="X position on grid",
    )
    position_y: int | None = Field(
        default=None,
        ge=0,
        description="Y position on grid",
    )
    window_type: WindowType | None = Field(
        default=None,
        description="Type of window to open (custom or external)",
    )
    window_id: str | None = Field(
        default=None,
        max_length=100,
        description="Window content ID (required for custom type)",
    )
    external_url: str | None = Field(
        default=None,
        description="URL for external links (required for external type)",
    )
    window_config: dict[str, Any] | None = Field(
        default=None,
        description="Window configuration",
    )
    required_level: int | None = Field(
        default=None,
        ge=1,
        description="Required level to see icon",
    )
    required_item: str | None = Field(
        default=None,
        max_length=100,
        description="Required item to see icon",
    )
    visible: bool | None = Field(
        default=None,
        description="Whether icon is visible",
    )
    order: int | None = Field(
        default=None,
        description="Display order",
    )

    @model_validator(mode="after")
    def validate_window_relation(self) -> "DesktopIconUpdate":
        """Ensure window_id or external_url is provided when changing window_type."""
        if self.window_type == "custom" and self.window_id is None:
            raise ValueError(
                "window_id must be provided when changing window_type to 'custom'"
            )
        if self.window_type == "external" and self.external_url is None:
            raise ValueError(
                "external_url must be provided when changing window_type to 'external'"
            )
        return self


class DesktopIconResponse(BaseModel):
    """Schema for desktop icon response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    icon_id: str
    label: str
    icon: str
    position_x: int
    position_y: int
    window_type: str
    window_id: str | None = None
    external_url: str | None = None
    window_config: dict[str, Any] | None = None
    required_level: int | None = None
    required_item: str | None = None
    visible: bool
    order: int
    created_at: datetime
    updated_at: datetime


class DesktopSettingsUpdate(BaseModel):
    """Schema for updating desktop settings."""

    grid_size: int | None = Field(
        default=None,
        ge=40,
        le=200,
        description="Grid cell size in pixels",
    )
    icon_spacing: int | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Spacing between icons",
    )
    start_position_x: int | None = Field(
        default=None,
        ge=0,
        description="Starting X position",
    )
    start_position_y: int | None = Field(
        default=None,
        ge=0,
        description="Starting Y position",
    )


class DesktopSettingsResponse(BaseModel):
    """Schema for desktop settings response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    key: str
    grid_size: int
    icon_spacing: int
    start_position_x: int
    start_position_y: int
    created_at: datetime
    updated_at: datetime


class ReorderIconsRequest(BaseModel):
    """Schema for reordering icons."""

    icon_ids: list[str] = Field(
        ...,
        min_length=1,
        description="Ordered list of icon IDs",
    )
