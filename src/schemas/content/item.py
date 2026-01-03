"""
Pydantic schemas for item-related operations.

Defines request/response schemas for item endpoints.
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


ItemRarity = Literal["common", "uncommon", "rare", "legendary"]


class ItemCreate(BaseModel):
    """Schema for creating a new item."""

    item_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9-]+$",
        description="Unique item identifier",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Item name",
    )
    description: str = Field(
        ...,
        max_length=200,
        description="Item description",
    )
    icon: str = Field(
        ...,
        max_length=255,
        description="Item icon (emoji or image path)",
    )
    rarity: ItemRarity = Field(
        default="common",
        description="Item rarity",
    )
    flavor_text: str | None = Field(
        default=None,
        max_length=150,
        description="Flavor text",
    )


class ItemUpdate(BaseModel):
    """Schema for updating an item."""

    item_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9-]+$",
        description="Unique item identifier",
    )
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Item name",
    )
    description: str | None = Field(
        default=None,
        max_length=200,
        description="Item description",
    )
    icon: str | None = Field(
        default=None,
        max_length=255,
        description="Item icon (emoji or image path)",
    )
    rarity: ItemRarity | None = Field(
        default=None,
        description="Item rarity",
    )
    flavor_text: str | None = Field(
        default=None,
        max_length=150,
        description="Flavor text",
    )


class ItemResponse(BaseModel):
    """Schema for item response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    item_id: str
    name: str
    description: str
    icon: str
    rarity: str
    flavor_text: str | None = None
    created_at: datetime
    updated_at: datetime
