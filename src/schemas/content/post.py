"""
Pydantic schemas for post-related operations.

Defines request/response schemas for post endpoints.
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


ContentPillar = Literal["programming", "growth-career", "saas-journey"]
TargetLevel = Literal["beginner", "intermediate", "advanced"]


class PostCreate(BaseModel):
    """Schema for creating a new post."""

    slug: str = Field(
        ...,
        min_length=1,
        max_length=255,
        pattern=r"^[a-z0-9-]+$",
        description="URL-friendly slug",
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Post title",
    )
    excerpt: str = Field(
        ...,
        max_length=300,
        description="Post excerpt/summary",
    )
    content: str = Field(
        ...,
        description="Post content (MDX)",
    )
    content_pillar: ContentPillar = Field(
        ...,
        description="Content pillar category",
    )
    target_level: TargetLevel = Field(
        ...,
        description="Target reader level",
    )
    author: str = Field(
        default="Diego",
        max_length=100,
        description="Post author",
    )
    tags: list[str] | None = Field(
        default=None,
        description="Post tags",
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
    challenge_text: str | None = Field(
        default=None,
        description="Challenge text for locked posts",
    )
    read_xp: int = Field(
        default=10,
        ge=0,
        description="XP reward for reading",
    )
    quest_id: str | None = Field(
        default=None,
        max_length=100,
        description="Associated quest ID",
    )
    meta_description: str | None = Field(
        default=None,
        max_length=160,
        description="SEO meta description",
    )
    og_image: str | None = Field(
        default=None,
        description="Open Graph image URL",
    )
    published: bool = Field(
        default=False,
        description="Whether the post is published",
    )
    featured: bool = Field(
        default=False,
        description="Whether the post is featured",
    )


class PostUpdate(BaseModel):
    """Schema for updating a post."""

    slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        pattern=r"^[a-z0-9-]+$",
        description="URL-friendly slug",
    )
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Post title",
    )
    excerpt: str | None = Field(
        default=None,
        max_length=300,
        description="Post excerpt/summary",
    )
    content: str | None = Field(
        default=None,
        description="Post content (MDX)",
    )
    content_pillar: ContentPillar | None = Field(
        default=None,
        description="Content pillar category",
    )
    target_level: TargetLevel | None = Field(
        default=None,
        description="Target reader level",
    )
    author: str | None = Field(
        default=None,
        max_length=100,
        description="Post author",
    )
    tags: list[str] | None = Field(
        default=None,
        description="Post tags",
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
    challenge_text: str | None = Field(
        default=None,
        description="Challenge text for locked posts",
    )
    read_xp: int | None = Field(
        default=None,
        ge=0,
        description="XP reward for reading",
    )
    quest_id: str | None = Field(
        default=None,
        max_length=100,
        description="Associated quest ID",
    )
    meta_description: str | None = Field(
        default=None,
        max_length=160,
        description="SEO meta description",
    )
    og_image: str | None = Field(
        default=None,
        description="Open Graph image URL",
    )
    published: bool | None = Field(
        default=None,
        description="Whether the post is published",
    )
    featured: bool | None = Field(
        default=None,
        description="Whether the post is featured",
    )


class PostResponse(BaseModel):
    """Schema for full post response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    title: str
    excerpt: str
    content: str
    content_pillar: str
    target_level: str
    author: str
    tags: list[str] | None = None
    required_level: int | None = None
    required_item: str | None = None
    challenge_text: str | None = None
    read_xp: int
    quest_id: str | None = None
    meta_description: str | None = None
    og_image: str | None = None
    published: bool
    featured: bool
    reading_time: int
    created_at: datetime
    updated_at: datetime


class PostSummaryResponse(BaseModel):
    """Schema for post summary response (list view)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    title: str
    excerpt: str
    content_pillar: str
    target_level: str
    author: str
    tags: list[str] | None = None
    required_level: int | None = None
    required_item: str | None = None
    read_xp: int
    published: bool
    featured: bool
    reading_time: int
    created_at: datetime
