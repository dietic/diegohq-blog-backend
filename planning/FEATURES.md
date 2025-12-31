# Features List - Backend API

This document outlines the key features and API endpoints of "The Adventurer's Journal" backend.

---

## 1. Authentication & Authorization

### User Registration
- **Endpoint:** `POST /api/v1/auth/register`
- Email/password registration with validation
- Username uniqueness check
- Password hashing (bcrypt/argon2)
- Optional email verification flow

### User Login
- **Endpoint:** `POST /api/v1/auth/login`
- Returns JWT access token + refresh token
- Access token: Short-lived (15-30 minutes)
- Refresh token: Long-lived (7-30 days), stored in HTTP-only cookie

### Token Refresh
- **Endpoint:** `POST /api/v1/auth/refresh`
- Exchange refresh token for new access token
- Rotate refresh token on use (security best practice)

### Logout
- **Endpoint:** `POST /api/v1/auth/logout`
- Invalidate refresh token on server
- Clear HTTP-only cookie

### Password Management
- **Endpoint:** `POST /api/v1/auth/forgot-password` - Request reset email
- **Endpoint:** `POST /api/v1/auth/reset-password` - Reset with token
- **Endpoint:** `POST /api/v1/auth/change-password` - Authenticated password change

---

## 2. User Profile Management

### Get Current User
- **Endpoint:** `GET /api/v1/users/me`
- Returns complete user profile with game state:
  ```json
  {
    "id": "uuid",
    "username": "Adventurer42",
    "email": "user@example.com",
    "avatarUrl": "/avatars/knight.png",
    "xp": 350,
    "level": 3,
    "xpToNextLevel": 520,
    "xpProgress": 0.67,
    "createdAt": "2025-01-01T00:00:00Z",
    "inventory": ["map-to-cloud-kingdom", "fire-potion"],
    "completedQuests": ["the-first-chronicler"],
    "readPosts": ["intro-to-git", "understanding-github"],
    "unlockedPosts": ["teamwork-makes-dream-work"],
    "stats": {
      "totalXpEarned": 450,
      "questsCompleted": 3,
      "postsRead": 12,
      "currentStreak": 5,
      "longestStreak": 7
    }
  }
  ```

### Update Profile
- **Endpoint:** `PATCH /api/v1/users/me`
- Update username, avatar, preferences
- Validate username uniqueness

### Delete Account
- **Endpoint:** `DELETE /api/v1/users/me`
- Soft delete with 30-day recovery window
- Anonymize data after recovery period

---

## 3. Game Mechanics API

### Read Post (Award XP)
- **Endpoint:** `POST /api/v1/game/read-post`
- **Request:** `{ "postSlug": "intro-to-git", "readXp": 10 }`
- Awards XP only once per post per user
- Checks for level-up trigger
- **Response:** Updated XP, level, and any level-up rewards

### Submit Quest Answer
- **Endpoint:** `POST /api/v1/quests/{questId}/submit`
- **Request:** `{ "answer": "git commit" }`
- Validates answer against correct answer (case-insensitive, trimmed)
- Awards XP and optional item reward
- Marks quest as completed
- **Response:** Success status, XP awarded, item received (if any)

### Check Content Access
- **Endpoint:** `GET /api/v1/game/check-access`
- **Query:** `?postSlug=advanced-git&type=level` or `?postSlug=secret-post&type=item`
- Returns access status and requirements if locked
- **Response:**
  ```json
  {
    "hasAccess": false,
    "reason": "level",
    "requiredLevel": 5,
    "currentLevel": 3
  }
  ```

### Use Item to Unlock Content
- **Endpoint:** `POST /api/v1/game/use-item`
- **Request:** `{ "itemId": "fire-potion", "postSlug": "frozen-knowledge" }`
- Verifies user has item in inventory
- Verifies post requires this item
- Marks post as unlocked for user
- **Response:** Success status, updated unlocked posts

### Get Level Progress
- **Endpoint:** `GET /api/v1/game/level-progress`
- Returns current level, XP, XP needed for next level, progress percentage

### Claim Daily Reward
- **Endpoint:** `POST /api/v1/game/daily-reward`
- Awards daily login bonus (XP or item)
- Tracks streak for bonus multipliers
- Returns next claim time (24h cooldown)

---

## 4. Inventory & Items

### Get User Inventory
- **Endpoint:** `GET /api/v1/users/me/inventory`
- Returns list of items with details
- **Response:**
  ```json
  {
    "items": [
      {
        "id": "map-to-cloud-kingdom",
        "name": "Map to the Cloud Kingdom",
        "description": "An ancient map revealing the path to GitHub.",
        "icon": "/items/map-cloud.png",
        "rarity": "uncommon",
        "acquiredAt": "2025-01-15T10:30:00Z"
      }
    ]
  }
  ```

### Get Item Details
- **Endpoint:** `GET /api/v1/items/{itemId}`
- Returns item metadata (from database, synced with CMS)

---

## 5. Quest Management

### Get Quest Status
- **Endpoint:** `GET /api/v1/quests/{questId}/status`
- Returns whether user has completed quest
- **Response:** `{ "completed": true, "completedAt": "2025-01-10T..." }`

### Get User Quest History
- **Endpoint:** `GET /api/v1/users/me/quests`
- Returns list of completed and in-progress quests
- Paginated response

---

## 6. Admin Endpoints (Protected)

### User Management
- **Endpoint:** `GET /api/v1/admin/users` - List all users (paginated)
- **Endpoint:** `GET /api/v1/admin/users/{userId}` - Get user details
- **Endpoint:** `PATCH /api/v1/admin/users/{userId}` - Update user (role, ban, etc.)
- **Endpoint:** `DELETE /api/v1/admin/users/{userId}` - Delete user

### Game Data Management
- **Endpoint:** `POST /api/v1/admin/award-xp` - Manually award XP to user
- **Endpoint:** `POST /api/v1/admin/grant-item` - Grant item to user
- **Endpoint:** `POST /api/v1/admin/reset-progress` - Reset user progress

### Content Sync
- **Endpoint:** `POST /api/v1/admin/sync-items` - Sync items from CMS
- **Endpoint:** `POST /api/v1/admin/sync-quests` - Sync quests from CMS

### Analytics
- **Endpoint:** `GET /api/v1/admin/analytics/overview` - Dashboard stats
- **Endpoint:** `GET /api/v1/admin/analytics/quests` - Quest completion rates
- **Endpoint:** `GET /api/v1/admin/analytics/posts` - Post read statistics

---

## 7. Utility Endpoints

### Health Check
- **Endpoint:** `GET /api/v1/health`
- Returns API status, database connection status, version

### API Version
- **Endpoint:** `GET /api/v1/version`
- Returns API version and build info

---

## 8. Rate Limiting Tiers

| Endpoint Category | Rate Limit |
|-------------------|------------|
| Auth (login, register) | 5 requests/minute |
| Game actions (read-post, submit quest) | 30 requests/minute |
| Profile updates | 10 requests/minute |
| General API | 100 requests/minute |
| Admin endpoints | 50 requests/minute |

---

## 9. Webhook Support (Future)

### Level Up Webhook
- Trigger external integrations when user levels up
- Payload includes user info and new level

### Quest Completion Webhook
- Trigger when user completes a quest
- Payload includes quest ID and rewards granted
