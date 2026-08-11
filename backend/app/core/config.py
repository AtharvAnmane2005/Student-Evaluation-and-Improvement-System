"""
Centralized application configuration.

All values are read from environment variables (or a local .env file in dev).
Never hardcode secrets here — see .env.example for the expected keys.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---
    APP_NAME: str = "PLACER API"
    APP_ENV: str = "development"  # development | staging | production
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # --- Security / JWT ---
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BCRYPT_ROUNDS: int = 12

    # --- Database ---
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "placer_db"

    # --- CORS ---
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # --- Auth cookie ---
    REFRESH_TOKEN_COOKIE_NAME: str = "placer_refresh_token"
    COOKIE_SECURE: bool = False  # MUST be True in production (HTTPS only)
    COOKIE_DOMAIN: str | None = None

    # --- Google OAuth ("Sign in with Google") ---
    GOOGLE_CLIENT_ID: str = ""

    # --- File storage ---
    STORAGE_BACKEND: str = "local"  # local | cloudinary
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    LOCAL_STORAGE_PATH: str = "./storage"
    MAX_RESUME_SIZE_MB: int = 5

    # --- Rate limiting ---
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_AUTH: str = "10/minute"

    # --- ML artifacts (wired in Phase 7) ---
    ML_ARTIFACTS_DIR: str = "./app/ml/matching/artifacts"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — env is read once per process."""
    return Settings()
