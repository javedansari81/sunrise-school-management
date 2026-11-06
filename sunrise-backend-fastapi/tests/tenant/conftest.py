"""
Fixtures for the tenant isolation tests.

These tests need the PostgreSQL database from DATABASE_URL. Each test:

1. opens one connection and starts a transaction,
2. applies Database/Versioning/V036_add_schools_and_tenant_columns.sql inside it,
3. adds a second school with its own users,
4. runs the test with sessions that turn commits into savepoints,
5. rolls everything back, so the database is left exactly as it was.

Run from sunrise-backend-fastapi/:
    python -m pytest tests/tenant -o addopts="" --asyncio-mode=auto
"""
import os
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

BACKEND_DIR = Path(__file__).resolve().parents[2]
REPO_DIR = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import main  # noqa: E402,F401  (loads every model so relationships resolve)
from app.core.config import settings  # noqa: E402
from app.core.security import get_password_hash  # noqa: E402
from app.core.tenant import set_session_school, tenant_bypass  # noqa: E402
from app.models.school import School  # noqa: E402
from app.models.user import User  # noqa: E402

MIGRATION = REPO_DIR / "Database" / "Versioning" / "V036_add_schools_and_tenant_columns.sql"

OTHER_SCHOOL_CODE = "oakridge"
TEST_PASSWORD = "Tenant-Test-Pass-1"
ADMIN_USER_TYPE_ID = 1


def _migration_body() -> str:
    # The file manages its own transaction. Inside the test transaction we drop
    # those statements so the rollback at the end also undoes the migration.
    lines = MIGRATION.read_text(encoding="utf-8").splitlines()
    return "\n".join(line for line in lines if line.strip().upper() not in ("BEGIN;", "COMMIT;"))


if not settings.DATABASE_URL.startswith("postgresql"):
    pytest.skip("Tenant tests need PostgreSQL (DATABASE_URL)", allow_module_level=True)


@pytest_asyncio.fixture
async def connection():
    engine = create_async_engine(
        settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        connect_args={"server_settings": {"search_path": "sunrise"}},
    )
    async with engine.connect() as conn:
        transaction = await conn.begin()
        await conn.execute(text("SELECT 1"))  # make sure the transaction is open on the server
        raw = await conn.get_raw_connection()
        await raw.driver_connection.execute(_migration_body())
        try:
            yield conn
        finally:
            await transaction.rollback()
    await engine.dispose()


@pytest.fixture
def make_session(connection):
    """Factory for sessions on the test connection. Commits become savepoints."""

    def _make(school_id=None) -> AsyncSession:
        session = AsyncSession(
            bind=connection, expire_on_commit=False, join_transaction_mode="create_savepoint"
        )
        if school_id is not None:
            set_session_school(session, school_id)
        return session

    return _make


@pytest_asyncio.fixture
async def schools(make_session):
    """School 1 (Sunrise, from the migration) and a second school with two users."""
    session = make_session()
    with tenant_bypass(session):
        sunrise = await session.get(School, 1)
        oakridge = School(code=OTHER_SCHOOL_CODE, name="Oakridge Public School")
        session.add(oakridge)
        await session.flush()

        # One user whose email also exists in Sunrise, to prove per-school uniqueness
        sunrise_user = (
            await session.execute(
                text("SELECT id, email FROM users WHERE school_id = 1 AND (is_deleted IS NOT TRUE) ORDER BY id LIMIT 1")
            )
        ).one()
        password_hash = get_password_hash(TEST_PASSWORD)
        shared = User(
            school_id=oakridge.id, email=sunrise_user.email, password=password_hash,
            first_name="Shared", last_name="Email", user_type_id=ADMIN_USER_TYPE_ID, is_active=True,
        )
        admin = User(
            school_id=oakridge.id, email="admin@oakridgeschool.in", password=password_hash,
            first_name="Oak", last_name="Admin", user_type_id=ADMIN_USER_TYPE_ID, is_active=True,
        )
        session.add_all([shared, admin])
        await session.commit()

    data = {
        "sunrise_id": sunrise.id,
        "sunrise_code": sunrise.code,
        "other_id": oakridge.id,
        "other_code": oakridge.code,
        "shared_email": sunrise_user.email,
        "sunrise_user_id": sunrise_user.id,
        "other_admin_id": admin.id,
        "other_admin_email": admin.email,
    }
    await session.close()
    return data
