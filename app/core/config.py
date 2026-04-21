"""Application configuration loader.

Environment variables are loaded from system environment first and optionally
from a local .env file for development convenience.
"""

import os
from dotenv import load_dotenv

# Populate environment values from .env when present.
load_dotenv()


class Settings:
    """Strongly-typed settings object used by infrastructure modules."""

    # Async SQLAlchemy DSN using the asyncpg driver.
    POSTGRES_URL: str = os.getenv("POSTGRES_URL", "postgresql+asyncpg://user:password@localhost:5432/eventtix_db")

    # MongoDB connection and target database name.
    MONGO_URL: str = os.getenv("MONGO_URL", "mongodb://admin:password@localhost:27017")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "eventtix_db")

    # Redis URL for cache, rate-limits, queues, or short-lived state.
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")


# Single shared settings instance imported throughout the app.
settings = Settings()