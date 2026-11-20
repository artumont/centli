from typing import Any
from uuid import UUID

from sqlmodel import col, delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models import BaseModel
from src.repos.errors import EntryNotFound


class BaseRepo[ModelType: BaseModel]:
    """Base repo for all SQLModels."""

    repo_model: type[ModelType]

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session: AsyncSession = db_session

    async def get_by_id(self, id: UUID) -> ModelType | None:
        """Read primitive.

        Fine for most services, no real restriction on use.

        Args:
            id (UUID): Model entry id.

        Returns:
            The entry model or None if not found.

        """
        stmt = select(self.repo_model).where(col(self.repo_model.id) == id)
        result = await self.db_session.exec(stmt)
        return result.first()

    async def get_list(self, offset: int = 0, *, limit: int = 100) -> list[ModelType]:
        """Get a list of users starting at an offset orderd by id.

        Args:
            offset (int): The offset for the lookup. Defaults to 0.
            limit (int): The list size limit. Defaults to 100.

        Returns:
            list[User]: A list of users ordered by id.

        """
        stmt = (
            select(self.repo_model)
            .order_by(col(self.repo_model.id))
            .offset(offset)
            .limit(limit)
        )
        result = await self.db_session.exec(stmt)
        return list(result.all())

    async def create(self, model: ModelType) -> None:
        """Create primitive, avoid using inside services.

        Args:
            model (ModelType): Model entry for the table.

        """
        self.db_session.add(model)
        await self.db_session.flush()

    async def update(self, id: UUID, fields: dict[str, Any]) -> ModelType:
        """Update primitive avoid using in services.

        Args:
            id (UUID): Entry id for the update.
            fields (dict[str, Any]): Fields to change in a dict.

        Raises:
            EntryNotFound: If the entry is not found we throw this along with a message.

        Returns:
            The modified entry model.

        """
        instance = await self.get_by_id(id)
        if not instance:
            raise EntryNotFound(id, self.repo_model)
        instance.sqlmodel_update(fields)
        self.db_session.add(instance)
        await self.db_session.flush()
        return instance

    async def delete(self, id: UUID) -> None:
        """Delete primitive.

        Its ok to use it in services but try to avoid it since
        it doesnt have cascade. Always prefer to use your own method
        with cascade over this primitive.

        Args:
            id (UUID): The entry id to delete.

        """
        stmt = delete(self.repo_model).where(col(self.repo_model.id) == id)
        await self.db_session.exec(stmt)
