"""
Application configurations
"""

import os
import secrets
from typing import Annotated, Any, Literal

from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

from pydantic import (
    AnyUrl,
    PostgresDsn,
    BeforeValidator,
    computed_field,
)


def parse_cors(v: Any) -> list[str] | str:
    """utility to parse cors origins"""
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


def expand_tilde(path):
    """expands the tilde (~) in a path to the user's home directory"""
    if path.startswith("~"):
        return os.path.expanduser(path)

    return path


class Settings(BaseSettings):
    """project settings"""

    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = (
        []
    )

    UPLOAD_TARGET: str = expand_tilde("~/uploads/")
    MODEL_TARGET: str = expand_tilde("~/models/")

    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS]

    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


settings = Settings()
