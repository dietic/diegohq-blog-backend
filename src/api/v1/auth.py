"""
Authentication endpoints.

Provides user registration, login, token refresh, and logout.
"""

from fastapi import APIRouter, Request, status

from src.core.rate_limit import limiter
from src.dependencies import AsyncSessionDep, CurrentUser
from src.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
)
from src.schemas.user import UserProfileResponse
from src.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    data: RegisterRequest,
    db: AsyncSessionDep,
) -> UserProfileResponse:
    """
    Register a new user account.

    Args:
        request: The FastAPI request object.
        data: The registration data.
        db: Database session.

    Returns:
        The created user profile.
    """
    auth_service = AuthService(db)
    user = await auth_service.register(data)
    return UserProfileResponse.model_validate(user)


@router.post("/login", response_model=LoginResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    data: LoginRequest,
    db: AsyncSessionDep,
) -> LoginResponse:
    """
    Login and receive access and refresh tokens.

    Args:
        request: The FastAPI request object.
        data: The login credentials.
        db: Database session.

    Returns:
        Access and refresh tokens.
    """
    auth_service = AuthService(db)
    return await auth_service.login(data.email, data.password)


@router.post("/refresh", response_model=RefreshResponse)
@limiter.limit("20/minute")
async def refresh_tokens(
    request: Request,
    data: RefreshRequest,
    db: AsyncSessionDep,
) -> RefreshResponse:
    """
    Refresh access and refresh tokens.

    Args:
        request: The FastAPI request object.
        data: The refresh token.
        db: Database session.

    Returns:
        New access and refresh tokens.
    """
    auth_service = AuthService(db)
    return await auth_service.refresh_tokens(data.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: CurrentUser,
    db: AsyncSessionDep,
) -> None:
    """
    Logout and revoke all refresh tokens.

    Args:
        current_user: The authenticated user.
        db: Database session.
    """
    auth_service = AuthService(db)
    await auth_service.logout(current_user.id)
