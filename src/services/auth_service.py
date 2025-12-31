"""
Authentication service for user registration and login.

Handles user authentication, token generation, and refresh.
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.core.exceptions import (
    BadRequestException,
    ConflictException,
    UnauthorizedException,
)
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)
from src.models.refresh_token import RefreshToken
from src.models.user import User
from src.repositories.refresh_token_repository import RefreshTokenRepository
from src.repositories.user_repository import UserRepository
from src.schemas.auth import LoginResponse, RefreshResponse, RegisterRequest


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the auth service.

        Args:
            db: The async database session.
        """
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = RefreshTokenRepository(db)

    async def register(self, request: RegisterRequest) -> User:
        """
        Register a new user.

        Args:
            request: The registration request data.

        Returns:
            The created User.

        Raises:
            ConflictException: If email or username already exists.
        """
        # Check if email exists
        if await self.user_repo.email_exists(request.email):
            raise ConflictException("Email already registered")

        # Check if username exists
        if await self.user_repo.username_exists(request.username):
            raise ConflictException("Username already taken")

        # Create user
        user = User(
            username=request.username,
            email=request.email,
            password_hash=hash_password(request.password),
        )

        return await self.user_repo.create(user)

    async def login(self, email: str, password: str) -> LoginResponse:
        """
        Authenticate a user and return tokens.

        Args:
            email: The user's email.
            password: The user's password.

        Returns:
            LoginResponse with access and refresh tokens.

        Raises:
            UnauthorizedException: If credentials are invalid.
        """
        user = await self.user_repo.get_by_email(email)

        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")

        # Generate tokens
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        # Store refresh token hash
        await self._store_refresh_token(user.id, refresh_token)

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def refresh_tokens(self, refresh_token: str) -> RefreshResponse:
        """
        Refresh access and refresh tokens.

        Args:
            refresh_token: The current refresh token.

        Returns:
            RefreshResponse with new tokens.

        Raises:
            UnauthorizedException: If refresh token is invalid.
        """
        payload = decode_refresh_token(refresh_token)
        if not payload:
            raise UnauthorizedException("Invalid refresh token")

        user_id = UUID(payload["sub"])
        user = await self.user_repo.get_by_id(user_id)

        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")

        # Revoke old token
        await self.token_repo.revoke_all_user_tokens(user_id)

        # Generate new tokens
        new_access_token = create_access_token(user.id)
        new_refresh_token = create_refresh_token(user.id)

        # Store new refresh token
        await self._store_refresh_token(user.id, new_refresh_token)

        return RefreshResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        )

    async def logout(self, user_id: UUID) -> bool:
        """
        Logout a user by revoking all refresh tokens.

        Args:
            user_id: The user's UUID.

        Returns:
            True if tokens were revoked.
        """
        await self.token_repo.revoke_all_user_tokens(user_id)
        return True

    async def _store_refresh_token(self, user_id: UUID, token: str) -> RefreshToken:
        """
        Store a hashed refresh token in the database.

        Args:
            user_id: The user's UUID.
            token: The refresh token to store.

        Returns:
            The created RefreshToken record.
        """
        expires_at = datetime.now(UTC) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=hash_token(token),
            expires_at=expires_at,
        )

        return await self.token_repo.create(refresh_token)
