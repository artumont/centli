from uuid import UUID

from sqlmodel import SQLModel


class EntryNotFound(Exception):
    def __init__(self, uuid: UUID, model: type[SQLModel]) -> None:
        super().__init__(f"{model} with id {uuid} not found.")
