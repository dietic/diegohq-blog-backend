"""
Health check endpoints.

Provides health status for monitoring and load balancers.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """
    Check API health status.

    Returns:
        Health status response.
    """
    return {"status": "healthy"}
