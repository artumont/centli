"""Common dependencies for routes."""

from typing import Any

from fastapi import HTTPException, Request


def get_db(request: Request) -> Any:
    """FastAPI dependency: get DatabaseClient from app lifespan.

    Returns:
        The configured DatabaseClient.

    Raises:
        HTTPException: 503 if the database is not configured.
    """
    db = getattr(request.app, "db", None)
    if db is None:
        raise HTTPException(status_code=503, detail="Database is not configured")
    return db


__all__ = [
    "get_db",
]
