"""Dependencies for auth routes."""

from fastapi import Depends, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from src.repos.user import UserRepo
from src.routes.deps import get_db_session
from src.services.auth import AuthService


def get_auth_service(
    request: Request, session: AsyncSession = Depends(get_db_session)
) -> AuthService:
    """Get the auth service."""
    return AuthService(UserRepo(session), request.app.state.config.hmac_secret)
