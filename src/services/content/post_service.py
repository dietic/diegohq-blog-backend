"""
Post service for blog post management.

Handles CRUD operations for blog posts.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ConflictException, NotFoundException
from src.models.content.post import Post
from src.repositories.content.post_repository import PostRepository


def calculate_reading_time(content: str) -> int:
    """Calculate reading time in minutes based on word count."""
    words = len(content.split())
    words_per_minute = 200
    return max(1, round(words / words_per_minute))


class PostService:
    """Service for post operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the post service."""
        self.db = db
        self.repo = PostRepository(db)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Post]:
        """Get all posts."""
        return await self.repo.get_all_ordered(skip, limit)

    async def get_published(self, skip: int = 0, limit: int = 100) -> list[Post]:
        """Get published posts."""
        return await self.repo.get_published(skip, limit)

    async def get_featured(self, limit: int = 10) -> list[Post]:
        """Get featured published posts."""
        return await self.repo.get_featured(limit)

    async def get_by_slug(self, slug: str) -> Post:
        """Get a post by slug."""
        post = await self.repo.get_by_slug(slug)
        if not post:
            raise NotFoundException(f"Post with slug '{slug}' not found")
        return post

    async def get_by_slug_published(self, slug: str) -> Post:
        """Get a published post by slug."""
        post = await self.repo.get_by_slug(slug)
        if not post:
            raise NotFoundException(f"Post with slug '{slug}' not found")
        if not post.published:
            raise NotFoundException(f"Post with slug '{slug}' not found")
        return post

    async def get_by_content_pillar(
        self, pillar: str, skip: int = 0, limit: int = 100
    ) -> list[Post]:
        """Get posts by content pillar."""
        return await self.repo.get_by_content_pillar(pillar, skip, limit)

    async def get_by_tag(self, tag: str, skip: int = 0, limit: int = 100) -> list[Post]:
        """Get posts by tag."""
        return await self.repo.get_by_tag(tag, skip, limit)

    async def create(
        self,
        slug: str,
        title: str,
        excerpt: str,
        content: str,
        content_pillar: str,
        target_level: str,
        author: str = "Diego",
        tags: list[str] | None = None,
        required_level: int | None = None,
        required_item: str | None = None,
        challenge_text: str | None = None,
        read_xp: int = 10,
        quest_id: str | None = None,
        meta_description: str | None = None,
        og_image: str | None = None,
        published: bool = False,
        featured: bool = False,
    ) -> Post:
        """Create a new post."""
        # Check if slug already exists
        if await self.repo.slug_exists(slug):
            raise ConflictException(f"Post with slug '{slug}' already exists")

        post = Post(
            slug=slug,
            title=title,
            excerpt=excerpt,
            content=content,
            content_pillar=content_pillar,
            target_level=target_level,
            author=author,
            tags=tags,
            required_level=required_level,
            required_item=required_item,
            challenge_text=challenge_text,
            read_xp=read_xp,
            quest_id=quest_id,
            meta_description=meta_description,
            og_image=og_image,
            published=published,
            featured=featured,
            reading_time=calculate_reading_time(content),
        )
        return await self.repo.create(post)

    async def update(
        self,
        slug: str,
        new_slug: str | None = None,
        **updates: dict,
    ) -> Post:
        """Update an existing post."""
        post = await self.get_by_slug(slug)

        # Check new slug if being changed
        if new_slug and new_slug != slug:
            if await self.repo.slug_exists(new_slug, str(post.id)):
                raise ConflictException(f"Post with slug '{new_slug}' already exists")
            post.slug = new_slug

        # Update fields
        for key, value in updates.items():
            if hasattr(post, key) and value is not None:
                setattr(post, key, value)

        # Recalculate reading time if content changed
        if "content" in updates:
            post.reading_time = calculate_reading_time(post.content)

        return await self.repo.update(post)

    async def delete(self, slug: str) -> None:
        """Delete a post."""
        post = await self.get_by_slug(slug)
        await self.repo.delete(post)

    async def publish(self, slug: str) -> Post:
        """Publish a post."""
        post = await self.get_by_slug(slug)
        post.published = True
        return await self.repo.update(post)

    async def unpublish(self, slug: str) -> Post:
        """Unpublish a post."""
        post = await self.get_by_slug(slug)
        post.published = False
        return await self.repo.update(post)
