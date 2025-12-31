# Project Overview: The Adventurer's Journal - Backend

## Mission

To provide a robust, scalable, and secure backend service that powers the gamification mechanics of "The Adventurer's Journal" blog. This backend handles user authentication, game state management, and all XP/level/quest/item tracking logic.

## Core Concept

The backend is a RESTful API built with Python and FastAPI. It serves as the "game server" for the blog, managing persistent user progress, validating quest completions, and enforcing content gating rules. The frontend consumes this API to provide a seamless gamified experience.

## Backend Responsibilities

### 1. Authentication & Authorization
- User registration and login (JWT-based)
- Session management with refresh tokens
- Admin role management for content moderation

### 2. User Profile & Game State
- Store and retrieve user profiles (username, avatar, preferences)
- Track XP, level, and progression
- Manage user inventory (items collected)
- Record completed quests and unlocked content

### 3. Gamification Logic
- Calculate XP requirements for each level
- Validate quest answers and award rewards
- Check content gating (level/item requirements)
- Handle daily login bonuses and streak tracking

### 4. Content Integration
- Sync with frontend CMS for quest/item definitions
- Track which posts have been read by each user
- Provide APIs for the frontend to check access permissions

## The API's Role in the Core Loop

1. **Explore:** Frontend calls `/api/v1/users/me` to get current user state (level, XP, inventory)
2. **Engage:** User reads a post; frontend calls `/api/v1/game/read-post` to award reading XP
3. **Progress:** User completes a quest; frontend calls `/api/v1/quests/{id}/submit` to validate and award rewards
4. **Unlock:** Frontend calls `/api/v1/game/check-access` to verify if user can access gated content
5. **Achieve:** When user uses an item to unlock content, frontend calls `/api/v1/game/use-item`

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
│         (Handles CMS content, UI, makes API calls)               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ HTTPS (REST API)
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Backend (FastAPI)                          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Auth       │  │   Game       │  │   Admin      │          │
│  │   Service    │  │   Service    │  │   Service    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────────────────────────────────────────┐           │
│  │                  Database Layer                   │           │
│  │            (SQLAlchemy / PostgreSQL)             │           │
│  └──────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PostgreSQL Database                         │
│              (Users, Progress, Inventory, Logs)                  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Design Principles

1. **Separation of Concerns:** Content lives in the frontend CMS; game logic lives in the backend
2. **Stateless API:** JWT-based auth, no server-side sessions
3. **Idempotent Operations:** Safe to retry failed requests
4. **Validation at Every Layer:** Pydantic models for request/response validation
5. **Security First:** Rate limiting, input sanitization, secure token handling
