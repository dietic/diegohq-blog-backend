"""
Pydantic schemas for window content operations.

Defines request/response schemas for window content endpoints.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WindowContentCreate(BaseModel):
    """Schema for creating new window content."""

    window_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9-]+$",
        description="Unique window identifier",
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Window title",
    )
    content: str = Field(
        ...,
        description="Window content (MDX)",
    )
    icon: str | None = Field(
        default=None,
        max_length=255,
        description="Window icon image path (overrides desktop icon)",
    )
    default_width: int = Field(
        default=600,
        ge=200,
        description="Default window width",
    )
    default_height: int = Field(
        default=400,
        ge=150,
        description="Default window height",
    )
    singleton: bool = Field(
        default=True,
        description="Whether only one instance can be open",
    )
    closable: bool = Field(
        default=True,
        description="Whether window can be closed",
    )
    minimizable: bool = Field(
        default=True,
        description="Whether window can be minimized",
    )
    maximizable: bool = Field(
        default=True,
        description="Whether window can be maximized",
    )
    required_level: int | None = Field(
        default=None,
        ge=1,
        description="Required level to access",
    )
    required_item: str | None = Field(
        default=None,
        max_length=100,
        description="Required item to access",
    )


class WindowContentUpdate(BaseModel):
    """Schema for updating window content."""

    window_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9-]+$",
        description="Unique window identifier",
    )
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Window title",
    )
    content: str | None = Field(
        default=None,
        description="Window content (MDX)",
    )
    icon: str | None = Field(
        default=None,
        max_length=255,
        description="Window icon image path (overrides desktop icon)",
    )
    default_width: int | None = Field(
        default=None,
        ge=200,
        description="Default window width",
    )
    default_height: int | None = Field(
        default=None,
        ge=150,
        description="Default window height",
    )
    singleton: bool | None = Field(
        default=None,
        description="Whether only one instance can be open",
    )
    closable: bool | None = Field(
        default=None,
        description="Whether window can be closed",
    )
    minimizable: bool | None = Field(
        default=None,
        description="Whether window can be minimized",
    )
    maximizable: bool | None = Field(
        default=None,
        description="Whether window can be maximized",
    )
    required_level: int | None = Field(
        default=None,
        ge=1,
        description="Required level to access",
    )
    required_item: str | None = Field(
        default=None,
        max_length=100,
        description="Required item to access",
    )


class WindowContentResponse(BaseModel):
    """Schema for window content response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    window_id: str
    title: str
    content: str
    icon: str | None = None
    default_width: int
    default_height: int
    singleton: bool
    closable: bool
    minimizable: bool
    maximizable: bool
    required_level: int | None = None
    required_item: str | None = None
    created_at: datetime
    updated_at: datetime
