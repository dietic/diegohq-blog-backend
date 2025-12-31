# Gamification Mechanics - Backend

This document details the server-side implementation of the gamification systems.

---

## 1. Experience Points (XP) System

### XP Sources

| Source | Base XP | Notes |
|--------|---------|-------|
| Reading a post | 10-20 | Defined per post in CMS (`readXp`) |
| Completing a quest | 30-100 | Defined per quest in CMS (`xpReward`) |
| Daily login bonus | 5-25 | Escalates with streak |
| Challenge completion | 100-250 | For multi-step challenges |

### XP Award Logic

```python
# src/services/game_service.py

async def award_xp(
    self,
    user_id: UUID,
    amount: int,
    source_type: str,
    source_id: str | None = None,
) -> tuple[int, int, bool]:
    """
    Award XP to a user and handle level-ups.
    
    Args:
        user_id: User's UUID
        amount: XP amount to award
        source_type: Type of XP source ('read_post', 'quest', 'daily', etc.)
        source_id: Optional identifier (post_slug, quest_id)
    
    Returns:
        Tuple of (new_total_xp, new_level, did_level_up)
    """
    user = await self.user_repo.get_by_id(user_id)
    
    old_xp = user.xp
    old_level = user.level
    
    new_xp = old_xp + amount
    new_level = calculate_level_from_xp(new_xp)
    did_level_up = new_level > old_level
    
    # Update user
    await self.user_repo.update(
        user_id,
        xp=new_xp,
        level=new_level,
    )
    
    # Log transaction
    await self.xp_repo.create_transaction(
        user_id=user_id,
        amount=amount,
        source_type=source_type,
        source_id=source_id,
        balance_before=old_xp,
        balance_after=new_xp,
        level_before=old_level,
        level_after=new_level,
    )
    
    return new_xp, new_level, did_level_up
```

### Preventing Double XP

```python
async def award_read_xp(
    self,
    user_id: UUID,
    post_slug: str,
    xp_amount: int,
) -> dict:
    """Award XP for reading a post (once per user per post)."""
    
    # Check if already awarded
    progress = await self.progress_repo.get_post_progress(user_id, post_slug)
    if progress and progress.has_read:
        raise BadRequestException(
            detail="XP already awarded for this post",
            code="XP_ALREADY_AWARDED",
        )
    
    # Award XP
    new_xp, new_level, leveled_up = await self.award_xp(
        user_id=user_id,
        amount=xp_amount,
        source_type="read_post",
        source_id=post_slug,
    )
    
    # Mark post as read
    await self.progress_repo.mark_post_read(user_id, post_slug)
    
    return {
        "success": True,
        "xpAwarded": xp_amount,
        "newTotalXp": new_xp,
        "leveledUp": leveled_up,
        "currentLevel": new_level,
    }
```

---

## 2. Leveling System

### Level Curve Formula

The XP required to reach each level follows an exponential curve:

```python
# src/utils/level_calculator.py

import math

# XP thresholds (cumulative)
# Level 1: 0 XP (starting level)
# Level 2: 100 XP
# Level 3: 282 XP
# Level 4: 520 XP
# ...

def calculate_xp_for_level(level: int) -> int:
    """
    Calculate cumulative XP required to reach a level.
    
    Formula: XP = floor(level^1.5 * 100)
    
    Level 1 = 0 (starting level)
    Level 2 = 100
    Level 3 = 282
    Level 4 = 520
    Level 5 = 800
    Level 10 = 3162
    Level 20 = 8944
    Level 50 = 35355
    """
    if level <= 1:
        return 0
    return int(math.floor((level ** 1.5) * 100))


def calculate_level_from_xp(xp: int) -> int:
    """
    Calculate user's level based on total XP.
    
    Inverse of the level formula.
    """
    if xp < 100:
        return 1
    
    # Solve: xp = level^1.5 * 100
    # level = (xp / 100)^(2/3)
    level = int((xp / 100) ** (2/3))
    
    # Verify and adjust
    while calculate_xp_for_level(level + 1) <= xp:
        level += 1
    
    return level


def calculate_xp_progress(xp: int) -> dict:
    """
    Calculate detailed progress within current level.
    
    Returns:
        {
            "currentLevel": 3,
            "currentXp": 350,
            "xpForCurrentLevel": 282,
            "xpForNextLevel": 520,
            "xpProgress": 0.286,
            "xpNeeded": 170
        }
    """
    level = calculate_level_from_xp(xp)
    xp_for_current = calculate_xp_for_level(level)
    xp_for_next = calculate_xp_for_level(level + 1)
    
    xp_in_level = xp - xp_for_current
    xp_range = xp_for_next - xp_for_current
    progress = xp_in_level / xp_range if xp_range > 0 else 0
    
    return {
        "currentLevel": level,
        "currentXp": xp,
        "xpForCurrentLevel": xp_for_current,
        "xpForNextLevel": xp_for_next,
        "xpProgress": round(progress, 3),
        "xpNeeded": xp_for_next - xp,
    }
```

### Level Progression Table

| Level | Cumulative XP | XP to Next Level |
|-------|---------------|------------------|
| 1 | 0 | 100 |
| 2 | 100 | 182 |
| 3 | 282 | 238 |
| 4 | 520 | 280 |
| 5 | 800 | 324 |
| 10 | 3,162 | 485 |
| 15 | 5,809 | 610 |
| 20 | 8,944 | 720 |
| 50 | 35,355 | 1,421 |

---

## 3. Quest Validation

### Answer Matching

```python
# src/services/quest_service.py

import re
from difflib import SequenceMatcher


def normalize_answer(answer: str) -> str:
    """Normalize an answer for comparison."""
    return re.sub(r'\s+', ' ', answer.lower().strip())


def check_answer(
    user_answer: str,
    correct_answer: str,
    match_type: str = "exact",
) -> bool:
    """
    Check if user's answer matches the correct answer.
    
    Match types:
    - exact: Must match exactly (after normalization)
    - contains: User answer must contain the correct answer
    - fuzzy: Allow small typos (>90% similarity)
    """
    user_normalized = normalize_answer(user_answer)
    correct_normalized = normalize_answer(correct_answer)
    
    if match_type == "exact":
        return user_normalized == correct_normalized
    
    elif match_type == "contains":
        return correct_normalized in user_normalized
    
    elif match_type == "fuzzy":
        ratio = SequenceMatcher(None, user_normalized, correct_normalized).ratio()
        return ratio >= 0.9
    
    return False


async def submit_quest_answer(
    self,
    user_id: UUID,
    quest_id: str,
    answer: str,
) -> dict:
    """
    Submit and validate a quest answer.
    """
    # Get quest definition
    quest = await self.quest_repo.get_by_id(quest_id)
    if not quest:
        raise NotFoundException("Quest not found")
    
    # Check if already completed
    progress = await self.progress_repo.get_quest_progress(user_id, quest_id)
    if progress and progress.completed:
        raise BadRequestException("Quest already completed")
    
    # Validate answer
    is_correct = check_answer(
        answer,
        quest.correct_answer,
        quest.match_type or "exact",
    )
    
    # Update attempts
    attempts = (progress.attempts if progress else 0) + 1
    await self.progress_repo.update_quest_attempts(user_id, quest_id, attempts)
    
    if not is_correct:
        return {
            "correct": False,
            "questId": quest_id,
            "attempts": attempts,
            "hint": quest.hint if attempts >= 3 else None,
        }
    
    # Award rewards
    new_xp, new_level, leveled_up = await self.game_service.award_xp(
        user_id=user_id,
        amount=quest.xp_reward,
        source_type="quest",
        source_id=quest_id,
    )
    
    item_awarded = None
    if quest.item_reward:
        await self.inventory_repo.add_item(user_id, quest.item_reward)
        item_awarded = await self.item_repo.get_by_id(quest.item_reward)
    
    # Mark quest complete
    await self.progress_repo.complete_quest(user_id, quest_id, answer)
    
    return {
        "correct": True,
        "questId": quest_id,
        "xpAwarded": quest.xp_reward,
        "itemAwarded": item_awarded,
        "newTotalXp": new_xp,
        "leveledUp": leveled_up,
        "currentLevel": new_level,
    }
```

### Quest Types

```python
# Quest type handling

class QuestType(str, Enum):
    MULTIPLE_CHOICE = "multiple-choice"
    TEXT_INPUT = "text-input"
    CALL_TO_ACTION = "call-to-action"


async def validate_quest_answer(quest: Quest, answer: str) -> bool:
    """Validate answer based on quest type."""
    
    if quest.type == QuestType.MULTIPLE_CHOICE:
        # Answer is the selected option ID
        correct_option = next(
            (opt for opt in quest.options if opt.is_correct),
            None
        )
        return answer == correct_option.id
    
    elif quest.type == QuestType.TEXT_INPUT:
        return check_answer(answer, quest.correct_answer, "fuzzy")
    
    elif quest.type == QuestType.CALL_TO_ACTION:
        # Honor system - user confirms they did the action
        return answer.lower() in ("true", "yes", "done", "completed")
    
    return False
```

---

## 4. Content Gating

### Level-Based Gating

```python
# src/services/game_service.py

async def check_level_access(
    self,
    user_id: UUID,
    required_level: int,
) -> dict:
    """Check if user meets level requirement."""
    user = await self.user_repo.get_by_id(user_id)
    
    has_access = user.level >= required_level
    
    return {
        "hasAccess": has_access,
        "gateType": "level",
        "requiredLevel": required_level,
        "currentLevel": user.level,
    }
```

### Item-Based Gating

```python
async def check_item_access(
    self,
    user_id: UUID,
    post_slug: str,
    required_item: str,
    challenge_text: str | None = None,
) -> dict:
    """Check if user can access item-gated content."""
    
    # Check if already unlocked
    progress = await self.progress_repo.get_post_progress(user_id, post_slug)
    if progress and progress.is_unlocked:
        return {
            "hasAccess": True,
            "postSlug": post_slug,
        }
    
    # Check if user has the required item
    has_item = await self.inventory_repo.user_has_item(user_id, required_item)
    
    return {
        "hasAccess": False,
        "postSlug": post_slug,
        "gateType": "item",
        "requiredItem": required_item,
        "hasItem": has_item,
        "canUnlock": has_item,
        "challengeText": challenge_text,
    }


async def use_item_to_unlock(
    self,
    user_id: UUID,
    item_id: str,
    post_slug: str,
) -> dict:
    """Use an item to unlock gated content."""
    
    # Verify user has the item
    has_item = await self.inventory_repo.user_has_item(user_id, item_id)
    if not has_item:
        raise BadRequestException("You don't have this item")
    
    # Check if post is already unlocked
    progress = await self.progress_repo.get_post_progress(user_id, post_slug)
    if progress and progress.is_unlocked:
        raise BadRequestException("Post already unlocked")
    
    # NOTE: Items are NOT consumed - they stay in inventory
    # This allows showing them as trophies
    
    # Mark post as unlocked
    await self.progress_repo.unlock_post(
        user_id=user_id,
        post_slug=post_slug,
        unlocked_with_item=item_id,
    )
    
    return {
        "success": True,
        "postSlug": post_slug,
        "itemUsed": item_id,
        "postUnlocked": True,
    }
```

---

## 5. Daily Rewards & Streaks

### Daily Reward Logic

```python
# src/services/game_service.py

from datetime import datetime, timedelta, timezone

DAILY_REWARDS = [
    {"day": 1, "type": "xp", "value": 5},
    {"day": 2, "type": "xp", "value": 5},
    {"day": 3, "type": "xp", "value": 10},
    {"day": 4, "type": "xp", "value": 10},
    {"day": 5, "type": "xp", "value": 15},
    {"day": 6, "type": "xp", "value": 15},
    {"day": 7, "type": "xp", "value": 25},  # Weekly bonus
]


async def claim_daily_reward(self, user_id: UUID) -> dict:
    """
    Claim daily login reward.
    
    - Can claim once per calendar day (UTC)
    - Streak continues if claimed within 48 hours
    - Streak resets after missing a day
    """
    user = await self.user_repo.get_by_id(user_id)
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Check if already claimed today
    last_reward = await self.reward_repo.get_last_reward(user_id)
    if last_reward and last_reward.claimed_at >= today_start:
        next_claim = today_start + timedelta(days=1)
        raise RateLimitedException(
            detail="Daily reward already claimed",
            code="DAILY_REWARD_CLAIMED",
            next_claim_at=next_claim,
        )
    
    # Calculate streak
    if last_reward:
        yesterday = today_start - timedelta(days=1)
        if last_reward.claimed_at >= yesterday:
            # Continue streak
            streak_day = (last_reward.streak_day % 7) + 1
            new_streak = user.current_streak + 1
        else:
            # Streak broken
            streak_day = 1
            new_streak = 1
    else:
        streak_day = 1
        new_streak = 1
    
    # Get reward for this streak day
    reward = DAILY_REWARDS[streak_day - 1]
    
    # Award reward
    if reward["type"] == "xp":
        await self.award_xp(
            user_id=user_id,
            amount=reward["value"],
            source_type="daily_reward",
            source_id=f"day_{streak_day}",
        )
    elif reward["type"] == "item":
        await self.inventory_repo.add_item(user_id, reward["value"])
    
    # Update user streak
    longest_streak = max(user.longest_streak, new_streak)
    await self.user_repo.update(
        user_id,
        current_streak=new_streak,
        longest_streak=longest_streak,
        last_login_at=now,
    )
    
    # Record the reward
    await self.reward_repo.create(
        user_id=user_id,
        reward_type=reward["type"],
        reward_value=str(reward["value"]),
        streak_day=streak_day,
    )
    
    return {
        "success": True,
        "rewardType": reward["type"],
        "rewardValue": reward["value"],
        "streakDay": streak_day,
        "currentStreak": new_streak,
        "nextClaimAt": today_start + timedelta(days=1),
    }
```

---

## 6. Inventory Management

### Adding Items

```python
# src/repositories/inventory_repository.py

async def add_item(
    self,
    user_id: UUID,
    item_id: str,
) -> InventoryItem:
    """
    Add an item to user's inventory.
    Silently ignores if user already has the item.
    """
    # Check if already has item
    existing = await self.db.execute(
        select(InventoryItem).where(
            InventoryItem.user_id == user_id,
            InventoryItem.item_id == item_id,
        )
    )
    if existing.scalar_one_or_none():
        return existing.scalar_one()  # Return existing
    
    # Add new item
    item = InventoryItem(
        user_id=user_id,
        item_id=item_id,
        acquired_at=datetime.now(timezone.utc),
    )
    self.db.add(item)
    await self.db.flush()
    
    return item


async def user_has_item(self, user_id: UUID, item_id: str) -> bool:
    """Check if user has a specific item."""
    result = await self.db.execute(
        select(InventoryItem).where(
            InventoryItem.user_id == user_id,
            InventoryItem.item_id == item_id,
        )
    )
    return result.scalar_one_or_none() is not None


async def get_user_inventory(self, user_id: UUID) -> list[InventoryItem]:
    """Get all items in user's inventory."""
    result = await self.db.execute(
        select(InventoryItem)
        .where(InventoryItem.user_id == user_id)
        .order_by(InventoryItem.acquired_at.desc())
    )
    return result.scalars().all()
```

---

## 7. Statistics Tracking

### User Statistics

```python
# src/services/stats_service.py

async def get_user_stats(self, user_id: UUID) -> dict:
    """Calculate comprehensive user statistics."""
    
    # Total XP earned (from transaction log)
    total_xp = await self.xp_repo.get_total_earned(user_id)
    
    # Quest statistics
    quest_stats = await self.progress_repo.get_quest_stats(user_id)
    
    # Post statistics
    post_stats = await self.progress_repo.get_post_stats(user_id)
    
    # Inventory count
    inventory_count = await self.inventory_repo.count_items(user_id)
    
    # Streak info
    user = await self.user_repo.get_by_id(user_id)
    
    return {
        "totalXpEarned": total_xp,
        "questsCompleted": quest_stats["completed"],
        "questsAttempted": quest_stats["attempted"],
        "postsRead": post_stats["read"],
        "postsUnlocked": post_stats["unlocked"],
        "itemsCollected": inventory_count,
        "currentStreak": user.current_streak,
        "longestStreak": user.longest_streak,
    }
```

---

## 8. Anti-Cheat Measures

### Request Validation

```python
# Prevent XP manipulation

async def award_read_xp(
    self,
    user_id: UUID,
    post_slug: str,
    xp_amount: int,
) -> dict:
    # Validate XP amount against CMS
    # The frontend sends the XP value, but we should verify it
    # In a more secure system, we'd fetch the post from CMS and use its XP value
    
    MAX_READ_XP = 50  # Reasonable maximum for reading a post
    if xp_amount > MAX_READ_XP:
        raise BadRequestException("Invalid XP amount")
    
    # ... rest of logic
```

### Rate Limiting per Action

```python
# Rate limits prevent rapid XP farming

RATE_LIMITS = {
    "read_post": "30/minute",      # Reading posts
    "submit_quest": "10/minute",   # Quest submissions
    "claim_daily": "1/day",        # Daily reward
}
```

### Audit Logging

```python
# All XP changes are logged for review

async def award_xp(self, ...):
    # ... award logic
    
    # Log for audit
    await self.xp_repo.create_transaction(
        user_id=user_id,
        amount=amount,
        source_type=source_type,
        source_id=source_id,
        balance_before=old_xp,
        balance_after=new_xp,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
```

---

## 9. Leaderboards (Future)

### Global Leaderboard

```python
# Future: Weekly/Monthly leaderboards

async def get_leaderboard(
    self,
    period: str = "all_time",
    limit: int = 100,
) -> list[dict]:
    """Get top users by XP."""
    
    if period == "all_time":
        query = (
            select(User.id, User.username, User.avatar_url, User.xp, User.level)
            .where(User.is_active == True)
            .order_by(User.xp.desc())
            .limit(limit)
        )
    elif period == "weekly":
        week_start = get_week_start()
        query = (
            select(
                User.id,
                User.username,
                func.sum(XpTransaction.amount).label("weekly_xp"),
            )
            .join(XpTransaction)
            .where(XpTransaction.created_at >= week_start)
            .group_by(User.id)
            .order_by(desc("weekly_xp"))
            .limit(limit)
        )
    
    result = await self.db.execute(query)
    return [
        {
            "rank": i + 1,
            "userId": row.id,
            "username": row.username,
            "xp": row.xp or row.weekly_xp,
            "level": row.level,
        }
        for i, row in enumerate(result.all())
    ]
```
