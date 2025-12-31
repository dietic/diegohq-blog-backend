"""
Refresh token repository for token management.

Handles CRUD operations and queries for RefreshToken model.
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.refresh_token import RefreshToken
from src.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """Repository for RefreshToken model operations."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the refresh token repository.

        Args:
            db: The async database session.
        """
        super().__init__(db, RefreshToken)

    async def get_active_token(self, user_id: UUID) -> RefreshToken | None:
        """
        Get an active (non-revoked, non-expired) refresh token for a user.

        Args:
            user_id: The user's UUID.

        Returns:
            The RefreshToken if found, None otherwise.
        """
        result = await self.db.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.user_id == user_id,
                    RefreshToken.revoked == False,  # noqa: E712
                    RefreshToken.expires_at > datetime.now(UTC),
                )
            )
        )
        return result.scalar_one_or_none()

    async def revoke_token(self, token_id: UUID) -> bool:
        """
        Revoke a specific refresh token.

        Args:
            token_id: The token's UUID.

        Returns:
            True if the token was revoked, False if not found.
        """
        result = await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.id == token_id)
            .values(revoked=True)
        )
        return result.rowcount > 0

    async def revoke_all_user_tokens(self, user_id: UUID) -> int:
        """
        Revoke all refresh tokens for a user.

        Args:
            user_id: The user's UUID.

        Returns:
            The number of tokens revoked.
        """
        result = await self.db.execute(
            update(RefreshToken)
            .where(
                and_(
                    RefreshToken.user_id == user_id,
                    RefreshToken.revoked == False,  # noqa: E712
                )
            )
            .values(revoked=True)
        )
        return result.rowcount

    async def cleanup_expired_tokens(self) -> int:
        """
        Delete all expired refresh tokens.

        Returns:
            The number of tokens deleted.
        """
        from sqlalchemy import delete

        result = await self.db.execute(
            delete(RefreshToken).where(
                RefreshToken.expires_at < datetime.now(UTC)
            )
        )
        return result.rowcount

    async def get_all_user_tokens(self, user_id: UUID) -> list[RefreshToken]:
        """
        Get all refresh tokens for a user.

        Args:
            user_id: The user's UUID.

        Returns:
            List of RefreshToken instances.
        """
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.user_id == user_id)
        )
        return list(result.scalars().all())
