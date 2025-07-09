"""
Runtime configuration (12-factor; env-driven). Single source-of-truth for every
micro-service inside the mono-repo.
"""
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import BaseSettings, Field, model_validator

_ROOT = Path(__file__).resolve().parents[2]  # repo root

class Settings(BaseSettings):
    # --- FastAPI ---
    APP_NAME: str = "AI-Analytics Platform"
    DEBUG: bool = Field(False, alias="DEBUG")
    HOST: str = Field("0.0.0.0", alias="HOST")
    PORT: int = Field(8000, alias="PORT")
    WORKERS: int = Field(4, alias="WORKERS")

    # --- Postgres ---
    DATABASE_URL: str = "postgresql+asyncpg://analytics:analytics@localhost:5432/analytics"
    DB_POOL_SIZE: int = 20

    # --- Redis ---
    REDIS_URL: str = "redis://localhost:6379"

    # --- Security ---
    SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30

    # --- AI ---
    OPENAI_API_KEY: str = "replace-me"
    OPENAI_MODEL: str = "gpt-4o-mini"
    MAX_TOKENS: int = 2048
    TEMPERATURE: float = 0.2

    # --- ETL ---
    MAX_WORKERS: int = 8
    BATCH_SIZE: int = 1000
    CHUNK_SIZE: int = 10_000

    ALLOWED_ORIGINS: List[str] = ["*"]

    # --- misc ---
    LOG_LEVEL: str = "INFO"
    CACHE_TTL: int = 3_600

    @model_validator(mode="after")
    def _check_urls(self):
        if not self.DATABASE_URL.startswith("postgresql"):
            raise ValueError("DATABASE_URL must be a Postgres URL")
        if not self.REDIS_URL.startswith("redis://"):
            raise ValueError("REDIS_URL must start with redis://")
        return self

@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]
