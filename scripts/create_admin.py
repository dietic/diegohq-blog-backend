#!/usr/bin/env python3
"""
Script to create an admin user in the database.

Usage:
    python scripts/create_admin.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.core.security import hash_password
from src.models.user import User


async def create_admin_user(
    email: str,
    username: str,
    password: str,
) -> None:
    """Create an admin user in the database."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if user already exists
        result = await session.execute(
            select(User).where((User.email == email) | (User.username == username))
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"User with email '{email}' or username '{username}' already exists.")
            if existing_user.role != "admin":
                existing_user.role = "admin"
                await session.commit()
                print(f"Updated user '{existing_user.username}' to admin role.")
            else:
                print(f"User '{existing_user.username}' is already an admin.")
            return

        # Create new admin user
        admin_user = User(
            email=email,
            username=username,
            password_hash=hash_password(password),
            role="admin",
            is_active=True,
            xp=0,
            level=1,
            current_streak=0,
            longest_streak=0,
        )

        session.add(admin_user)
        await session.commit()
        print(f"Admin user '{username}' created successfully!")
        print(f"  Email: {email}")
        print(f"  Role: admin")

    await engine.dispose()


def main() -> None:
    """Main entry point."""
    # Default admin credentials - change these!
    email = "admin@diegohq.com"
    username = "admin"
    password = "admin123"  # Change this in production!

    print("Creating admin user...")
    print("-" * 40)

    asyncio.run(create_admin_user(email, username, password))

    print("-" * 40)
    print("Done! You can now log in with:")
    print(f"  Email: {email}")
    print(f"  Password: {password}")


if __name__ == "__main__":
    main()
