# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI backend for "The Adventurer's Journal" - a gamified programming blog with user authentication, XP tracking, leveling, quests, and inventory management.

**Stack:** Python 3.12+, FastAPI 0.115+, SQLAlchemy 2.0+ (async), PostgreSQL 16+, Pydantic v2, pytest

## Common Commands

```bash
# Development server
uvicorn src.main:app --reload --port 8000

# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=src --cov-report=html

# Linting (Ruff)
ruff check src tests
ruff check src tests --fix
ruff format src tests

# Type checking (strict mypy)
mypy src

# Database migrations
alembic upgrade head
alembic revision --autogenerate -m "Description"
alembic downgrade -1
```

## Architecture

Layered architecture with strict separation of concerns:

```
Request → Router (API endpoint) → Pydantic Schema (validation)
  → Service (business logic) → Repository (data access) → SQLAlchemy Model
```

- **`src/api/v1/`** - FastAPI routers organized by feature (auth, users, game, quests, content, contact)
- **`src/schemas/`** - Pydantic models for request/response validation
- **`src/services/`** - Business logic layer
- **`src/repositories/`** - Data access layer with generic `BaseRepository[T]`
- **`src/models/`** - SQLAlchemy ORM models with `UUIDMixin` and `TimestampMixin`
- **`src/core/`** - Security (JWT, password hashing), exceptions, rate limiting

## Code Standards

**Type Hints:** Required on ALL function parameters and returns. Use Python 3.12+ syntax:
- `str | None` (not `Optional[str]`)
- `list[str]` (not `List[str]`)
- No `Any` unless absolutely necessary

**Async:** All I/O operations must be async. All endpoint handlers are async.

**Error Handling:** Use custom exceptions from `src/core/exceptions.py`:
- `NotFoundException`, `BadRequestException`, `UnauthorizedException`, `ForbiddenException`, `ConflictException`, `ValidationException`, `TooManyRequestsException`

**Pydantic Schemas:** Follow naming convention `NameCreate`, `NameResponse`, `NameUpdate`. Use `ConfigDict(from_attributes=True)` for ORM compatibility.

**SQLAlchemy Models:** Use `Mapped` type hints. Inherit from `Base` and appropriate mixins (`UUIDMixin`, `TimestampMixin`). Use timezone-aware UTC datetime.

**Commit Messages:** Conventional Commits format - `feat(scope):`, `fix(scope):`, `refactor(scope):`, `test(scope):`, `docs:`

## Key Documentation

Detailed specifications are in `planning/`:
- `TECHNICAL_STANDARDS.md` - Comprehensive coding rules
- `API_SPECIFICATION.md` - Endpoint specifications
- `DATABASE_SCHEMA.md` - Database design
- `GAMIFICATION_MECHANICS.md` - XP, levels, quests logic

Agent instructions: `.github/instructions/journal-backend.instructions.md`
