from typing import Any
from uuid import UUID

from sqlmodel import col, delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models import BaseModel
from src.repos.errors import EntryNotFound


class BaseRepo[ModelType: BaseModel]:
    repo_model: type[ModelType]

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def get_by_id(self, uuid: UUID) -> ModelType | None:
        """Read primitive.

        Fine for most services, no real restriction on use.

        Args:
            uuid (UUID): Model entry id.

        Returns:
            The entry model or None if not found.
        """
        stmt = select(self.repo_model).where(col(self.repo_model.id) == uuid)
        result = await self.db_session.exec(stmt)
        return result.first()

    async def create(self, model: ModelType) -> None:
        """Create primitive, avoid using inside services.

        Args:
            model (ModelType): Model entry for the table.
        """
        self.db_session.add(model)
        await self.db_session.flush()

    async def update(self, uuid: UUID, fields: dict[str, Any]) -> ModelType:
        """Update primitive avoid using in services.

        Args:
            uuid (UUID): Entry id for the update.
            fields (dict[str, Any]): Fields to change in a dict.

        Raises:
            EntryNotFound: If the entry is not found we throw this along with a message.

        Returns:
            The modified entry model.
        """
        instance = await self.get_by_id(uuid)
        if not instance:
            raise EntryNotFound(uuid, self.repo_model)
        instance.sqlmodel_update(fields)
        self.db_session.add(instance)
        await self.db_session.flush()
        return instance

    async def delete(self, uuid: UUID) -> None:
        """Delete primitive.

        Its ok to use it in services but try to avoid it since
        it doesnt have cascade. Always prefer to use your own method
        with cascade over this primitive.

        Args:
            uuid (UUID): The entry id to delete.
        """
        stmt = delete(self.repo_model).where(col(self.repo_model.id) == uuid)
        await self.db_session.exec(stmt)


__all__ = ["BaseRepo"]
