from .base import BaseModel

# DB Models
from .user import User

models = [User]

__all__ = ["BaseModel", "models"]
