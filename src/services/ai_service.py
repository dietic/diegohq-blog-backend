"""
AI service for code quest review.

Uses OpenAI API to evaluate user code submissions against quest criteria.
"""

import logging

from openai import AsyncOpenAI

from src.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered code review."""

    def __init__(self) -> None:
        """Initialize the AI service."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def review_code(
        self,
        code: str,
        language: str,
        quest_prompt: str,
        ai_criteria: str,
    ) -> tuple[bool, str]:
        """
        Review user-submitted code against quest criteria.

        Args:
            code: The user's submitted code.
            language: The programming language.
            quest_prompt: The quest prompt/question.
            ai_criteria: The AI review criteria.

        Returns:
            Tuple of (passed: bool, feedback: str).
        """
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured")
            return False, "Code review is not available. Please configure OpenAI API key."

        system_prompt = """You are a code reviewer for a gamified programming blog.
Your job is to evaluate user code submissions against specific criteria.

IMPORTANT RULES:
1. Be encouraging but honest
2. Focus on whether the code meets the criteria, not perfection
3. If the code mostly works but has minor issues, pass it with suggestions
4. Only fail if the code fundamentally doesn't meet the criteria
5. Keep feedback concise (2-3 sentences max)
6. Don't be overly strict - this is for learning

Response format:
- Start with "PASS" or "FAIL" on the first line
- Then provide brief, helpful feedback"""

        user_prompt = f"""Quest: {quest_prompt}

Criteria to evaluate:
{ai_criteria}

Language: {language}

User's submitted code:
```{language}
{code}
```

Evaluate if this code meets the criteria. Be lenient - if it shows understanding of the concept and mostly works, pass it."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=300,
                temperature=0.3,
            )

            content = response.choices[0].message.content or ""

            # Parse response
            lines = content.strip().split("\n", 1)
            first_line = lines[0].upper().strip()

            passed = first_line.startswith("PASS")
            feedback = lines[1].strip() if len(lines) > 1 else content

            return passed, feedback

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return False, "An error occurred during code review. Please try again."


# Singleton instance
_ai_service: AIService | None = None


def get_ai_service() -> AIService:
    """Get the AI service singleton instance."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
