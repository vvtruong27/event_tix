"""Database client and session initialization.

This module exposes:
- an async SQLAlchemy session dependency for relational data,
- a MongoDB client for document-style data,
- a Redis client for cache/ephemeral state.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
from app.core.config import settings

# Create async SQLAlchemy engine for PostgreSQL-backed entities.
engine = create_async_engine(settings.POSTGRES_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db():
    """Yield one SQLAlchemy AsyncSession per request lifecycle."""
    async with AsyncSessionLocal() as session:
        yield session

# Global MongoDB client for collections used outside relational workflows.
mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
mongo_db = mongo_client[settings.MONGO_DB_NAME]

# Redis client configured for text responses (instead of raw bytes).
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)