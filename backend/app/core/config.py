from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "ECE AI Studio"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str = "dev_secret_key_change_me_in_production_min_32_chars_long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # DB: Supports SQLite (for instant local standalone testing) and Postgres
    DATABASE_URL: str = "sqlite+aiosqlite:///./ece_studio.db"

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Storage
    STORAGE_DIR: str = str(Path(__file__).resolve().parent.parent.parent / "storage")

    # AI Configurations
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    AI_DEFAULT_PROVIDER: str = "gemini"

    # Octave
    OCTAVE_EXECUTABLE: str = "octave-cli"

    # Quotas
    FREE_EXECUTION_QUOTA: int = 100
    FREE_AI_TOKEN_QUOTA: int = 50000

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

# Ensure local storage directories exist
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_DIR, "artifacts"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_DIR, "reports"), exist_ok=True)
