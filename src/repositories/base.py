"""
Base repository class for common database operations.

Provides generic CRUD operations for SQLAlchemy models.
"""

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common database operations."""

    def __init__(self, db: AsyncSession, model: type[ModelType]) -> None:
        """
        Initialize the repository.

        Args:
            db: The async database session.
            model: The SQLAlchemy model class.
        """
        self.db = db
        self.model = model

    async def get_by_id(self, id: UUID) -> ModelType | None:
        """
        Get a record by its ID.

        Args:
            id: The UUID of the record.

        Returns:
            The model instance if found, None otherwise.
        """
        return await self.db.get(self.model, id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """
        Get all records with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of model instances.
        """
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, obj: ModelType) -> ModelType:
        """
        Create a new record.

        Args:
            obj: The model instance to create.

        Returns:
            The created model instance.
        """
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: ModelType) -> ModelType:
        """
        Update an existing record.

        Args:
            obj: The model instance to update.

        Returns:
            The updated model instance.
        """
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: ModelType) -> None:
        """
        Delete a record.

        Args:
            obj: The model instance to delete.
        """
        await self.db.delete(obj)
        await self.db.flush()
