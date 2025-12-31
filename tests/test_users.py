"""Tests for user endpoints."""

import pytest
from httpx import AsyncClient


class TestGetCurrentUser:
    """Tests for getting current user profile."""

    @pytest.mark.asyncio
    async def test_get_me_success(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        test_user: dict[str, str],
    ) -> None:
        """Test getting current user profile."""
        response = await client.get(
            "/api/v1/users/me",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user["email"]
        assert data["username"] == test_user["username"]
        assert data["xp"] == 0
        assert data["level"] == 1

    @pytest.mark.asyncio
    async def test_get_me_unauthenticated(self, client: AsyncClient) -> None:
        """Test getting profile without auth fails."""
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 401


class TestUpdateCurrentUser:
    """Tests for updating current user profile."""

    @pytest.mark.asyncio
    async def test_update_username(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test updating username."""
        response = await client.patch(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"username": "newusername"},
        )
        assert response.status_code == 200
        assert response.json()["username"] == "newusername"

    @pytest.mark.asyncio
    async def test_update_avatar(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test updating avatar URL."""
        response = await client.patch(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"avatar_url": "https://example.com/avatar.png"},
        )
        assert response.status_code == 200
        assert response.json()["avatar_url"] == "https://example.com/avatar.png"

    @pytest.mark.asyncio
    async def test_update_invalid_username(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test updating with invalid username fails."""
        response = await client.patch(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"username": "ab"},  # Too short
        )
        assert response.status_code == 422
