"""
Pytest fixtures and configuration for tests.

Provides async database sessions and test clients.
"""

import asyncio
from collections.abc import AsyncGenerator
from typing import Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.config import settings
from src.database import get_async_session
from src.main import app
from src.models import Base

# Test database engine
test_engine = create_async_engine(
    settings.TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)

# Test session factory
test_async_session_maker = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a database session for tests.

    Creates tables before each test and drops them after.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_async_session_maker() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an async HTTP client for testing endpoints.

    Overrides the database dependency with the test session.
    """

    async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
        yield db

    app.dependency_overrides[get_async_session] = override_get_async_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db: AsyncSession) -> dict[str, str]:
    """
    Create a test user and return credentials.

    Returns:
        Dictionary with email, password, and username.
    """
    from src.core.security import hash_password
    from src.models.user import User

    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("testpassword123"),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {
        "id": str(user.id),
        "email": "test@example.com",
        "password": "testpassword123",
        "username": "testuser",
    }


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, test_user: dict[str, str]) -> dict[str, str]:
    """
    Get authentication headers for a test user.

    Returns:
        Dictionary with Authorization header.
    """
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user["email"],
            "password": test_user["password"],
        },
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['accessToken']}"}
