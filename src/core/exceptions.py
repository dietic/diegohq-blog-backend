"""
Custom exception classes for the application.

Provides domain-specific exceptions that map to HTTP status codes.
"""

from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base exception for application-specific errors."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundException(AppException):
    """Exception raised when a requested resource is not found."""

    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class BadRequestException(AppException):
    """Exception raised for invalid request data."""

    def __init__(self, detail: str = "Bad request") -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedException(AppException):
    """Exception raised when authentication is required but not provided."""

    def __init__(self, detail: str = "Not authenticated") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(AppException):
    """Exception raised when user lacks permission for an action."""

    def __init__(self, detail: str = "Access forbidden") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ConflictException(AppException):
    """Exception raised when there's a resource conflict."""

    def __init__(self, detail: str = "Resource conflict") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class ValidationException(AppException):
    """Exception raised for validation errors."""

    def __init__(self, detail: str = "Validation error") -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class InternalServerException(AppException):
    """Exception raised for internal server errors."""

    def __init__(self, detail: str = "Internal server error") -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class TooManyRequestsException(AppException):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, detail: str = "Too many requests") -> None:
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
        )
