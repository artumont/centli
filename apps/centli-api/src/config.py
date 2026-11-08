from functools import lru_cache
from typing import ClassVar
from urllib.parse import quote

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Api configuration (env vars)."""

    host: str = "127.0.0.1"
    port: int = 80
    slow_request_ms: int = 1000

    _database_host: str = "postgres"
    _database_port: int = 5432
    _database_name: str = "centil-db"
    _database_role: str = "centil-api"
    _database_password: str = ""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        case_sensitive=False, env_file=(".env", ".env.dev"), extra="ignore"
    )

    @property
    def database_url(self) -> str:
        if not self._database_password:
            return ""
        return (
            f"postgresql+asyncpg://{self._database_role}:{quote(self._database_password, safe='')}"
            f"@{self._database_host}:{self._database_port}/{self._database_name}"
        )


@lru_cache
def get_config() -> Config:
    """Get the environment config.

    Returns:
        Config: Environment config object.
    """
    return Config()
