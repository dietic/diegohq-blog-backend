"""
XP transaction repository for tracking XP changes.

Handles CRUD operations and queries for XPTransaction model.
"""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.xp_transaction import XPTransaction
from src.repositories.base import BaseRepository


class XPTransactionRepository(BaseRepository[XPTransaction]):
    """Repository for XPTransaction model operations."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the XP transaction repository.

        Args:
            db: The async database session.
        """
        super().__init__(db, XPTransaction)

    async def create_transaction(
        self,
        user_id: UUID,
        amount: int,
        source: str,
        source_id: str | None = None,
        description: str | None = None,
    ) -> XPTransaction:
        """
        Create a new XP transaction.

        Args:
            user_id: The user's UUID.
            amount: The XP amount (positive or negative).
            source: The source of the XP (e.g., "read_post", "quest", "daily").
            source_id: Optional identifier for the source (e.g., post slug).
            description: Optional description.

        Returns:
            The created XPTransaction.
        """
        transaction = XPTransaction(
            user_id=user_id,
            amount=amount,
            source=source,
            source_id=source_id,
            description=description,
        )
        return await self.create(transaction)

    async def get_user_transactions(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> list[XPTransaction]:
        """
        Get XP transactions for a user.

        Args:
            user_id: The user's UUID.
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of XPTransaction instances.
        """
        result = await self.db.execute(
            select(XPTransaction)
            .where(XPTransaction.user_id == user_id)
            .order_by(XPTransaction.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_total_xp_from_source(self, user_id: UUID, source: str) -> int:
        """
        Get total XP earned from a specific source.

        Args:
            user_id: The user's UUID.
            source: The XP source to filter by.

        Returns:
            The total XP from the specified source.
        """
        result = await self.db.execute(
            select(func.sum(XPTransaction.amount)).where(
                XPTransaction.user_id == user_id,
                XPTransaction.source == source,
            )
        )
        total = result.scalar_one_or_none()
        return total or 0

    async def has_received_xp_for_source(
        self,
        user_id: UUID,
        source: str,
        source_id: str,
    ) -> bool:
        """
        Check if user already received XP for a specific source.

        Args:
            user_id: The user's UUID.
            source: The XP source.
            source_id: The source identifier.

        Returns:
            True if XP was already awarded, False otherwise.
        """
        result = await self.db.execute(
            select(XPTransaction.id).where(
                XPTransaction.user_id == user_id,
                XPTransaction.source == source,
                XPTransaction.source_id == source_id,
            )
        )
        return result.scalar_one_or_none() is not None
