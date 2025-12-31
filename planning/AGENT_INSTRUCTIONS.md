# AI Agent Instructions: DiegoHQ Blog Backend

This document provides comprehensive instructions for AI coding agents (GitHub Copilot, Claude, etc.) working on "The Adventurer's Journal" backend. Read this document in full before making any changes.

---

## 🎯 Project Summary

**What is this project?**
A FastAPI backend that powers the gamification mechanics of a retro-styled programming blog. It handles user authentication, XP tracking, leveling, quest validation, inventory management, and content gating.

**Current Phase:** Phase 1 (MVP) - Core API Foundation

**Tech Stack:**

- **Framework:** FastAPI 0.115+
- **Language:** Python 3.12+
- **ORM:** SQLAlchemy 2.0+ (async)
- **Database:** PostgreSQL 16+
- **Migrations:** Alembic
- **Auth:** JWT (python-jose) + Argon2 (passlib)
- **Validation:** Pydantic v2
- **Testing:** pytest + pytest-asyncio + httpx
- **Linting:** Ruff
- **Type Checking:** mypy (strict mode)
- **Package Manager:** uv (or pip)

---

## 📁 Project Structure

```
diegohq-blog-backend/
├── planning/                    # 📖 READ THESE FIRST
│   ├── PROJECT_OVERVIEW.md      # Vision and architecture
│   ├── FEATURES.md              # Full feature/endpoint list
│   ├── TECHNICAL_STANDARDS.md   # Coding guidelines (MUST FOLLOW)
│   ├── DATABASE_SCHEMA.md       # Database design
│   ├── API_SPECIFICATION.md     # Detailed endpoint specs
│   ├── GAMIFICATION_MECHANICS.md # XP, levels, quests logic
│   ├── MVP_ROLLOUT_PLAN.md      # Phased development approach
│   ├── AGENT_INSTRUCTIONS.md    # THIS FILE
│   └── todo.md                  # Current task list
├── src/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Settings (Pydantic BaseSettings)
│   ├── database.py              # Database connection
│   ├── dependencies.py          # FastAPI dependencies
│   ├── api/v1/                  # API endpoints
│   │   ├── router.py            # Main v1 router
│   │   ├── auth.py              # Auth endpoints
│   │   ├── users.py             # User endpoints
│   │   ├── game.py              # Game mechanics
│   │   ├── quests.py            # Quest endpoints
│   │   └── admin.py             # Admin endpoints
│   ├── models/                  # SQLAlchemy models
│   ├── schemas/                 # Pydantic schemas
│   ├── services/                # Business logic
│   ├── repositories/            # Data access layer
│   ├── core/                    # Security, exceptions
│   └── utils/                   # Helpers
├── tests/                       # Test files
├── alembic/                     # Database migrations
├── scripts/                     # Utility scripts
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── requirements.txt
```

---

## ⚠️ CRITICAL RULES (Always Follow)

### 1. Code Style

- **Type hints required** on ALL function parameters and return types
- **Use `|` union syntax:** `str | None` not `Optional[str]`
- **Use lowercase generics:** `list[str]` not `List[str]`
- **No `Any` type** unless absolutely necessary
- **Docstrings** on all public functions (Google style)

```python
# ✅ CORRECT
async def get_user_by_id(user_id: UUID) -> User | None:
    """
    Retrieve a user by their unique identifier.

    Args:
        user_id: The UUID of the user to retrieve.

    Returns:
        The User object if found, None otherwise.
    """
    ...

# ❌ WRONG
def get_user(id):  # No type hints
    ...
```

### 2. Async/Await

- **All I/O operations must be async** (database, HTTP, file)
- **All endpoint handlers must be async**
- **Use `await`** for all async calls

```python
# ✅ CORRECT
async def get_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User))
    return result.scalars().all()

# ❌ WRONG - Synchronous in async context
def get_users(db: Session) -> list[User]:
    return db.query(User).all()
```

### 3. Error Handling

- **Use custom exceptions** from `src/core/exceptions.py`
- **Never expose raw errors** to API responses
- **Log errors with context**

```python
# ✅ CORRECT
from src.core.exceptions import NotFoundException, BadRequestException

async def get_user(user_id: UUID) -> User:
    user = await db.get(User, user_id)
    if not user:
        raise NotFoundException(f"User {user_id} not found")
    return user

# ❌ WRONG - Generic exception
raise Exception("User not found")
```

### 4. Pydantic Schemas

- **Use descriptive names:** `UserCreate`, `UserResponse`, `UserUpdate`
- **Add field validation** with `Field(...)`
- **Use `ConfigDict(from_attributes=True)`** for ORM models

```python
# ✅ CORRECT
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    username: str
    email: str
    xp: int
    level: int
```

### 5. SQLAlchemy Models

- **Use `Mapped` type hints**
- **Include `UUIDMixin` and `TimestampMixin`**
- **Define relationships properly**

```python
# ✅ CORRECT
class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
```

### 6. Dependency Injection

- **Use FastAPI's `Depends`** for all dependencies
- **Create reusable dependencies** in `dependencies.py`

```python
# ✅ CORRECT
@router.get("/me")
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)
```

### 7. Commit Messages

Use **Conventional Commits**:

```
feat(auth): add refresh token rotation
fix(game): prevent double XP award
refactor(users): extract service layer
test(quests): add submission tests
chore(deps): upgrade fastapi to 0.115
docs: update API documentation
```

---

## 🔒 Security Rules

### Never Do:
- Store raw passwords (always hash with Argon2)
- Store raw refresh tokens (hash them)
- Return password hashes in API responses
- Log sensitive data (passwords, tokens)
- Trust client-provided XP values without validation
- Use string formatting for SQL queries

### Always Do:
- Validate all user inputs with Pydantic
- Use parameterized queries (SQLAlchemy handles this)
- Rate limit auth endpoints
- Check authorization in protected endpoints
- Use HTTP-only cookies for refresh tokens

---

## 📋 Current Tasks (Phase 1)

Reference `planning/todo.md` for the full list. Key priorities:

### 1. Project Setup
- [ ] Create `pyproject.toml` with all dependencies
- [ ] Configure Ruff (linting/formatting)
- [ ] Configure mypy (type checking)
- [ ] Create `.env.example` with all variables
- [ ] Create `Dockerfile` and `docker-compose.yml`

### 2. Database
- [ ] Create `src/database.py` with async engine
- [ ] Create base models (`UUIDMixin`, `TimestampMixin`)
- [ ] Create `User` model
- [ ] Set up Alembic and initial migration

### 3. Authentication
- [ ] Create `src/core/security.py` (password hashing, JWT)
- [ ] Create auth schemas (`LoginRequest`, `TokenResponse`)
- [ ] Create `POST /auth/register` endpoint
- [ ] Create `POST /auth/login` endpoint
- [ ] Create auth dependencies (`get_current_user`)

### 4. Users
- [ ] Create user schemas (`UserResponse`, `UserUpdate`)
- [ ] Create `GET /users/me` endpoint
- [ ] Create `PATCH /users/me` endpoint

---

## 🧪 Testing Guidelines

### Test File Structure

```
tests/
├── conftest.py              # Fixtures
├── test_auth.py             # Auth endpoint tests
├── test_users.py            # User endpoint tests
├── test_game.py             # Game mechanics tests
└── factories.py             # Test data factories
```

### Test Patterns

```python
# tests/test_auth.py
import pytest
from httpx import AsyncClient


class TestLogin:
    """Tests for POST /auth/login."""

    @pytest.mark.asyncio
    async def test_login_valid_credentials(
        self,
        client: AsyncClient,
        test_user: User,
    ):
        """Users can login with valid credentials."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "testpassword123",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "accessToken" in data
        assert data["tokenType"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(
        self,
        client: AsyncClient,
        test_user: User,
    ):
        """Login fails with wrong password."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword",
            },
        )
        
        assert response.status_code == 401
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

---

## 🔧 Common Operations

### Running the Project

```bash
# Development with auto-reload
uvicorn src.main:app --reload --port 8000

# With Docker
docker-compose up

# Production
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Add users table"

# Apply migrations
alembic upgrade head

# Rollback one
alembic downgrade -1

# View history
alembic history
```

### Linting & Formatting

```bash
# Format code
ruff format src tests

# Lint code
ruff check src tests

# Fix auto-fixable issues
ruff check src tests --fix

# Type check
mypy src
```

---

## 🎮 Game Mechanics Reference

### XP & Leveling

```python
# Level formula: XP = floor(level^1.5 * 100)
# Level 2: 100 XP
# Level 3: 282 XP
# Level 5: 800 XP
# Level 10: 3162 XP

from src.utils.level_calculator import (
    calculate_xp_for_level,
    calculate_level_from_xp,
)
```

### XP Sources

| Action | XP Range | Notes |
|--------|----------|-------|
| Read post | 10-20 | Once per post |
| Complete quest | 30-100 | Once per quest |
| Daily login | 5-25 | Once per day, streak bonus |

### Content Gating Types

1. **Level-gated:** User must reach required level
2. **Item-gated:** User must have and use specific item

---

## 📚 API Endpoint Patterns

### Standard Response Format

```python
# Success (single resource)
{
    "id": "uuid",
    "field": "value"
}

# Success (list)
{
    "items": [...],
    "total": 100,
    "page": 1,
    "pageSize": 20
}

# Error
{
    "detail": "Human-readable message",
    "code": "ERROR_CODE"
}
```

### Endpoint Implementation Pattern

```python
# src/api/v1/users.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_current_user
from src.models.user import User
from src.schemas.user import UserResponse, UserUpdate
from src.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """
    Get the current authenticated user's profile.
    
    Returns the user's profile including game state (XP, level, inventory).
    """
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_current_user_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Update the current user's profile.
    
    Allows updating username and avatar.
    """
    user_service = UserService(db)
    updated_user = await user_service.update_user(current_user.id, update_data)
    return UserResponse.model_validate(updated_user)
```

---

## 🚨 Common Pitfalls to Avoid

1. ❌ Using sync database operations in async functions
2. ❌ Forgetting to `await` async calls
3. ❌ Missing type hints on functions
4. ❌ Using `Any` type unnecessarily
5. ❌ Hardcoding configuration (use env vars)
6. ❌ Returning password hashes in responses
7. ❌ Not validating input with Pydantic
8. ❌ Creating SQL queries with string formatting
9. ❌ Catching and silencing exceptions
10. ❌ Not including error handling in endpoints

---

## 🤖 Agent Workflow Recommendations

### When asked to implement a feature:

1. Read relevant planning docs (especially FEATURES.md, API_SPECIFICATION.md)
2. Check if related code exists (models, schemas, services)
3. Follow the layered architecture:
   - Schema (Pydantic) → Router (FastAPI) → Service (Business Logic) → Repository (Data)
4. Write tests alongside implementation
5. Commit with proper conventional commit message

### When asked to fix a bug:

1. Reproduce the issue (understand expected vs actual)
2. Write a failing test that exposes the bug
3. Fix the bug
4. Verify test passes
5. Commit with `fix(scope): description`

### When asked to add an endpoint:

1. Check API_SPECIFICATION.md for the endpoint spec
2. Create/update Pydantic schema in `src/schemas/`
3. Create/update service method in `src/services/`
4. Add endpoint in `src/api/v1/`
5. Add to router in `src/api/v1/router.py`
6. Write tests in `tests/`
7. Update OpenAPI docs if needed

---

## 📝 Before You Code

1. **Read relevant planning docs** for the feature
2. **Check existing code** for patterns to follow
3. **Run tests** to ensure baseline works
4. **Run linter** to ensure code style is correct

```bash
# Before starting work
pytest                  # Verify tests pass
ruff check src tests    # Verify no lint errors
mypy src               # Verify types

# After making changes
ruff format src tests   # Format code
ruff check src tests    # Check for issues
mypy src               # Type check
pytest                  # Run tests
```

---

## ✅ Definition of Done

A task is complete when:

- [ ] Code follows all TECHNICAL_STANDARDS.md rules
- [ ] All functions have type hints and docstrings
- [ ] Tests are written and passing
- [ ] No Ruff errors or warnings
- [ ] No mypy errors
- [ ] API endpoint matches API_SPECIFICATION.md
- [ ] Committed with proper conventional commit message

---

## 📚 Quick Reference Links

| Document | Purpose |
|----------|---------|
| `PROJECT_OVERVIEW.md` | Architecture and design |
| `FEATURES.md` | Complete endpoint list |
| `TECHNICAL_STANDARDS.md` | **MUST READ** - Coding rules |
| `DATABASE_SCHEMA.md` | Database design |
| `API_SPECIFICATION.md` | Detailed endpoint specs |
| `GAMIFICATION_MECHANICS.md` | XP, levels, quests logic |
| `MVP_ROLLOUT_PLAN.md` | Development phases |
| `todo.md` | Current task list |

---

## 🔗 Frontend Integration Notes

The backend serves the frontend at `https://diegohq.dev` (production) or `http://localhost:3000` (development).

### CORS Configuration

```python
# src/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Cookie Settings

```python
# For refresh tokens
response.set_cookie(
    key="refresh_token",
    value=token,
    httponly=True,
    secure=True,  # HTTPS only in production
    samesite="strict",
    path="/api/v1/auth",
    max_age=60 * 60 * 24 * 7,  # 7 days
)
```

### Content Sync

The frontend CMS defines quests and items in JSON files. The backend can sync these via:

1. Manual script: `python scripts/sync_content.py`
2. Admin endpoint: `POST /admin/sync-quests`

This ensures the backend has quest/item definitions for validation.
