import asyncio
from uuid import UUID

import bcrypt
from sqlmodel import select

from src.models.user import User
from src.repos import BaseRepo


class UserRepo(BaseRepo[User]):
    """Repo for the `User` table."""

    async def add_user(self, username: str, password: str) -> None:
        """Add user to the database.

        No direct validation is done here, any validation
        for usernames or passwords should be done in the
        service / controller.
        """
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = await asyncio.to_thread(bcrypt.hashpw, password_bytes, salt)
        model = User(username=username, password=hashed_password.decode("utf-8"))
        await self.create(model)

    async def make_admin(self, id: UUID) -> None:
        """Give a user the admin flag."""
        await self.update(id, {"is_admin": True})

    async def get_by_username(self, username: str) -> User | None:
        """Get a user by its username."""
        stmt = select(self.repo_model).where(User.username == username)
        result = await self.db_session.exec(stmt)
        return result.first()
