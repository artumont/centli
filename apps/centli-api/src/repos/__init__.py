from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models import BaseModel


class BaseRepo[ModelType: BaseModel]:
    model: type[ModelType]

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def get_by_id(self, uuid: UUID) -> ModelType | None:
        stmt = select(self.model).where(self.model.id == uuid)
        result = await self.db_session.exec(stmt)
        return result.first()


__all__ = ["BaseRepo"]
