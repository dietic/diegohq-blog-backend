# API Specification

This document provides detailed API endpoint specifications for "The Adventurer's Journal" backend.

---

## Base URL

```
Production: https://api.diegohq.dev/api/v1
Development: http://localhost:8000/api/v1
```

---

## Authentication

All authenticated endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

---

## Endpoints

### 1. Authentication

#### POST /auth/register

Create a new user account.

**Request:**
```json
{
  "username": "Adventurer42",
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "Adventurer42",
  "email": "user@example.com",
  "xp": 0,
  "level": 1,
  "createdAt": "2025-01-01T00:00:00Z"
}
```

**Errors:**
- `400` - Validation error (invalid email, password too short)
- `409` - Username or email already exists

---

#### POST /auth/login

Authenticate and receive tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (200 OK):**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIs...",
  "tokenType": "bearer",
  "expiresIn": 1800
}
```

**Headers Set:**
```
Set-Cookie: refresh_token=<token>; HttpOnly; Secure; SameSite=Strict; Path=/api/v1/auth
```

**Errors:**
- `401` - Invalid credentials
- `403` - Account disabled

---

#### POST /auth/refresh

Get a new access token using refresh token.

**Request:**
Refresh token sent via HTTP-only cookie.

**Response (200 OK):**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIs...",
  "tokenType": "bearer",
  "expiresIn": 1800
}
```

**Errors:**
- `401` - Invalid or expired refresh token

---

#### POST /auth/logout

Invalidate the current session.

**Request:**
Requires authentication. Refresh token sent via cookie.

**Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

**Headers Set:**
```
Set-Cookie: refresh_token=; HttpOnly; Secure; SameSite=Strict; Path=/api/v1/auth; Max-Age=0
```

---

#### POST /auth/forgot-password

Request a password reset email.

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "If an account exists, a reset email has been sent"
}
```

---

#### POST /auth/reset-password

Reset password using token from email.

**Request:**
```json
{
  "token": "reset-token-from-email",
  "newPassword": "newSecurePassword123"
}
```

**Response (200 OK):**
```json
{
  "message": "Password successfully reset"
}
```

**Errors:**
- `400` - Invalid or expired token

---

### 2. Users

#### GET /users/me

Get the current user's profile with full game state.

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "Adventurer42",
  "email": "user@example.com",
  "avatarUrl": "/avatars/knight.png",
  "role": "user",
  "xp": 350,
  "level": 3,
  "xpToNextLevel": 520,
  "xpProgress": 0.67,
  "currentStreak": 5,
  "longestStreak": 7,
  "createdAt": "2025-01-01T00:00:00Z",
  "inventory": [
    {
      "itemId": "map-to-cloud-kingdom",
      "acquiredAt": "2025-01-15T10:30:00Z"
    }
  ],
  "completedQuests": ["the-first-chronicler", "cloud-ascendant"],
  "readPosts": ["intro-to-git", "understanding-github"],
  "unlockedPosts": ["teamwork-makes-dream-work"],
  "stats": {
    "totalXpEarned": 450,
    "questsCompleted": 3,
    "postsRead": 12,
    "itemsCollected": 5
  }
}
```

---

#### PATCH /users/me

Update the current user's profile.

**Request:**
```json
{
  "username": "NewUsername",
  "avatarUrl": "/avatars/wizard.png"
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "NewUsername",
  "avatarUrl": "/avatars/wizard.png",
  // ... rest of user fields
}
```

**Errors:**
- `409` - Username already taken

---

#### DELETE /users/me

Delete the current user's account.

**Request:**
```json
{
  "password": "currentPassword"
}
```

**Response (200 OK):**
```json
{
  "message": "Account scheduled for deletion",
  "deletionDate": "2025-02-01T00:00:00Z"
}
```

---

#### GET /users/me/inventory

Get the current user's inventory.

**Response (200 OK):**
```json
{
  "items": [
    {
      "itemId": "map-to-cloud-kingdom",
      "name": "Map to the Cloud Kingdom",
      "description": "An ancient map revealing the path to GitHub.",
      "icon": "/items/map-cloud.png",
      "rarity": "uncommon",
      "acquiredAt": "2025-01-15T10:30:00Z"
    },
    {
      "itemId": "fire-potion",
      "name": "Fire Potion",
      "description": "A bubbling red potion that can melt any ice.",
      "icon": "/items/fire-potion.png",
      "rarity": "rare",
      "acquiredAt": "2025-01-20T14:00:00Z"
    }
  ],
  "total": 2
}
```

---

#### GET /users/me/quests

Get the current user's quest history.

**Query Parameters:**
- `status` (optional): `completed`, `in_progress`, `all` (default: `all`)
- `page` (optional): Page number (default: 1)
- `pageSize` (optional): Items per page (default: 20, max: 100)

**Response (200 OK):**
```json
{
  "items": [
    {
      "questId": "the-first-chronicler",
      "name": "The First Chronicler",
      "completed": true,
      "completedAt": "2025-01-10T12:00:00Z",
      "xpEarned": 40,
      "itemEarned": "map-to-cloud-kingdom"
    },
    {
      "questId": "cloud-ascendant",
      "name": "Cloud Ascendant",
      "completed": false,
      "attempts": 2
    }
  ],
  "total": 2,
  "page": 1,
  "pageSize": 20,
  "totalPages": 1
}
```

---

### 3. Game Mechanics

#### POST /game/read-post

Award XP for reading a post.

**Request:**
```json
{
  "postSlug": "intro-to-git",
  "readXp": 10
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "xpAwarded": 10,
  "newTotalXp": 360,
  "leveledUp": false,
  "currentLevel": 3,
  "xpToNextLevel": 520,
  "xpProgress": 0.69
}
```

**Response when level up (200 OK):**
```json
{
  "success": true,
  "xpAwarded": 10,
  "newTotalXp": 525,
  "leveledUp": true,
  "previousLevel": 3,
  "currentLevel": 4,
  "xpToNextLevel": 800,
  "xpProgress": 0.01
}
```

**Errors:**
- `400` - Already awarded XP for this post

---

#### GET /game/check-access

Check if user can access a specific post.

**Query Parameters:**
- `postSlug`: The post to check access for

**Response (200 OK - Has Access):**
```json
{
  "hasAccess": true,
  "postSlug": "intro-to-git"
}
```

**Response (200 OK - Level Gated):**
```json
{
  "hasAccess": false,
  "postSlug": "advanced-patterns",
  "gateType": "level",
  "requiredLevel": 5,
  "currentLevel": 3
}
```

**Response (200 OK - Item Gated):**
```json
{
  "hasAccess": false,
  "postSlug": "frozen-knowledge",
  "gateType": "item",
  "requiredItem": "fire-potion",
  "hasItem": false,
  "challengeText": "A wall of ice blocks this ancient script."
}
```

**Response (200 OK - Item Gated, Has Item):**
```json
{
  "hasAccess": false,
  "postSlug": "frozen-knowledge",
  "gateType": "item",
  "requiredItem": "fire-potion",
  "hasItem": true,
  "challengeText": "A wall of ice blocks this ancient script.",
  "canUnlock": true
}
```

---

#### POST /game/use-item

Use an item to unlock gated content.

**Request:**
```json
{
  "itemId": "fire-potion",
  "postSlug": "frozen-knowledge"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "postSlug": "frozen-knowledge",
  "itemUsed": "fire-potion",
  "postUnlocked": true
}
```

**Errors:**
- `400` - User doesn't have the item
- `400` - Post doesn't require this item
- `400` - Post already unlocked

---

#### GET /game/level-progress

Get detailed level progress information.

**Response (200 OK):**
```json
{
  "currentLevel": 3,
  "currentXp": 350,
  "xpForCurrentLevel": 282,
  "xpForNextLevel": 520,
  "xpProgress": 0.67,
  "xpNeeded": 170,
  "levelHistory": [
    { "level": 1, "reachedAt": "2025-01-01T00:00:00Z" },
    { "level": 2, "reachedAt": "2025-01-05T10:00:00Z" },
    { "level": 3, "reachedAt": "2025-01-15T14:30:00Z" }
  ]
}
```

---

#### POST /game/daily-reward

Claim the daily login reward.

**Response (200 OK):**
```json
{
  "success": true,
  "rewardType": "xp",
  "rewardValue": 5,
  "streakDay": 3,
  "currentStreak": 3,
  "nextClaimAt": "2025-01-16T00:00:00Z",
  "streakBonus": "Day 7 reward: Mystery Item!"
}
```

**Response (429 Too Many Requests - Already Claimed):**
```json
{
  "error": "daily_reward_claimed",
  "message": "Daily reward already claimed",
  "nextClaimAt": "2025-01-16T00:00:00Z"
}
```

---

### 4. Quests

#### GET /quests/{questId}

Get quest information (public, no auth required).

**Response (200 OK):**
```json
{
  "id": "the-first-chronicler",
  "name": "The First Chronicler",
  "description": "Prove your understanding of Git basics.",
  "type": "text-input",
  "prompt": "What is the command to save your changes to your local repository?",
  "difficulty": "easy",
  "xpReward": 40,
  "itemReward": "map-to-cloud-kingdom",
  "hostPostSlug": "intro-to-git"
}
```

---

#### GET /quests/{questId}/status

Get user's progress on a specific quest.

**Response (200 OK - Not Started):**
```json
{
  "questId": "the-first-chronicler",
  "status": "not_started"
}
```

**Response (200 OK - In Progress):**
```json
{
  "questId": "the-first-chronicler",
  "status": "in_progress",
  "attempts": 2
}
```

**Response (200 OK - Completed):**
```json
{
  "questId": "the-first-chronicler",
  "status": "completed",
  "completedAt": "2025-01-10T12:00:00Z",
  "xpEarned": 40,
  "itemEarned": "map-to-cloud-kingdom"
}
```

---

#### POST /quests/{questId}/submit

Submit an answer to a quest.

**Request:**
```json
{
  "answer": "git commit"
}
```

**Response (200 OK - Correct):**
```json
{
  "correct": true,
  "questId": "the-first-chronicler",
  "xpAwarded": 40,
  "itemAwarded": {
    "itemId": "map-to-cloud-kingdom",
    "name": "Map to the Cloud Kingdom"
  },
  "newTotalXp": 400,
  "leveledUp": false
}
```

**Response (200 OK - Incorrect):**
```json
{
  "correct": false,
  "questId": "the-first-chronicler",
  "attempts": 3,
  "hint": "Think about saving changes locally before pushing..."
}
```

**Errors:**
- `400` - Quest already completed
- `404` - Quest not found

---

### 5. Items

#### GET /items

List all available items.

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "map-to-cloud-kingdom",
      "name": "Map to the Cloud Kingdom",
      "description": "An ancient map revealing the path to GitHub.",
      "icon": "/items/map-cloud.png",
      "rarity": "uncommon"
    },
    {
      "id": "fire-potion",
      "name": "Fire Potion",
      "description": "A bubbling red potion that can melt any ice.",
      "icon": "/items/fire-potion.png",
      "rarity": "rare"
    }
  ]
}
```

---

#### GET /items/{itemId}

Get a specific item's details.

**Response (200 OK):**
```json
{
  "id": "map-to-cloud-kingdom",
  "name": "Map to the Cloud Kingdom",
  "description": "An ancient map revealing the path to GitHub.",
  "icon": "/items/map-cloud.png",
  "rarity": "uncommon",
  "flavorText": "With this map, the fog lifts and the way becomes clear.",
  "usedFor": ["understanding-github"]
}
```

---

### 6. Admin Endpoints

All admin endpoints require `role: admin`.

#### GET /admin/users

List all users (paginated).

**Query Parameters:**
- `page`: Page number (default: 1)
- `pageSize`: Items per page (default: 20, max: 100)
- `search`: Search by username or email
- `role`: Filter by role
- `sortBy`: Sort field (default: `createdAt`)
- `sortOrder`: `asc` or `desc` (default: `desc`)

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "Adventurer42",
      "email": "user@example.com",
      "role": "user",
      "xp": 350,
      "level": 3,
      "isActive": true,
      "createdAt": "2025-01-01T00:00:00Z",
      "lastLoginAt": "2025-01-15T10:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "pageSize": 20,
  "totalPages": 8
}
```

---

#### POST /admin/award-xp

Manually award XP to a user.

**Request:**
```json
{
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "amount": 100,
  "reason": "Bug bounty reward"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "xpAwarded": 100,
  "newTotalXp": 450,
  "newLevel": 3
}
```

---

#### POST /admin/grant-item

Grant an item to a user.

**Request:**
```json
{
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "itemId": "legendary-sword",
  "reason": "Contest winner"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "itemGranted": "legendary-sword"
}
```

---

### 7. Utility Endpoints

#### GET /health

Health check endpoint.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0",
  "timestamp": "2025-01-15T12:00:00Z"
}
```

---

#### GET /version

API version information.

**Response (200 OK):**
```json
{
  "version": "1.0.0",
  "build": "abc123",
  "environment": "production"
}
```

---

## Error Response Format

All errors follow this format:

```json
{
  "detail": "Human-readable error message",
  "code": "ERROR_CODE"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `UNAUTHORIZED` | 401 | Missing or invalid token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource already exists |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Rate Limiting Headers

All responses include rate limiting headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705315200
```

---

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `page`: Page number (1-indexed)
- `pageSize`: Items per page (default varies, max 100)

**Response Format:**
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "pageSize": 20,
  "totalPages": 8
}
```
