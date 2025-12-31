# Database Schema

This document defines the database schema for "The Adventurer's Journal" backend.

---

## Overview

The database uses PostgreSQL with the following design principles:

- **UUIDs** for all primary keys (better for distributed systems, no sequential guessing)
- **Timestamps** on all tables (created_at, updated_at)
- **Soft deletes** where appropriate (deleted_at instead of hard delete)
- **Normalized design** with appropriate indexes

---

## Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────────┐
│     users       │       │   inventory_items   │
├─────────────────┤       ├─────────────────────┤
│ id (PK)         │──┐    │ id (PK)             │
│ username        │  │    │ user_id (FK)        │──┐
│ email           │  │    │ item_id             │  │
│ password_hash   │  │    │ acquired_at         │  │
│ avatar_url      │  └───<│ created_at          │  │
│ role            │       └─────────────────────┘  │
│ is_active       │                                │
│ xp              │       ┌─────────────────────┐  │
│ level           │       │   quest_progress    │  │
│ current_streak  │       ├─────────────────────┤  │
│ longest_streak  │──┐    │ id (PK)             │  │
│ last_login_at   │  │    │ user_id (FK)        │──┤
│ created_at      │  │    │ quest_id            │  │
│ updated_at      │  └───<│ completed           │  │
└─────────────────┘       │ completed_at        │  │
                          │ answer_given        │  │
                          │ attempts            │  │
                          │ created_at          │  │
                          └─────────────────────┘  │
                                                   │
                          ┌─────────────────────┐  │
                          │   post_progress     │  │
                          ├─────────────────────┤  │
                          │ id (PK)             │  │
                          │ user_id (FK)        │──┤
                          │ post_slug           │  │
                          │ has_read            │  │
                          │ read_at             │  │
                          │ is_unlocked         │  │
                          │ unlocked_at         │  │
                          │ unlocked_with_item  │  │
                          │ created_at          │  │
                          └─────────────────────┘  │
                                                   │
                          ┌─────────────────────┐  │
                          │   daily_rewards     │  │
                          ├─────────────────────┤  │
                          │ id (PK)             │  │
                          │ user_id (FK)        │──┘
                          │ claimed_at          │
                          │ reward_type         │
                          │ reward_value        │
                          │ streak_day          │
                          └─────────────────────┘

                          ┌─────────────────────┐
                          │   refresh_tokens    │
                          ├─────────────────────┤
                          │ id (PK)             │
                          │ user_id (FK)        │
                          │ token_hash          │
                          │ expires_at          │
                          │ revoked             │
                          │ created_at          │
                          └─────────────────────┘
```

---

## Table Definitions

### 1. users

Primary table for user accounts and game state.

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username        VARCHAR(30) NOT NULL UNIQUE,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    avatar_url      VARCHAR(500),
    role            VARCHAR(20) NOT NULL DEFAULT 'user',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- Game state (denormalized for performance)
    xp              INTEGER NOT NULL DEFAULT 0,
    level           INTEGER NOT NULL DEFAULT 1,
    current_streak  INTEGER NOT NULL DEFAULT 0,
    longest_streak  INTEGER NOT NULL DEFAULT 0,
    last_login_at   TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_level ON users(level);
CREATE INDEX idx_users_is_active ON users(is_active) WHERE is_active = TRUE;
```

**Role Values:**
- `user` - Regular user (default)
- `admin` - Full admin access
- `moderator` - Limited admin access (future)

---

### 2. inventory_items

Tracks items collected by users.

```sql
CREATE TABLE inventory_items (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    item_id     VARCHAR(100) NOT NULL,  -- References item definition from CMS
    acquired_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Timestamps
    created_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_user_item UNIQUE (user_id, item_id)
);

-- Indexes
CREATE INDEX idx_inventory_user_id ON inventory_items(user_id);
CREATE INDEX idx_inventory_item_id ON inventory_items(item_id);
```

**Notes:**
- `item_id` matches the item definition in the frontend CMS (`content/items/{item_id}.json`)
- One row per user-item combination (users can only have one of each item)

---

### 3. quest_progress

Tracks user progress on quests.

```sql
CREATE TABLE quest_progress (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    quest_id        VARCHAR(100) NOT NULL,  -- References quest from CMS
    completed       BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at    TIMESTAMP WITH TIME ZONE,
    answer_given    TEXT,                    -- Store the user's answer
    attempts        INTEGER NOT NULL DEFAULT 0,
    
    -- Timestamps
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_user_quest UNIQUE (user_id, quest_id)
);

-- Indexes
CREATE INDEX idx_quest_progress_user_id ON quest_progress(user_id);
CREATE INDEX idx_quest_progress_quest_id ON quest_progress(quest_id);
CREATE INDEX idx_quest_progress_completed ON quest_progress(completed) WHERE completed = TRUE;
```

**Notes:**
- `quest_id` matches the quest definition in the frontend CMS (`content/quests/{quest_id}.json`)
- `attempts` tracks how many times the user tried to answer
- `answer_given` stores the successful answer (useful for analytics)

---

### 4. post_progress

Tracks user reading progress and content unlocks.

```sql
CREATE TABLE post_progress (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    post_slug           VARCHAR(200) NOT NULL,  -- References post from CMS
    
    -- Reading tracking
    has_read            BOOLEAN NOT NULL DEFAULT FALSE,
    read_at             TIMESTAMP WITH TIME ZONE,
    
    -- Unlock tracking (for item-gated content)
    is_unlocked         BOOLEAN NOT NULL DEFAULT FALSE,
    unlocked_at         TIMESTAMP WITH TIME ZONE,
    unlocked_with_item  VARCHAR(100),  -- Which item was used to unlock
    
    -- Timestamps
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_user_post UNIQUE (user_id, post_slug)
);

-- Indexes
CREATE INDEX idx_post_progress_user_id ON post_progress(user_id);
CREATE INDEX idx_post_progress_post_slug ON post_progress(post_slug);
CREATE INDEX idx_post_progress_has_read ON post_progress(has_read) WHERE has_read = TRUE;
```

**Notes:**
- `post_slug` matches the post file name in the frontend CMS (`content/posts/{post_slug}.mdx`)
- `is_unlocked` is for item-gated posts; level-gated posts don't need tracking (just check user level)
- `unlocked_with_item` records which item was "consumed" to unlock

---

### 5. daily_rewards

Tracks daily login rewards and streaks.

```sql
CREATE TABLE daily_rewards (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    claimed_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    reward_type     VARCHAR(50) NOT NULL,  -- 'xp', 'item', 'bonus_xp'
    reward_value    VARCHAR(100) NOT NULL, -- XP amount or item ID
    streak_day      INTEGER NOT NULL,      -- Which day of the streak (1, 2, 3...)
    
    -- Timestamps
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_daily_rewards_user_id ON daily_rewards(user_id);
CREATE INDEX idx_daily_rewards_claimed_at ON daily_rewards(claimed_at);
CREATE INDEX idx_daily_rewards_user_claimed ON daily_rewards(user_id, claimed_at DESC);
```

**Notes:**
- One row per daily reward claimed
- Used to prevent claiming twice in 24 hours
- `streak_day` enables escalating rewards (day 7 = better reward)

---

### 6. refresh_tokens

Tracks refresh tokens for secure session management.

```sql
CREATE TABLE refresh_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash  VARCHAR(255) NOT NULL,  -- Hashed token (never store raw)
    expires_at  TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked     BOOLEAN NOT NULL DEFAULT FALSE,
    revoked_at  TIMESTAMP WITH TIME ZONE,
    
    -- Device/session info (optional, for "active sessions" feature)
    device_info VARCHAR(500),
    ip_address  INET,
    
    -- Timestamps
    created_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens(expires_at) WHERE revoked = FALSE;

-- Cleanup: Automatically delete expired tokens (run via cron or pg_cron)
-- DELETE FROM refresh_tokens WHERE expires_at < NOW() - INTERVAL '7 days';
```

**Notes:**
- Never store raw refresh tokens; only store hashed versions
- `revoked` is set to TRUE on logout or token rotation
- Can implement "logout all devices" by revoking all user's tokens

---

### 7. xp_transactions (Audit Log)

Optional table for tracking all XP changes (useful for debugging and analytics).

```sql
CREATE TABLE xp_transactions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount          INTEGER NOT NULL,  -- Positive or negative
    source_type     VARCHAR(50) NOT NULL,  -- 'read_post', 'quest', 'daily', 'admin', etc.
    source_id       VARCHAR(200),  -- post_slug, quest_id, etc.
    balance_before  INTEGER NOT NULL,
    balance_after   INTEGER NOT NULL,
    level_before    INTEGER NOT NULL,
    level_after     INTEGER NOT NULL,
    
    -- Timestamps
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_xp_transactions_user_id ON xp_transactions(user_id);
CREATE INDEX idx_xp_transactions_source ON xp_transactions(source_type);
CREATE INDEX idx_xp_transactions_created ON xp_transactions(created_at);
```

**Source Types:**
- `read_post` - XP from reading a post
- `quest_complete` - XP from completing a quest
- `daily_reward` - XP from daily login
- `admin_grant` - Manual XP grant by admin
- `admin_deduct` - Manual XP deduction by admin

---

## Migrations

Use Alembic for database migrations:

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

---

## Seed Data

Initial data for development/testing:

```python
# scripts/seed_db.py

async def seed_database():
    """Seed initial data for development."""
    
    # Create admin user
    admin = User(
        username="admin",
        email="admin@diegohq.dev",
        password_hash=hash_password("admin123"),  # Change in production!
        role="admin",
        xp=1000,
        level=5,
    )
    
    # Create test user
    test_user = User(
        username="TestAdventurer",
        email="test@example.com",
        password_hash=hash_password("test123"),
        role="user",
        xp=150,
        level=2,
    )
    
    # Give test user some items
    test_items = [
        InventoryItem(user=test_user, item_id="map-to-cloud-kingdom"),
    ]
    
    # Mark some quests complete
    test_quests = [
        QuestProgress(
            user=test_user,
            quest_id="the-first-chronicler",
            completed=True,
            completed_at=datetime.now(timezone.utc),
            answer_given="git commit",
        ),
    ]
    
    # ... save to database
```

---

## Performance Considerations

### Indexes

All foreign keys and commonly queried columns are indexed. Consider adding:

- Composite indexes for common query patterns
- Partial indexes for boolean flags (e.g., `WHERE is_active = TRUE`)
- Expression indexes if needed

### Denormalization

The `users` table includes `xp` and `level` directly (instead of calculating from transactions) for:

- Faster reads on the common "get user profile" query
- Simpler queries for leaderboards and level checks

The trade-off is maintaining consistency when XP changes (always update both the transaction log and user record in a transaction).

### Caching

Consider Redis caching for:

- User profiles (cache invalidate on XP change)
- Leaderboards (recalculate periodically)
- Session data

---

## Data Retention

| Table | Retention Policy |
|-------|------------------|
| users | Indefinite (soft delete after 30 days) |
| inventory_items | Tied to user lifetime |
| quest_progress | Tied to user lifetime |
| post_progress | Tied to user lifetime |
| daily_rewards | 1 year (for analytics) |
| refresh_tokens | Auto-delete expired after 7 days |
| xp_transactions | 1 year (for analytics/debugging) |

---

## GDPR Compliance

For user data export (GDPR Article 15):

```sql
-- Export all user data
SELECT 
    u.*,
    json_agg(DISTINCT i.item_id) as inventory,
    json_agg(DISTINCT q.quest_id) FILTER (WHERE q.completed) as completed_quests,
    json_agg(DISTINCT p.post_slug) FILTER (WHERE p.has_read) as read_posts
FROM users u
LEFT JOIN inventory_items i ON u.id = i.user_id
LEFT JOIN quest_progress q ON u.id = q.user_id
LEFT JOIN post_progress p ON u.id = p.user_id
WHERE u.id = :user_id
GROUP BY u.id;
```

For user data deletion (GDPR Article 17):

```sql
-- Soft delete (immediate)
UPDATE users SET deleted_at = NOW(), is_active = FALSE WHERE id = :user_id;

-- Hard delete (after 30 days)
DELETE FROM users WHERE id = :user_id;
-- CASCADE will remove inventory_items, quest_progress, post_progress, daily_rewards, refresh_tokens
```
