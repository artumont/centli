import asyncio
from typing import cast
from uuid import UUID

import bcrypt

from src.db import DatabaseClient
from src.models.user import User
from src.repos import user
from src.repos.user import UserRepo
from src.services.auth.errors import IncorrectPassword, InvalidToken, UserNotFound
from src.services.auth.token import TokenType, decode_jwt_token, generate_jwt_token

_DUMMY_HASH = bcrypt.hashpw(b"dummy", bcrypt.gensalt())


class AuthService:
    """_summary_

    Attributes:
        user_repo: _description_
        signing_secret: _description_
        _access_token_ttl: _description_
        _refresh_token_ttl: _description_

    """

    def __init__(
        self,
        user_repo: UserRepo,
        signing_secret: str,
        *,
        access_token_ttl: int = 3600,
        refresh_token_ttl: int = 604800,
    ) -> None:
        self.user_repo = user_repo
        self.signing_secret = signing_secret
        self._access_token_ttl = access_token_ttl
        self._refresh_token_ttl = refresh_token_ttl

    async def get_user_from_token(self, token: str) -> User | None:
        """Decode a token to get the id assigned.

        Args:
            token (str): JWT Token can be refresh or access.

        Raises:
            InvalidToken: Token is either expired or not valid.

        Returns:
            User | None: Returns a user if found else None.

        """
        claims = decode_jwt_token(self.signing_secret, token)
        user_id = claims.get("sub")
        if user_id is None:
            raise InvalidToken(token)
        return await self.user_repo.get_by_id(UUID(str(user_id)))

    async def generate_session(
        self, username: str, password: str
    ) -> dict[TokenType, str]:
        """Generate a jwt token session.

        Args:
            username (str): Username of the account.
            password (str): Password of the account.

        Raises:
            UserNotFound: User with the username wasnt found.
            IncorrectPassword: The provided password is incorrect.

        Returns:
            dict[TokenType, str]: Dict with access and refresh token.

        """
        possible_user = await self.user_repo.get_by_username(username)
        if possible_user is None:
            bcrypt.checkpw(b"dummy", _DUMMY_HASH)
            raise UserNotFound(username)

        password_check = await asyncio.to_thread(
            bcrypt.checkpw,
            password.encode("utf-8"),
            possible_user.password.encode("utf-8"),
        )
        if password_check is False:
            raise IncorrectPassword(possible_user.id)

        user_id = possible_user.id
        return {
            TokenType.ACCESS: generate_jwt_token(
                self.signing_secret,
                str(user_id),
                self._access_token_ttl,
                token_type=TokenType.ACCESS,
            ),
            TokenType.REFRESH: generate_jwt_token(
                self.signing_secret,
                str(user_id),
                self._refresh_token_ttl,
                token_type=TokenType.REFRESH,
            ),
        }


__all__ = ["AuthService"]
