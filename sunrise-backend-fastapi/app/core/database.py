from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from typing import AsyncGenerator

from app.core.config import settings

# Convert sync DATABASE_URL to async
if settings.DATABASE_URL.startswith("sqlite"):
    ASYNC_DATABASE_URL = settings.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
else:
    ASYNC_DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine with connection options for schema
connect_args = {}
if not settings.DATABASE_URL.startswith("sqlite"):
    # Set search_path to sunrise schema for PostgreSQL
    connect_args = {
        "server_settings": {
            "search_path": "sunrise"
        }
    }

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    future=True,
    connect_args=connect_args
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create sync engine for migrations and initial setup
sync_engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

Base = declarative_base()

# Set schema for all tables if using PostgreSQL with custom schema
if not settings.DATABASE_URL.startswith("sqlite"):
    Base.metadata.schema = "sunrise"


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    # Import all models here to ensure they are registered with SQLAlchemy
    from app.models import user, teacher, student, fee, leave, expense

    # Create tables in the sunrise schema
    async with async_engine.begin() as conn:
        # Create schema if it doesn't exist (for PostgreSQL)
        if not settings.DATABASE_URL.startswith("sqlite"):
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS sunrise"))

        await conn.run_sync(Base.metadata.create_all)
