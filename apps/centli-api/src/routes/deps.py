"""Common dependencies for routes."""

from typing import Any, AsyncGenerator

from fastapi import Depends, HTTPException, Request, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db import DatabaseClient
from src.models.user import User


def get_db(request: Request) -> Any:
    """Get the database client from the lifespan. Raises 503 if its None."""
    db = getattr(request.app, "db", None)
    if db is None:
        raise HTTPException(status_code=503, detail="Database is not configured")
    return db


async def get_db_session(
    db: DatabaseClient = Depends(get_db),
) -> AsyncGenerator[AsyncSession]:
    """Get an async db session for transactions."""
    async with db.session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_identity(request: Request) -> User | None:
    """Get the caller identity, or None. Never raises."""
    return request.state.identity


async def require_auth(
    identity: User | None = Depends(get_identity),
) -> User:
    """Ensure the caller is authenticated. Raises 401 otherwise."""
    if identity is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return identity


__all__ = [
    "get_db",
    "get_identity",
    "require_auth",
]
