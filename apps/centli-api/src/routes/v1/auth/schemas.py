from pydantic import BaseModel


class NewSession(BaseModel):
    """Communication schema used in `/auth/login`."""

    username: str
    password: str
