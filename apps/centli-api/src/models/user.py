from sqlmodel import Field

from src.models import BaseModel


class User(BaseModel):
    username: str
    password: str

    is_admin: bool = Field(default=False)
