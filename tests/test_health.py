"""Tests for health endpoint."""

import pytest
from httpx import AsyncClient


class TestHealth:
    """Tests for health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient) -> None:
        """Test health endpoint returns healthy status."""
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
