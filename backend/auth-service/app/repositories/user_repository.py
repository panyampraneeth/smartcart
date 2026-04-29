from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """
    Handles all database operations for users.
    No business logic here — only database queries.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, email: str, username: str, hashed_password: str, role: str) -> User:
        """Insert a new user into the database."""
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            role=role,
        )
        self.db.add(user)
        await self.db.flush()  # Get the ID without committing
        await self.db.refresh(user)  # Load the full user from DB
        return user

    async def get_by_email(self, email: str) -> Optional[User]:
        """Find a user by email address."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Find a user by username."""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Find a user by their ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
