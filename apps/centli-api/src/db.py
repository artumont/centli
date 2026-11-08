from __future__ import annotations

from typing import Self

from sqlalchemy import text
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.sql.expression import Executable


class DatabaseClient:
    """Async database client wrapping a SQLAlchemy async engine.

    Supports both PostgreSQL (``asyncpg``) and SQLite (``aiosqlite``).
    The dialect is inferred from the connection URL.

    Args:
        url: SQLAlchemy async connection string.
        echo: When ``True``, log all SQL statements (default ``False``).
    """

    def __init__(self, url: str, *, echo: bool = False) -> None:
        self._engine: AsyncEngine = create_async_engine(url, echo=echo)
        self._session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
        )

    @property
    def engine(self) -> AsyncEngine:
        """The underlying async engine (read-only)."""
        return self._engine

    def session(self) -> AsyncSession:
        """Create an async database session.

        Caller owns session lifecycle. Use it as an async context manager so
        connections return to engine pool:

        .. code-block:: python

            async with client.session() as session:
                result = await session.execute(statement)

        Returns:
            A new async database session.
        """
        return self._session_factory()

    async def ping(self) -> bool:
        """Check whether the underlying connection is alive.

        Sends a lightweight ``SELECT 1`` probe.

        Returns:
            ``True`` if the server responds, ``False`` on any error.
        """
        try:
            async with self._engine.connect() as conn:
                _ = await conn.execute(text("SELECT 1"))
            return True
        except Exception:  # noqa: BLE001
            return False

    async def close(self) -> None:
        """Dispose the engine and release all pooled connections.

        After calling this method the instance must not be reused.
        """
        await self._engine.dispose()

    async def run(self, stmt: Executable) -> Result[tuple[object, ...]]:
        """Execute a SQLAlchemy executable statement.

        The caller is responsible for consuming returned result; statement
        is *not* committed automatically.

        Args:
            stmt: A SQLAlchemy ``Executable`` (``select``, ``insert``,
                ``update``, ``delete``, ``text``, …) to execute.

        Returns:
            A buffered SQLAlchemy result.
        """
        session = self._session_factory()
        result = await session.execute(stmt)
        return result

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()
