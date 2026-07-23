"""
Runtime configuration (12-factor; env-driven). Single source-of-truth for every
micro-service inside the mono-repo.
"""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

_ROOT = Path(__file__).resolve().parents[2]  # repo root


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    # --- FastAPI ---
    APP_NAME: str = "AI-Analytics Platform"
    DEBUG: bool = Field(default=False)
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    WORKERS: int = Field(default=4)

    # --- Postgres ---
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://analytics:analytics@localhost:5432/analytics"
    )
    DB_POOL_SIZE: int = Field(default=20)

    # --- Redis ---
    REDIS_URL: str = Field(default="redis://localhost:6379")

    # --- Security ---
    SECRET_KEY: str = Field(default="change-me-in-production")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRE_MINUTES: int = Field(default=30)

    # --- AI ---
    OPENAI_API_KEY: str = Field(default="replace-me")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini")
    MAX_TOKENS: int = Field(default=2048)
    TEMPERATURE: float = Field(default=0.2)

    # --- ETL ---
    MAX_WORKERS: int = Field(default=8)
    BATCH_SIZE: int = Field(default=1000)
    CHUNK_SIZE: int = Field(default=10_000)

    ALLOWED_ORIGINS: List[str] = Field(default=["*"])

    # --- misc ---
    LOG_LEVEL: str = Field(default="INFO")
    CACHE_TTL: int = Field(default=3_600)

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith("postgresql"):
            raise ValueError("DATABASE_URL must be a Postgres URL")
        return v

    @field_validator("REDIS_URL")
    @classmethod
    def validate_redis_url(cls, v: str) -> str:
        if not v.startswith("redis://"):
            raise ValueError("REDIS_URL must start with redis://")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
