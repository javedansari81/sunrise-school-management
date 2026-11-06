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
    # asyncpg rejects ?sslmode=..., so the URL without it is used and SSL is passed below
    ASYNC_DATABASE_URL = settings.ASYNCPG_DSN.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create async engine with connection options for schema
connect_args = {}
if not settings.DATABASE_URL.startswith("sqlite"):
    # Every connection only sees this application's schema. This is set per
    # connection, never database-wide, because the database may be shared.
    connect_args = {
        "server_settings": {
            "search_path": settings.DB_SCHEMA
        }
    }
    if settings.DB_SSL:
        connect_args["ssl"] = settings.DB_SSL

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,  # Disable SQL query logging
    future=True,
    connect_args=connect_args
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create sync engine for migrations and initial setup (psycopg2 understands sslmode itself)
sync_engine = create_engine(
    settings.DATABASE_URL,
    connect_args={} if settings.DATABASE_URL.startswith("sqlite") else {"options": f"-csearch_path={settings.DB_SCHEMA}"},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

Base = declarative_base()

# Set schema for all tables if using PostgreSQL with custom schema
if not settings.DATABASE_URL.startswith("sqlite"):
    Base.metadata.schema = settings.DB_SCHEMA


# Register the tenant (school) scoping session events. Imported for its side effect.
import app.core.tenant  # noqa: E402,F401


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

    # Create tables in the application schema
    async with async_engine.begin() as conn:
        # Create schema if it doesn't exist (for PostgreSQL)
        if not settings.DATABASE_URL.startswith("sqlite"):
            await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{settings.DB_SCHEMA}"'))

        await conn.run_sync(Base.metadata.create_all)
