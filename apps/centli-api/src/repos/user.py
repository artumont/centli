from uuid import UUID

import bcrypt

from src.models.user import User
from src.repos import BaseRepo


class UserRepo(BaseRepo[User]):
    async def add_user(self, username: str, password: str) -> None:
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        model = User(username=username, password=hashed_password.decode("utf-8"))
        await self.create(model)

    async def make_admin(self, uuid: UUID) -> None:
        await self.update(uuid, {"is_admin": True})
