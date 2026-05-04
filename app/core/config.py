"""Application configuration loader."""

import os
from dotenv import load_dotenv

# Populate environment values from .env when present.
load_dotenv()

class Settings:
    """Strongly-typed settings object used by infrastructure modules."""

    # Databases
    POSTGRES_URL: str = os.getenv("POSTGRES_URL")
    MONGO_URL: str = os.getenv("MONGO_URL")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "eventtix_db")
    REDIS_URL: str = os.getenv("REDIS_URL")

    # Security & JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fallback-secret-if-env-fails")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Single shared settings instance imported throughout the app.
settings = Settings()