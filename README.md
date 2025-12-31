# DiegoHQ Blog Backend

FastAPI backend for "The Adventurer's Journal" - a gamified programming blog.

## Features

- 🔐 **Authentication**: JWT-based auth with access/refresh tokens
- 🎮 **Gamification**: XP, levels, streaks, and daily rewards
- 📜 **Quests**: Interactive coding challenges with validation
- 🎒 **Inventory**: Item system for content gating
- 📊 **Progress Tracking**: Post reads, quest completion, and XP history

## Tech Stack

- **Framework**: FastAPI 0.115+
- **Language**: Python 3.12+
- **ORM**: SQLAlchemy 2.0+ (async)
- **Database**: PostgreSQL 16+
- **Migrations**: Alembic
- **Auth**: JWT (python-jose) + Argon2 (passlib)
- **Validation**: Pydantic v2
- **Testing**: pytest + pytest-asyncio + httpx

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 16+
- Docker (optional)

### Development Setup

1. **Clone and install dependencies:**

```bash
cd diegohq-blog-backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

2. **Set up environment:**

```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. **Start PostgreSQL:**

```bash
# Using Docker
docker compose up db -d

# Or use your local PostgreSQL
```

4. **Run migrations:**

```bash
alembic upgrade head
```

5. **Start the server:**

```bash
uvicorn src.main:app --reload
```

6. **View API docs:**

Open http://localhost:8000/docs

### Using Docker

```bash
# Start all services
docker compose up

# View logs
docker compose logs -f app
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get tokens |
| POST | `/api/v1/auth/refresh` | Refresh tokens |
| POST | `/api/v1/auth/logout` | Logout (revoke tokens) |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/me` | Get current user profile |
| PATCH | `/api/v1/users/me` | Update profile |

### Game

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/game/read-post` | Mark post as read |
| POST | `/api/v1/game/daily-reward` | Claim daily reward |
| POST | `/api/v1/game/use-item` | Use inventory item |
| POST | `/api/v1/game/check-access` | Check content access |
| GET | `/api/v1/game/level-progress` | Get level progress |

### Quests

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/quests/{id}/submit` | Submit quest answer |
| GET | `/api/v1/quests/{id}/progress` | Get quest progress |
| GET | `/api/v1/quests/progress` | Get all quest progress |

## Development

### Code Quality

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

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View current revision
alembic current
```

## Project Structure

```
diegohq-blog-backend/
├── src/
│   ├── api/v1/           # API endpoints
│   ├── core/             # Security, exceptions
│   ├── models/           # SQLAlchemy models
│   ├── repositories/     # Data access layer
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── config.py         # Settings
│   ├── database.py       # DB connection
│   ├── dependencies.py   # FastAPI deps
│   └── main.py           # App entry
├── tests/                # Test files
├── alembic/              # Migrations
├── planning/             # Documentation
└── docker-compose.yml
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT signing key (min 32 chars) | Required |
| `APP_ENV` | Environment (development/production) | development |
| `DEBUG` | Enable debug mode | true |
| `CORS_ORIGINS` | Allowed CORS origins | localhost:3000 |

## License

MIT License - see LICENSE for details.
