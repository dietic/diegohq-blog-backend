"""Tests for game mechanics endpoints."""

import pytest
from httpx import AsyncClient


class TestReadPost:
    """Tests for marking posts as read."""

    @pytest.mark.asyncio
    async def test_read_post_first_time(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test reading a post for the first time awards XP."""
        response = await client.post(
            "/api/v1/game/read-post",
            headers=auth_headers,
            json={"postSlug": "test-post-1"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["alreadyRead"] is False
        assert data["xpAwarded"] > 0
        assert data["newXp"] == data["xpAwarded"]

    @pytest.mark.asyncio
    async def test_read_post_already_read(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test reading a post again doesn't award XP."""
        # Read first time
        await client.post(
            "/api/v1/game/read-post",
            headers=auth_headers,
            json={"postSlug": "test-post-2"},
        )

        # Read again
        response = await client.post(
            "/api/v1/game/read-post",
            headers=auth_headers,
            json={"postSlug": "test-post-2"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["alreadyRead"] is True
        assert data["xpAwarded"] == 0


class TestDailyReward:
    """Tests for daily reward claiming."""

    @pytest.mark.asyncio
    async def test_claim_daily_reward(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test claiming daily reward."""
        response = await client.post(
            "/api/v1/game/daily-reward",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["alreadyClaimed"] is False
        assert data["xpAwarded"] > 0
        assert data["streakDay"] == 1

    @pytest.mark.asyncio
    async def test_claim_daily_reward_already_claimed(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test claiming daily reward twice fails."""
        # Claim first time
        await client.post(
            "/api/v1/game/daily-reward",
            headers=auth_headers,
        )

        # Try to claim again
        response = await client.post(
            "/api/v1/game/daily-reward",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["alreadyClaimed"] is True
        assert data["xpAwarded"] == 0


class TestCheckAccess:
    """Tests for content access checking."""

    @pytest.mark.asyncio
    async def test_check_access_no_requirements(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test access check with no requirements."""
        response = await client.post(
            "/api/v1/game/check-access",
            headers=auth_headers,
            json={"postSlug": "open-post"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["hasAccess"] is True

    @pytest.mark.asyncio
    async def test_check_access_level_gated(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test access check for level-gated content."""
        response = await client.post(
            "/api/v1/game/check-access",
            headers=auth_headers,
            json={
                "postSlug": "advanced-post",
                "requiredLevel": 10,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["hasAccess"] is False
        assert data["requiredLevel"] == 10


class TestLevelProgress:
    """Tests for level progress endpoint."""

    @pytest.mark.asyncio
    async def test_get_level_progress(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test getting level progress."""
        response = await client.get(
            "/api/v1/game/level-progress",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["currentLevel"] == 1
        assert data["currentXp"] == 0
        assert "xpForNextLevel" in data
        assert "progressPercentage" in data
