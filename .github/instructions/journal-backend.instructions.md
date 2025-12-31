---
applyTo: '**'
---

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
│   ├── AGENT_INSTRUCTIONS.md    # Detailed agent instructions
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
```

### 4. Pydantic Schemas

- **Use descriptive names:** `UserCreate`, `UserResponse`, `UserUpdate`
- **Add field validation** with `Field(...)`
- **Use `ConfigDict(from_attributes=True)`** for ORM models

```python
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    username: str
    xp: int
    level: int
```

### 5. SQLAlchemy Models

- **Use `Mapped` type hints**
- **Include `UUIDMixin` and `TimestampMixin`**
- **Define relationships properly**

```python
class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
```

### 6. Commit Messages

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

### Always Do:
- Validate all user inputs with Pydantic
- Use parameterized queries (SQLAlchemy handles this)
- Rate limit auth endpoints
- Check authorization in protected endpoints
- Use HTTP-only cookies for refresh tokens

---

## 🎮 Game Mechanics Reference

### XP & Leveling

```python
# Level formula: XP = floor(level^1.5 * 100)
# Level 2: 100 XP
# Level 3: 282 XP
# Level 5: 800 XP
# Level 10: 3162 XP
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

## �� Common Operations

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

## 🧪 Testing Guidelines

```python
# tests/test_auth.py
import pytest
from httpx import AsyncClient


class TestLogin:
    @pytest.mark.asyncio
    async def test_login_valid_credentials(
        self,
        client: AsyncClient,
        test_user: User,
    ):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "testpassword123"},
        )
        assert response.status_code == 200
        assert "accessToken" in response.json()
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
8. ❌ Catching and silencing exceptions

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

## 🤖 Agent Workflow Recommendations

### When asked to implement a feature:

1. Read relevant planning docs (especially FEATURES.md, API_SPECIFICATION.md)
2. Check if related code exists (models, schemas, services)
3. Follow the layered architecture:
   - Schema (Pydantic) → Router (FastAPI) → Service (Business Logic) → Repository (Data)
4. Write tests alongside implementation
5. Commit with proper conventional commit message

### When asked to fix a bug:

1. Write a failing test that exposes the bug
2. Fix the bug
3. Verify test passes
4. Commit with `fix(scope): description`

### When asked to add an endpoint:

1. Check API_SPECIFICATION.md for the endpoint spec
2. Create/update Pydantic schema in `src/schemas/`
3. Create/update service method in `src/services/`
4. Add endpoint in `src/api/v1/`
5. Write tests in `tests/`

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
