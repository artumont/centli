from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel, UTCDateTime
from uuid6 import uuid7

from src.models.user import User
from src.utils import utc_now


class BaseModel(SQLModel):
    """SQL table base for all other models.

    We use uuidv7 for ids because it explicitly contains a
    timstamp which allows us to filter like we do with normal
    integer ids.
    """

    id: UUID = Field(
        default_factory=uuid7,
        primary_key=True,
        index=True,
        nullable=False,
    )

    created_at: datetime = Field(
        default_factory=utc_now,
        sa_type=UTCDateTime,
        nullable=False,
    )

    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_type=UTCDateTime,
        sa_column_kwargs={"onupdate": utc_now},
        nullable=False,
    )


models = [User]

__all__ = ["BaseModel", "models"]
