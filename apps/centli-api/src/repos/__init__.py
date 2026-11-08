from typing import TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepo[ModelType: BaseModel]:
    model: type[ModelType]

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def get_by_id(self, uuid: UUID) -> ModelType | None:
        raise NotImplementedError()


__all__ = ["BaseRepo"]
