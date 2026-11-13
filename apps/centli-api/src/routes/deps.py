"""Common dependencies for routes."""

import importlib
from typing import Any

from fastapi import HTTPException

_app_main: Any = None


def get_app_main() -> Any:
    """Lazy import of src.__main__ to avoid circular imports.

    Returns:
        The imported application module.
    """
    global _app_main
    if _app_main is None:
        _app_main = importlib.import_module("src.__main__")
    return _app_main


def get_db() -> Any:
    """FastAPI dependency: get DatabaseClient from app lifespan.

    Returns:
        The configured DatabaseClient.

    Raises:
        HTTPException: 503 if the database is not configured.
    """
    app = get_app_main()
    db = getattr(app, "db", None)
    if db is None:
        raise HTTPException(status_code=503, detail="Database is not configured")
    return db


__all__ = [
    "get_app_main",
    "get_db",
]
