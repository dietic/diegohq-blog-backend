"""
Security utilities for authentication and authorization.

Provides password hashing and JWT token management.
"""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.config import settings

# Password hashing context using Argon2
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using Argon2.

    Args:
        password: The plain text password to hash.

    Returns:
        The hashed password string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: The plain text password to verify.
        hashed_password: The hashed password to compare against.

    Returns:
        True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    user_id: UUID,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        user_id: The user's UUID to encode in the token.
        expires_delta: Optional custom expiration time.

    Returns:
        The encoded JWT access token.
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.now(UTC) + expires_delta
    to_encode: dict[str, Any] = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
    }

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    user_id: UUID,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT refresh token.

    Args:
        user_id: The user's UUID to encode in the token.
        expires_delta: Optional custom expiration time.

    Returns:
        The encoded JWT refresh token.
    """
    if expires_delta is None:
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    expire = datetime.now(UTC) + expires_delta
    to_encode: dict[str, Any] = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
    }

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    Decode and validate a JWT access token.

    Args:
        token: The JWT token to decode.

    Returns:
        The decoded token payload, or None if invalid.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def decode_refresh_token(token: str) -> dict[str, Any] | None:
    """
    Decode and validate a JWT refresh token.

    Args:
        token: The JWT token to decode.

    Returns:
        The decoded token payload, or None if invalid.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None


def hash_token(token: str) -> str:
    """
    Hash a token for secure storage.

    Args:
        token: The token to hash.

    Returns:
        The hashed token string.
    """
    return pwd_context.hash(token)


def verify_token_hash(token: str, hashed_token: str) -> bool:
    """
    Verify a token against its hash.

    Args:
        token: The plain text token to verify.
        hashed_token: The hashed token to compare against.

    Returns:
        True if the token matches, False otherwise.
    """
    return pwd_context.verify(token, hashed_token)
