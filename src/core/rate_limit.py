"""
Rate limiting configuration using SlowAPI.

Provides rate limiting for API endpoints.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from src.config import settings

# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    enabled=settings.RATE_LIMIT_ENABLED,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
)
