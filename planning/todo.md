# Backend TODO List

This document tracks the current tasks for "The Adventurer's Journal" backend.

---

## Current Phase: Phase 1 - Core API Foundation

---

## 🚀 Project Setup

### Configuration
- [ ] Create `pyproject.toml` with dependencies
  - FastAPI, SQLAlchemy, Alembic, Pydantic
  - python-jose, passlib[argon2]
  - pytest, pytest-asyncio, httpx
  - ruff, mypy
- [ ] Create `requirements.txt` from pyproject.toml
- [ ] Create `.env.example` with all required variables
- [ ] Create `src/config.py` with Pydantic BaseSettings

### Docker
- [ ] Create `Dockerfile` (multi-stage build)
- [ ] Create `docker-compose.yml` (app + postgres + redis optional)
- [ ] Create `.dockerignore`

### Tooling
- [ ] Configure Ruff in `pyproject.toml`
- [ ] Configure mypy in `pyproject.toml`
- [ ] Configure pytest in `pyproject.toml`
- [ ] Create `Makefile` with common commands

---

## 🗄️ Database Setup

### SQLAlchemy
- [ ] Create `src/database.py` with async engine and session
- [ ] Create `src/models/base.py` with Base, UUIDMixin, TimestampMixin
- [ ] Create `src/models/__init__.py` to export all models

### Models
- [ ] Create `src/models/user.py` - User model
- [ ] Create `src/models/refresh_token.py` - RefreshToken model

### Alembic
- [ ] Initialize Alembic: `alembic init alembic`
- [ ] Configure `alembic/env.py` for async
- [ ] Create initial migration: `alembic revision --autogenerate -m "Initial schema"`
- [ ] Test migration: `alembic upgrade head`

### Seeding
- [ ] Create `scripts/seed_db.py` for development data

---

## 🔐 Authentication

### Security Utilities
- [ ] Create `src/core/security.py`
  - [ ] Password hashing (Argon2)
  - [ ] Password verification
  - [ ] Access token creation
  - [ ] Refresh token creation
  - [ ] Token decoding/validation

### Schemas
- [ ] Create `src/schemas/auth.py`
  - [ ] `RegisterRequest` - username, email, password
  - [ ] `LoginRequest` - email, password
  - [ ] `TokenResponse` - accessToken, tokenType, expiresIn
  - [ ] `RefreshRequest` - (empty, uses cookie)

### Endpoints
- [ ] Create `src/api/v1/auth.py` router
- [ ] `POST /auth/register` - Create new account
- [ ] `POST /auth/login` - Authenticate and get tokens
- [ ] `POST /auth/refresh` - Get new access token
- [ ] `POST /auth/logout` - Invalidate refresh token

### Dependencies
- [ ] Create `src/dependencies.py`
  - [ ] `get_db` - Database session dependency
  - [ ] `get_current_user` - Auth dependency

### Services
- [ ] Create `src/services/auth_service.py`
  - [ ] `register_user()` - Create user, hash password
  - [ ] `authenticate_user()` - Verify credentials
  - [ ] `create_tokens()` - Generate access + refresh tokens
  - [ ] `refresh_tokens()` - Rotate refresh token
  - [ ] `logout()` - Revoke refresh token

### Repository
- [ ] Create `src/repositories/user_repository.py`
  - [ ] `get_by_id()` - Get user by UUID
  - [ ] `get_by_email()` - Get user by email
  - [ ] `get_by_username()` - Get user by username
  - [ ] `create()` - Create new user
  - [ ] `update()` - Update user fields
- [ ] Create `src/repositories/token_repository.py`
  - [ ] `create_refresh_token()` - Store hashed token
  - [ ] `get_by_token_hash()` - Find token
  - [ ] `revoke()` - Mark token as revoked

### Tests
- [ ] Create `tests/test_auth.py`
  - [ ] Test registration with valid data
  - [ ] Test registration with duplicate email
  - [ ] Test registration with duplicate username
  - [ ] Test login with valid credentials
  - [ ] Test login with wrong password
  - [ ] Test login with non-existent email
  - [ ] Test token refresh
  - [ ] Test logout

---

## 👤 User Profile

### Schemas
- [ ] Create `src/schemas/user.py`
  - [ ] `UserResponse` - Public user data + game state
  - [ ] `UserUpdate` - Updateable fields (username, avatar)
  - [ ] `UserWithGameState` - Full profile with inventory, quests

### Endpoints
- [ ] Create `src/api/v1/users.py` router
- [ ] `GET /users/me` - Get current user profile
- [ ] `PATCH /users/me` - Update profile

### Services
- [ ] Create `src/services/user_service.py`
  - [ ] `get_user_with_game_state()` - Get full profile
  - [ ] `update_user()` - Update profile fields

### Tests
- [ ] Create `tests/test_users.py`
  - [ ] Test get profile (authenticated)
  - [ ] Test get profile (unauthenticated)
  - [ ] Test update username
  - [ ] Test update with duplicate username

---

## 🏥 Health & Utilities

### Endpoints
- [ ] `GET /health` - Health check
- [ ] `GET /version` - API version info

### App Setup
- [ ] Create `src/main.py` with FastAPI app
- [ ] Configure CORS middleware
- [ ] Add exception handlers
- [ ] Mount v1 router at `/api/v1`
- [ ] Add OpenAPI configuration

---

## 📝 Documentation

- [ ] Create `README.md` with setup instructions
- [ ] Document environment variables
- [ ] Document API endpoints (auto-generated from OpenAPI)
- [ ] Create development setup guide

---

## 🔜 Next Phase Preview (Phase 2)

After Phase 1 is complete:

- [ ] XP & leveling system
- [ ] Post progress tracking
- [ ] Level-up detection
- [ ] `/game/read-post` endpoint
- [ ] `/game/check-access` endpoint

---

## Notes

- Priority order: Setup → Database → Auth → Users → Health
- Run `ruff check src tests` and `mypy src` frequently
- Write tests as you implement features
- Commit after each completed section

---

## Recently Completed

_(Move items here when done)_

---

## Blocked

_(Items waiting on something)_
