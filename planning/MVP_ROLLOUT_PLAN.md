# MVP Rollout Plan - Backend

This document outlines a phased approach to building "The Adventurer's Journal" backend.

---

## Phase 1: Core API Foundation

The goal of this phase is to build the essential authentication and user profile APIs.

### Key Objectives:

- [ ] **Project Setup**
  - [ ] Initialize FastAPI project structure
  - [ ] Configure pyproject.toml with dependencies
  - [ ] Set up Ruff for linting and formatting
  - [ ] Configure mypy for type checking
  - [ ] Create Dockerfile and docker-compose.yml
  - [ ] Set up environment configuration (Pydantic Settings)

- [ ] **Database Setup**
  - [ ] Configure SQLAlchemy with async PostgreSQL
  - [ ] Create base model classes (UUID, Timestamps)
  - [ ] Set up Alembic for migrations
  - [ ] Create initial migration with users table
  - [ ] Create seed script for dev data

- [ ] **Authentication**
  - [ ] Implement password hashing (Argon2)
  - [ ] Create JWT token generation and validation
  - [ ] Build `/auth/register` endpoint
  - [ ] Build `/auth/login` endpoint
  - [ ] Build `/auth/refresh` endpoint
  - [ ] Build `/auth/logout` endpoint
  - [ ] Implement refresh token storage and rotation
  - [ ] Set up HTTP-only cookie handling

- [ ] **User Profile**
  - [ ] Build `/users/me` endpoint (GET)
  - [ ] Build `/users/me` endpoint (PATCH)
  - [ ] Return user game state (xp, level, inventory)

- [ ] **Health & Utilities**
  - [ ] Build `/health` endpoint
  - [ ] Build `/version` endpoint
  - [ ] Set up CORS configuration

**Testing:**
- [ ] Write tests for auth endpoints
- [ ] Write tests for user endpoints

**Outcome:** A functional authentication system with user profiles.

---

## Phase 2: Game Mechanics Core

This phase implements the fundamental gamification logic.

### Key Objectives:

- [ ] **XP & Leveling System**
  - [ ] Implement level calculation utilities
  - [ ] Create XP award service
  - [ ] Add XP transaction logging
  - [ ] Build `/game/read-post` endpoint
  - [ ] Build `/game/level-progress` endpoint

- [ ] **Post Progress Tracking**
  - [ ] Create post_progress table and model
  - [ ] Track which posts users have read
  - [ ] Prevent double XP awards for same post

- [ ] **Level-Up Detection**
  - [ ] Detect when XP crosses level threshold
  - [ ] Return level-up info in API responses

- [ ] **Content Access Checking**
  - [ ] Build `/game/check-access` endpoint
  - [ ] Implement level-based access logic

**Testing:**
- [ ] Write tests for XP calculations
- [ ] Write tests for level-up scenarios
- [ ] Write tests for access checking

**Outcome:** Users can earn XP by reading posts and level up.

---

## Phase 3: Quest System

This phase adds the quest completion and reward system.

### Key Objectives:

- [ ] **Quest Progress Tracking**
  - [ ] Create quest_progress table and model
  - [ ] Track quest attempts and completion

- [ ] **Quest Submission**
  - [ ] Build `/quests/{questId}` endpoint (GET)
  - [ ] Build `/quests/{questId}/status` endpoint
  - [ ] Build `/quests/{questId}/submit` endpoint
  - [ ] Implement answer validation logic
  - [ ] Handle multiple quest types (multiple-choice, text-input, call-to-action)

- [ ] **Inventory System**
  - [ ] Create inventory_items table and model
  - [ ] Build `/users/me/inventory` endpoint
  - [ ] Award items as quest rewards
  - [ ] Build `/items/{itemId}` endpoint

- [ ] **Item-Based Content Gating**
  - [ ] Extend `/game/check-access` for item gating
  - [ ] Build `/game/use-item` endpoint
  - [ ] Track unlocked posts

**Testing:**
- [ ] Write tests for quest submission
- [ ] Write tests for item rewards
- [ ] Write tests for item-based unlocking

**Outcome:** Complete quest loop with rewards and content unlocking.

---

## Phase 4: Daily Rewards & Engagement

This phase adds engagement features to encourage return visits.

### Key Objectives:

- [ ] **Daily Rewards**
  - [ ] Create daily_rewards table and model
  - [ ] Build `/game/daily-reward` endpoint
  - [ ] Implement 24-hour claim cooldown
  - [ ] Track and reset login streaks
  - [ ] Escalating rewards for streak days

- [ ] **User Statistics**
  - [ ] Calculate and return user stats
  - [ ] Track total XP earned
  - [ ] Track quests completed
  - [ ] Track posts read

- [ ] **Rate Limiting**
  - [ ] Install and configure SlowAPI
  - [ ] Apply rate limits to game endpoints
  - [ ] Apply stricter limits to auth endpoints

**Testing:**
- [ ] Write tests for daily rewards
- [ ] Write tests for streak logic
- [ ] Write tests for rate limiting

**Outcome:** Engagement features that encourage daily visits.

---

## Phase 5: Admin & Analytics

This phase adds admin functionality and monitoring.

### Key Objectives:

- [ ] **Admin Endpoints**
  - [ ] Create admin role middleware
  - [ ] Build `/admin/users` endpoint (list, search)
  - [ ] Build `/admin/users/{userId}` endpoint
  - [ ] Build `/admin/award-xp` endpoint
  - [ ] Build `/admin/grant-item` endpoint

- [ ] **Content Sync**
  - [ ] Script to sync quest definitions from CMS
  - [ ] Script to sync item definitions from CMS
  - [ ] Build `/admin/sync-items` endpoint
  - [ ] Build `/admin/sync-quests` endpoint

- [ ] **Analytics & Monitoring**
  - [ ] Basic analytics dashboard data
  - [ ] Quest completion rates
  - [ ] User progression metrics
  - [ ] Set up structured logging
  - [ ] Error tracking integration (Sentry optional)

**Testing:**
- [ ] Write tests for admin endpoints
- [ ] Write tests for content sync

**Outcome:** Admin tools for content management and basic analytics.

---

## Phase 6: Security & Production Readiness

This phase hardens the API for production deployment.

### Key Objectives:

- [ ] **Security Hardening**
  - [ ] Security audit of all endpoints
  - [ ] Input validation review
  - [ ] SQL injection prevention check
  - [ ] Implement request signing (optional)
  - [ ] Add CSRF protection for cookie-based auth

- [ ] **Password Reset Flow**
  - [ ] Build `/auth/forgot-password` endpoint
  - [ ] Build `/auth/reset-password` endpoint
  - [ ] Email service integration (or placeholder)

- [ ] **Account Management**
  - [ ] Build `/auth/change-password` endpoint
  - [ ] Build `/users/me` DELETE endpoint
  - [ ] Implement soft delete with recovery
  - [ ] GDPR data export endpoint

- [ ] **Performance Optimization**
  - [ ] Database query optimization
  - [ ] Add strategic indexes
  - [ ] Implement caching where needed
  - [ ] Response compression

- [ ] **Documentation**
  - [ ] Auto-generate OpenAPI spec
  - [ ] Write API documentation
  - [ ] Deployment guide

**Testing:**
- [ ] Security-focused test cases
- [ ] Load testing

**Outcome:** Production-ready, secure API.

---

## Deployment Strategy

### Development

```bash
# Local development with Docker
docker-compose up -d postgres
uvicorn src.main:app --reload --port 8000
```

### Staging

- Deploy to staging environment (Railway, Render, etc.)
- Run migrations
- Seed test data
- Integration testing with frontend

### Production

- Blue-green deployment
- Database migrations with zero downtime
- Health check monitoring
- Automated backups

---

## Dependency on Frontend

The backend is designed to work independently but expects:

1. **CMS Content Definitions:** Quest and item JSON files from frontend
2. **API Consumption:** Frontend calls backend APIs for game state
3. **Content Gating:** Frontend handles UI gating; backend validates access

### Data Flow

```
Frontend CMS (content/quests/*.json)
           │
           ▼ (sync script or manual)
┌──────────────────────────────────┐
│       Backend Database           │
│  (quest definitions cached)      │
└──────────────────────────────────┘
           │
           ▼ (API responses)
┌──────────────────────────────────┐
│       Frontend App               │
│  (displays quests, items, UI)    │
└──────────────────────────────────┘
```

---

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Core API | 1-2 weeks | None |
| Phase 2: Game Mechanics | 1 week | Phase 1 |
| Phase 3: Quest System | 1-2 weeks | Phase 2 |
| Phase 4: Daily Rewards | 1 week | Phase 3 |
| Phase 5: Admin & Analytics | 1 week | Phase 4 |
| Phase 6: Security & Production | 1-2 weeks | Phase 5 |

**Total Estimated Time:** 6-10 weeks

---

## Success Criteria

### Phase 1 Complete When:
- [ ] Users can register and login
- [ ] Users can retrieve their profile
- [ ] JWT authentication works end-to-end
- [ ] Tests pass with >80% coverage

### Phase 2 Complete When:
- [ ] XP is awarded for reading posts
- [ ] Level-ups are detected correctly
- [ ] Level-based access works
- [ ] Frontend can integrate with `/game/read-post`

### Phase 3 Complete When:
- [ ] Quests can be submitted and validated
- [ ] Items are awarded as rewards
- [ ] Items can unlock gated content
- [ ] Inventory is displayed correctly

### Phase 4 Complete When:
- [ ] Daily rewards can be claimed
- [ ] Streaks are tracked correctly
- [ ] Rate limiting prevents abuse

### MVP Complete When:
- [ ] All Phase 1-4 criteria met
- [ ] Frontend-backend integration works
- [ ] No critical bugs
- [ ] Performance is acceptable (<200ms avg response)
