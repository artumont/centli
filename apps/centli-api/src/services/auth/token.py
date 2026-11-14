import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class TokenType(Enum):
    ACCESS = "ACCESS"
    REFRESH = "REFRESH"


class Token(BaseModel):
    token: str
    token_type: TokenType
    expiration: datetime.datetime


class TokenData(BaseModel):
    uuid: UUID
    username: str


def generate_jwt_token(token_data: TokenData, token_type: TokenType, key: str) -> Token:
    pass


def decode_jwt_token(token: str, token_type: TokenType, key: str) -> TokenData:
    pass
