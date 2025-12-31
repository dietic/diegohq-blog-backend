# Technical Standards & Coding Guidelines - Backend

This document serves as the "source of truth" for all development on the **DiegoHQ Blog Backend**. All AI agents and developers must adhere to these standards to ensure consistency, maintainability, and security.

---

## 1. Tech Stack & Versioning

- **Framework:** FastAPI 0.115+
- **Python Version:** 3.12+
- **ORM:** SQLAlchemy 2.0+ (async)
- **Database:** PostgreSQL 16+
- **Migrations:** Alembic
- **Authentication:** JWT (PyJWT / python-jose)
- **Password Hashing:** Passlib with Argon2
- **Validation:** Pydantic v2
- **Testing:** pytest + pytest-asyncio + httpx
- **Linting:** Ruff (replaces flake8, isort, black)
- **Type Checking:** mypy (strict mode)
- **Package Manager:** uv (or pip with requirements.txt)
- **Containerization:** Docker + Docker Compose

---

## 2. Project Structure

```
diegohq-blog-backend/
├── planning/                    # Documentation (this folder)
│   ├── PROJECT_OVERVIEW.md
│   ├── FEATURES.md
│   ├── TECHNICAL_STANDARDS.md
│   ├── DATABASE_SCHEMA.md
│   ├── API_SPECIFICATION.md
│   ├── GAMIFICATION_MECHANICS.md
│   ├── MVP_ROLLOUT_PLAN.md
│   ├── AGENT_INSTRUCTIONS.md
│   └── todo.md
├── src/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Settings and environment config
│   ├── database.py              # Database connection and session
│   ├── dependencies.py          # FastAPI dependencies (auth, db)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py        # Main v1 router
│   │   │   ├── auth.py          # Auth endpoints
│   │   │   ├── users.py         # User endpoints
│   │   │   ├── game.py          # Game mechanics endpoints
│   │   │   ├── quests.py        # Quest endpoints
│   │   │   ├── items.py         # Item endpoints
│   │   │   └── admin.py         # Admin endpoints
│   ├── models/                  # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py              # Base model class
│   │   ├── user.py
│   │   ├── inventory.py
│   │   ├── quest_progress.py
│   │   ├── post_progress.py
│   │   └── daily_reward.py
│   ├── schemas/                 # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── game.py
│   │   ├── quest.py
│   │   ├── item.py
│   │   └── common.py
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── game_service.py
│   │   ├── quest_service.py
│   │   └── item_service.py
│   ├── repositories/            # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user_repository.py
│   │   ├── inventory_repository.py
│   │   └── progress_repository.py
│   ├── core/                    # Core utilities
│   │   ├── __init__.py
│   │   ├── security.py          # JWT, password hashing
│   │   ├── exceptions.py        # Custom exceptions
│   │   └── constants.py         # App constants
│   └── utils/                   # Helper utilities
│       ├── __init__.py
│       └── level_calculator.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_game.py
│   └── test_quests.py
├── alembic/                     # Database migrations
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
├── scripts/                     # Utility scripts
│   ├── seed_db.py               # Seed initial data
│   └── sync_content.py          # Sync with frontend CMS
├── .env.example                 # Environment variables template
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml               # Project config (ruff, mypy, pytest)
├── requirements.txt             # Dependencies
└── README.md
```

---

## 3. Code Style & Conventions

### 3.1. Python Style

- **Line Length:** 88 characters (Black/Ruff default)
- **Quotes:** Double quotes for strings
- **Imports:** Sorted by isort rules (stdlib, third-party, local)
- **Docstrings:** Google style for public functions/classes

```python
# ✅ GOOD
async def get_user_by_id(user_id: UUID) -> User | None:
    """
    Retrieve a user by their unique identifier.

    Args:
        user_id: The UUID of the user to retrieve.

    Returns:
        The User object if found, None otherwise.
    """
    ...

# ❌ BAD
def get_user(id):  # No type hints, unclear naming
    ...
```

### 3.2. Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Variables | snake_case | `user_level` |
| Functions | snake_case | `calculate_xp_for_level()` |
| Classes | PascalCase | `UserService` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_LEVEL` |
| Private | Leading underscore | `_internal_method()` |
| Modules | snake_case | `user_service.py` |
| Schemas | PascalCase + suffix | `UserCreateSchema`, `UserResponse` |

### 3.3. Type Hints

- **Required:** All function parameters and return types must have type hints
- **Use `|` syntax:** `str | None` instead of `Optional[str]`
- **Use `list`/`dict`:** Lowercase generics (Python 3.9+) - `list[str]` not `List[str]`

```python
# ✅ GOOD
async def award_xp(user_id: UUID, amount: int) -> tuple[int, bool]:
    """Returns (new_xp_total, did_level_up)"""
    ...

# ❌ BAD
async def award_xp(user_id, amount):  # Missing type hints
    ...
```

### 3.4. Async/Await

- **Always use async** for I/O operations (database, HTTP, file)
- **Use `async def`** for all endpoint handlers
- **Use `await`** for all async calls

```python
# ✅ GOOD
async def get_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User))
    return result.scalars().all()

# ❌ BAD - Blocking call in async context
def get_users(db: Session) -> list[User]:
    return db.query(User).all()
```

---

## 4. FastAPI Patterns

### 4.1. Router Structure

```python
# src/api/v1/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_current_user
from src.schemas.user import UserResponse, UserUpdate
from src.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get the current authenticated user's profile."""
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_current_user_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Update the current user's profile."""
    user_service = UserService(db)
    updated_user = await user_service.update_user(current_user.id, update_data)
    return UserResponse.model_validate(updated_user)
```

### 4.2. Dependency Injection

```python
# src/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import decode_access_token
from src.database import get_db
from src.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency to get the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = await db.get(User, user_id)
    if user is None:
        raise credentials_exception
    
    return user


async def get_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency to ensure user has admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
```

### 4.3. Error Handling

```python
# src/core/exceptions.py
from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base exception for application errors."""
    pass


class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(AppException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class BadRequestException(AppException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ConflictException(AppException):
    def __init__(self, detail: str = "Conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
```

---

## 5. Pydantic Schemas

### 5.1. Schema Patterns

```python
# src/schemas/user.py
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base user fields shared across schemas."""
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    """Schema for user profile updates."""
    username: str | None = Field(None, min_length=3, max_length=30)
    avatar_url: str | None = None


class UserResponse(UserBase):
    """Schema for user response (public profile)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    avatar_url: str | None
    xp: int
    level: int
    xp_to_next_level: int
    xp_progress: float
    created_at: datetime


class UserWithGameState(UserResponse):
    """Extended user response with full game state."""
    inventory: list[str]
    completed_quests: list[str]
    read_posts: list[str]
    unlocked_posts: list[str]
    stats: "UserStats"


class UserStats(BaseModel):
    """User statistics."""
    total_xp_earned: int
    quests_completed: int
    posts_read: int
    current_streak: int
    longest_streak: int
```

### 5.2. Request/Response Naming

| Type | Naming Pattern | Example |
|------|----------------|---------|
| Create input | `{Entity}Create` | `UserCreate` |
| Update input | `{Entity}Update` | `UserUpdate` |
| Response | `{Entity}Response` | `UserResponse` |
| List response | `{Entity}ListResponse` | `UserListResponse` |
| Internal | `{Entity}InDB` | `UserInDB` |

---

## 6. SQLAlchemy Models

### 6.1. Model Patterns

```python
# src/models/base.py
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class UUIDMixin:
    """Mixin for UUID primary key."""
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
```

```python
# src/models/user.py
from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    """User model for authentication and game state."""
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Game state
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    current_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    inventory_items: Mapped[list["InventoryItem"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    quest_progress: Mapped[list["QuestProgress"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    post_progress: Mapped[list["PostProgress"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
```

---

## 7. Service Layer Pattern

```python
# src/services/game_service.py
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import BadRequestException, NotFoundException
from src.models.user import User
from src.models.post_progress import PostProgress
from src.repositories.user_repository import UserRepository
from src.repositories.progress_repository import ProgressRepository
from src.utils.level_calculator import calculate_xp_for_level, calculate_level_from_xp


class GameService:
    """Service for game mechanics and progression."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.progress_repo = ProgressRepository(db)

    async def award_read_xp(
        self,
        user_id: UUID,
        post_slug: str,
        xp_amount: int,
    ) -> tuple[int, int, bool]:
        """
        Award XP for reading a post.

        Args:
            user_id: The user's ID
            post_slug: The slug of the post read
            xp_amount: Amount of XP to award

        Returns:
            Tuple of (new_total_xp, new_level, did_level_up)
        """
        # Check if user already read this post
        existing = await self.progress_repo.get_post_progress(user_id, post_slug)
        if existing and existing.has_read:
            raise BadRequestException("XP already awarded for this post")

        # Get user
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        # Award XP
        old_level = user.level
        new_xp = user.xp + xp_amount
        new_level = calculate_level_from_xp(new_xp)
        did_level_up = new_level > old_level

        # Update user
        await self.user_repo.update(user_id, xp=new_xp, level=new_level)

        # Mark post as read
        await self.progress_repo.mark_post_read(user_id, post_slug)

        await self.db.commit()

        return new_xp, new_level, did_level_up
```

---

## 8. Testing Standards

### 8.1. Test Structure

```python
# tests/test_game.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from tests.factories import UserFactory


class TestReadPost:
    """Tests for the read-post endpoint."""

    @pytest.mark.asyncio
    async def test_read_post_awards_xp(
        self,
        client: AsyncClient,
        db: AsyncSession,
        auth_headers: dict,
    ):
        """Reading a post for the first time should award XP."""
        response = await client.post(
            "/api/v1/game/read-post",
            json={"postSlug": "intro-to-git", "readXp": 10},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["xpAwarded"] == 10
        assert data["newTotalXp"] >= 10

    @pytest.mark.asyncio
    async def test_read_post_twice_no_double_xp(
        self,
        client: AsyncClient,
        db: AsyncSession,
        auth_headers: dict,
    ):
        """Reading the same post twice should not award XP twice."""
        # First read
        await client.post(
            "/api/v1/game/read-post",
            json={"postSlug": "intro-to-git", "readXp": 10},
            headers=auth_headers,
        )

        # Second read
        response = await client.post(
            "/api/v1/game/read-post",
            json={"postSlug": "intro-to-git", "readXp": 10},
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "already awarded" in response.json()["detail"].lower()
```

### 8.2. Fixtures

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.config import settings
from src.database import get_db
from src.main import app
from src.models.base import Base


@pytest.fixture
async def db():
    """Create a test database session."""
    engine = create_async_engine(settings.TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine) as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db: AsyncSession):
    """Create a test client with database dependency override."""
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()
```

---

## 9. Security Standards

### 9.1. Password Hashing

```python
# src/core/security.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)
```

### 9.2. JWT Handling

```python
# src/core/security.py
from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, jwt

from src.config import settings

ALGORITHM = "HS256"


def create_access_token(user_id: UUID, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {"sub": str(user_id), "exp": expire, "type": "access"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: UUID) -> str:
    """Create a JWT refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": str(user_id), "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Decode and validate an access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None
```

### 9.3. Rate Limiting

```python
# src/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Usage in endpoints
@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, ...):
    ...
```

---

## 10. Commit Standards (Conventional Commits)

### 10.1. Structure

```
<type>(<scope>): <short description>

[optional body explaining "why" - not "what"]
```

### 10.2. Types

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Formatting (no code change)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding or correcting tests
- `chore`: Build process, dependencies, auxiliary tools

### 10.3. Examples

- `feat(auth): add refresh token rotation`
- `fix(game): prevent double XP award for same post`
- `chore(deps): upgrade fastapi to 0.115`

---

## 11. Environment Variables

```bash
# .env.example

# Application
APP_NAME=diegohq-blog-backend
APP_ENV=development
DEBUG=true
SECRET_KEY=your-super-secret-key-change-in-production

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/diegohq_blog
TEST_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/diegohq_blog_test

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Rate Limiting
RATE_LIMIT_ENABLED=true

# Admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=change-this-password
```

---

## 12. Logging Standards

```python
# src/core/logging.py
import logging
import sys

from src.config import settings


def setup_logging() -> None:
    """Configure application logging."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
```

Usage:

```python
import logging

logger = logging.getLogger(__name__)

async def award_xp(...):
    logger.info(f"Awarding {amount} XP to user {user_id}")
    # ...
    logger.debug(f"User {user_id} new level: {new_level}")
```

---

## 13. API Response Standards

### 13.1. Success Responses

```json
// Single resource
{
  "id": "uuid",
  "username": "Adventurer42",
  "xp": 350
}

// List of resources
{
  "items": [...],
  "total": 100,
  "page": 1,
  "pageSize": 20,
  "totalPages": 5
}

// Action result
{
  "success": true,
  "xpAwarded": 50,
  "newTotalXp": 400,
  "leveledUp": true,
  "newLevel": 4
}
```

### 13.2. Error Responses

```json
{
  "detail": "User not found",
  "code": "USER_NOT_FOUND"
}

// Validation errors
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Invalid email format",
      "type": "value_error"
    }
  ]
}
```
