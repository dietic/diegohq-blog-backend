"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


class TestRegister:
    """Tests for user registration."""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient) -> None:
        """Test successful user registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "securepassword123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert data["xp"] == 0
        assert data["level"] == 1

    @pytest.mark.asyncio
    async def test_register_duplicate_email(
        self, client: AsyncClient, test_user: dict[str, str]
    ) -> None:
        """Test registration with existing email fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "different",
                "email": test_user["email"],
                "password": "securepassword123",
            },
        )
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_duplicate_username(
        self, client: AsyncClient, test_user: dict[str, str]
    ) -> None:
        """Test registration with existing username fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": test_user["username"],
                "email": "different@example.com",
                "password": "securepassword123",
            },
        )
        assert response.status_code == 409
        assert "already taken" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient) -> None:
        """Test registration with invalid email fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "not-an-email",
                "password": "securepassword123",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_short_password(self, client: AsyncClient) -> None:
        """Test registration with short password fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "short",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_invalid_username(self, client: AsyncClient) -> None:
        """Test registration with invalid username fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "invalid user!",  # Contains space and special char
                "email": "newuser@example.com",
                "password": "securepassword123",
            },
        )
        assert response.status_code == 422


class TestLogin:
    """Tests for user login."""

    @pytest.mark.asyncio
    async def test_login_success(
        self, client: AsyncClient, test_user: dict[str, str]
    ) -> None:
        """Test successful login returns tokens."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "accessToken" in data
        assert "refreshToken" in data
        assert data["tokenType"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(
        self, client: AsyncClient, test_user: dict[str, str]
    ) -> None:
        """Test login with wrong password fails."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient) -> None:
        """Test login with non-existent email fails."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "somepassword",
            },
        )
        assert response.status_code == 401


class TestRefresh:
    """Tests for token refresh."""

    @pytest.mark.asyncio
    async def test_refresh_success(
        self, client: AsyncClient, test_user: dict[str, str]
    ) -> None:
        """Test successful token refresh."""
        # First login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"],
            },
        )
        refresh_token = login_response.json()["refreshToken"]

        # Refresh
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refreshToken": refresh_token},
        )
        assert response.status_code == 200
        data = response.json()
        assert "accessToken" in data
        assert "refreshToken" in data

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, client: AsyncClient) -> None:
        """Test refresh with invalid token fails."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refreshToken": "invalid-token"},
        )
        assert response.status_code == 401


class TestLogout:
    """Tests for user logout."""

    @pytest.mark.asyncio
    async def test_logout_success(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test successful logout."""
        response = await client.post(
            "/api/v1/auth/logout",
            headers=auth_headers,
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_logout_unauthenticated(self, client: AsyncClient) -> None:
        """Test logout without authentication fails."""
        response = await client.post("/api/v1/auth/logout")
        assert response.status_code == 401
