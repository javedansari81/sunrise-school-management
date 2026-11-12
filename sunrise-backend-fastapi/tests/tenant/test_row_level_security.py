"""
Row-level security (Phase 7): the database itself keeps schools apart, below the
ORM scoping and the raw SQL guard in app/core/tenant.py.

These tests run SQL straight on the connection (exec_driver_sql), which skips
every check in the app, so only the database policy stands between a school
and another school's rows. See conftest.py for how the database is prepared and
rolled back.
"""
import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.core.tenant import tenant_bypass
from app.models.school import School

POLICY = "tenant_isolation"


async def _raw(session, sql: str):
    """Run SQL on the session's connection without any of the app's tenant checks."""
    conn = await session.connection()
    return (await conn.exec_driver_sql(sql)).all()


async def _schools_seen(session, table="users") -> set:
    return {row[0] for row in await _raw(session, f"SELECT DISTINCT school_id FROM {table}")}


async def _sync(session):
    """Any ORM statement brings the connection's RLS settings in line with the session."""
    await session.execute(select(School.id).limit(1))


@pytest.fixture
async def fresh_connection():
    """A new connection with nothing set on it, outside the test transaction."""
    connect_args = {"server_settings": {"search_path": settings.DB_SCHEMA}}
    if settings.DB_SSL:
        connect_args["ssl"] = settings.DB_SSL
    engine = create_async_engine(
        settings.ASYNCPG_DSN.replace("postgresql://", "postgresql+asyncpg://", 1), connect_args=connect_args)
    try:
        async with engine.connect() as conn:
            transaction = await conn.begin()
            yield conn
            await transaction.rollback()
    finally:
        await engine.dispose()


# ---------------------------------------------------------------------------
# The database setup
# ---------------------------------------------------------------------------

async def test_app_role_does_not_skip_row_level_security(connection):
    """A superuser or a BYPASSRLS role skips every policy, which would make the rest of this file pointless."""
    row = (await connection.exec_driver_sql(
        "SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = current_user")).one()
    assert (row.rolsuper, row.rolbypassrls) == (False, False), (
        "The database user is a superuser or has BYPASSRLS: row-level security does not apply to it. "
        "Connect the app (and these tests) as an ordinary role that owns the schema.")


async def test_every_school_owned_table_has_forced_row_level_security(connection):
    rows = (await connection.exec_driver_sql(f"""
        SELECT c.relname, c.relrowsecurity, c.relforcerowsecurity,
               EXISTS (SELECT 1 FROM pg_policies p
                       WHERE p.schemaname = n.nspname AND p.tablename = c.relname AND p.policyname = '{POLICY}')
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        JOIN pg_attribute a ON a.attrelid = c.oid AND a.attname = 'school_id' AND NOT a.attisdropped
        WHERE n.nspname = current_schema() AND c.relkind IN ('r', 'p')
        ORDER BY c.relname""")).all()
    assert len(rows) >= 46  # every school-owned table as of Phase 7
    missing = [r[0] for r in rows if not (r[1] and r[2] and r[3])]
    assert missing == [], (
        f"School-owned tables without forced row-level security: {missing}. "
        "End the migration that adds them with: SELECT enable_tenant_row_level_security();")


# ---------------------------------------------------------------------------
# The policy, straight on a connection
# ---------------------------------------------------------------------------

async def test_connection_without_a_school_sees_and_writes_nothing(fresh_connection, schools):
    conn = fresh_connection
    for table in ("users", "school_settings", "classes", "students", "fee_heads", "payments"):
        assert (await conn.exec_driver_sql(f"SELECT COUNT(*) FROM {table}")).scalar_one() == 0, table
    with pytest.raises(DBAPIError, match="row-level security"):
        async with conn.begin_nested():
            await conn.exec_driver_sql(
                "INSERT INTO school_settings (school_id, key, value) VALUES (1, 'rls.test', 'x')")


async def test_school_setting_shows_only_that_school(fresh_connection):
    conn = fresh_connection
    await conn.exec_driver_sql("SELECT set_config('app.school_id', '1', true)")
    seen = {r[0] for r in (await conn.exec_driver_sql("SELECT DISTINCT school_id FROM classes")).all()}
    assert seen == {1}
    with pytest.raises(DBAPIError, match="row-level security"):
        async with conn.begin_nested():
            # school 1 may not write a row for another school (id 0 never exists; the check comes first)
            await conn.exec_driver_sql(
                "INSERT INTO school_settings (school_id, key, value) VALUES (0, 'rls.test', 'x')")


async def test_bypass_setting_shows_every_school(fresh_connection):
    conn = fresh_connection
    await conn.exec_driver_sql("SELECT set_config('app.bypass_rls', 'on', true)")
    platform_admins = (await conn.exec_driver_sql(
        "SELECT COUNT(*) FROM users WHERE school_id IS NULL")).scalar_one()
    everyone = (await conn.exec_driver_sql("SELECT COUNT(*) FROM users")).scalar_one()
    assert everyone > platform_admins


# ---------------------------------------------------------------------------
# The app's sessions set the policy's settings
# ---------------------------------------------------------------------------

async def test_school_session_reaches_only_its_school_even_past_the_app_checks(make_session, schools):
    for school_id in (schools["sunrise_id"], schools["other_id"]):
        async with make_session(school_id) as session:
            await _sync(session)
            assert await _schools_seen(session) == {school_id}


async def test_school_session_cannot_write_for_another_school_past_the_app_checks(make_session, schools):
    async with make_session(schools["sunrise_id"]) as session:
        await _sync(session)
        with pytest.raises(DBAPIError, match="row-level security"):
            async with session.begin_nested():
                await _raw(session, f"INSERT INTO school_settings (school_id, key, value) "
                                    f"VALUES ({schools['other_id']}, 'rls.test', 'x') RETURNING id")


async def test_flush_runs_under_the_sessions_school(make_session, schools):
    """Writes made by a flush (not by session.execute) also carry the school setting."""
    from app.models.school import SchoolSetting

    async with make_session(schools["other_id"]) as session:
        session.add(SchoolSetting(key="rls.flush_test", value="1"))
        await session.flush()
        assert await _raw(session, "SELECT school_id FROM school_settings WHERE key = 'rls.flush_test'") == [
            (schools["other_id"],)]


async def test_tenant_bypass_opens_and_closes_the_policy(make_session, schools):
    both = {schools["sunrise_id"], schools["other_id"]}
    async with make_session(schools["other_id"]) as session:
        with tenant_bypass(session):
            await _sync(session)
            assert both <= await _schools_seen(session)
        await _sync(session)
        assert await _schools_seen(session) == {schools["other_id"]}


async def test_rolled_back_savepoint_does_not_leave_stale_settings(make_session, schools):
    """Rolling back a savepoint also rolls back settings made inside it; the session sets them again."""
    async with make_session(schools["other_id"]) as session:
        await _sync(session)
        nested = await session.begin_nested()
        with tenant_bypass(session):
            await _sync(session)
        await nested.rollback()
        await _sync(session)
        assert await _schools_seen(session) == {schools["other_id"]}


async def test_platform_session_sees_platform_admins_and_school_sessions_do_not(make_session, schools):
    from app.core.security import get_password_hash
    from app.models.user import PLATFORM_ADMIN_USER_TYPE_ID, User

    async with make_session() as session:
        with tenant_bypass(session):
            session.add(User(school_id=None, email="rls-platform@example-platform.com",
                             password=get_password_hash("Rls-Platform-1"), first_name="R", last_name="LS",
                             user_type_id=PLATFORM_ADMIN_USER_TYPE_ID, is_active=True))
            await session.commit()

    async with make_session(schools["sunrise_id"]) as session:
        await _sync(session)
        assert await _raw(session, "SELECT id FROM users WHERE school_id IS NULL") == []


async def test_raw_sql_guard_and_policy_agree(make_session, schools):
    """The ordinary path (text() with :school_id) still works with the policy on."""
    async with make_session(schools["other_id"]) as session:
        count = (await session.execute(
            text("SELECT COUNT(*) FROM users WHERE school_id = :school_id"))).scalar_one()
        assert count == 2  # the two users the fixture made for the second school
