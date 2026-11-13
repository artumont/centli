from functools import lru_cache
from typing import ClassVar
from urllib.parse import quote

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Api configuration (env vars)."""

    host: str = "127.0.0.1"
    port: int = 80
    slow_request_ms: int = 1000

    vault_path: str = "/data/secrets.vault"
    master_key_file: str = "/run/secrets/vault_master_key"

    database_host: str = "postgres"
    database_port: int = 5432
    database_name: str = "centil-db"
    database_role: str = "centil-api"
    database_password: str = ""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        case_sensitive=False, env_file=(".env", ".env.dev"), extra="ignore"
    )

    @property
    def database_url(self) -> str:
        if not self.database_password:
            return ""
        return (
            f"postgresql+asyncpg://{self.database_role}:{quote(self.database_password, safe='')}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )


@lru_cache
def get_config() -> Config:
    """Get the environment config.

    Returns:
        Config: Environment config object.
    """
    return Config()
