"""
FastAPI dependencies for dependency injection.

Provides reusable dependencies for authentication, database sessions, etc.
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import decode_access_token
from src.database import get_async_session
from src.models.user import User
from src.repositories.user_repository import UserRepository

# Type aliases for cleaner dependency injection
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]

# Security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    db: AsyncSessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> User:
    """
    Dependency to get the current authenticated user.

    Args:
        db: Database session.
        credentials: Bearer token credentials.

    Returns:
        The authenticated User object.

    Raises:
        HTTPException: If authentication fails.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(UUID(user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Dependency to get the current active user.

    Args:
        current_user: The current authenticated user.

    Returns:
        The active User object.

    Raises:
        HTTPException: If user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Dependency to get the current admin user.

    Args:
        current_user: The current authenticated user.

    Returns:
        The admin User object.

    Raises:
        HTTPException: If user is not an admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


# Type aliases for common dependencies
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
CurrentAdminUser = Annotated[User, Depends(get_current_admin_user)]
