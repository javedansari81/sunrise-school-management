"""
Tenant isolation tests: one school can never read or change another school's rows.
See conftest.py for how the database is prepared and rolled back.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.school_resolver import school_code_from_host
from app.core.security import create_access_token
from app.core.tenant import TenantContextError, set_session_school
from app.models.metadata import Class
from app.models.student import Student
from app.models.user import User

from .conftest import TEST_PASSWORD


# ---------------------------------------------------------------------------
# ORM scoping
# ---------------------------------------------------------------------------

async def test_select_returns_only_current_school_rows(make_session, schools):
    async with make_session(schools["other_id"]) as session:
        emails = set((await session.execute(select(User.email))).scalars())
        assert emails == {schools["shared_email"], schools["other_admin_email"]}

    async with make_session(schools["sunrise_id"]) as session:
        users = (await session.execute(select(User))).scalars().all()
        assert users and all(u.school_id == schools["sunrise_id"] for u in users)
        assert schools["other_admin_id"] not in {u.id for u in users}


async def test_same_email_resolves_to_each_schools_own_user(make_session, schools):
    for school_id in (schools["sunrise_id"], schools["other_id"]):
        async with make_session(school_id) as session:
            user = (
                await session.execute(select(User).where(User.email == schools["shared_email"]))
            ).scalar_one()
            assert user.school_id == school_id


async def test_get_by_primary_key_of_other_school_returns_none(make_session, schools):
    async with make_session(schools["sunrise_id"]) as session:
        assert await session.get(User, schools["other_admin_id"]) is None
    async with make_session(schools["other_id"]) as session:
        assert await session.get(User, schools["sunrise_user_id"]) is None


async def test_aggregates_and_joins_are_scoped(make_session, schools):
    async with make_session(schools["other_id"]) as session:
        assert (await session.execute(select(func.count()).select_from(Class))).scalar_one() == 0
        joined = await session.execute(select(Student).join(Class, Student.class_id == Class.id))
        assert joined.scalars().all() == []

    async with make_session(schools["sunrise_id"]) as session:
        assert (await session.execute(select(func.count()).select_from(Class))).scalar_one() > 0


async def test_relationship_loads_are_scoped(make_session, schools):
    async with make_session(schools["sunrise_id"]) as session:
        classes = (
            await session.execute(select(Class).options(selectinload(Class.students)))
        ).scalars().all()
        for cls in classes:
            assert all(s.school_id == schools["sunrise_id"] for s in cls.students)


async def test_orm_update_only_touches_current_school(make_session, schools):
    async with make_session(schools["other_id"]) as session:
        result = await session.execute(
            update(User).where(User.email == schools["shared_email"]).values(first_name="Changed")
        )
        assert result.rowcount == 1
        await session.commit()

    async with make_session(schools["sunrise_id"]) as session:
        user = (
            await session.execute(select(User).where(User.email == schools["shared_email"]))
        ).scalar_one()
        assert user.first_name != "Changed"


# ---------------------------------------------------------------------------
# Writes
# ---------------------------------------------------------------------------

async def test_new_rows_are_stamped_with_current_school(make_session, schools):
    async with make_session(schools["other_id"]) as session:
        cls = Class(name="Grade 1", description="Grade 1", sort_order=1)
        session.add(cls)
        await session.commit()
        assert cls.school_id == schools["other_id"]


async def test_class_names_are_unique_per_school_not_globally(make_session, schools):
    async with make_session(schools["sunrise_id"]) as session:
        existing_name = (await session.execute(select(Class.name).limit(1))).scalar_one()

    async with make_session(schools["other_id"]) as session:
        session.add(Class(name=existing_name, description="Same name, other school"))
        await session.commit()  # allowed in a different school

        session.add(Class(name=existing_name, description="Duplicate in the same school"))
        with pytest.raises(IntegrityError):
            await session.commit()
        await session.rollback()


async def test_user_email_is_unique_within_a_school(make_session, schools):
    async with make_session(schools["other_id"]) as session:
        session.add(User(
            email=schools["other_admin_email"], password="x", first_name="Dup", last_name="User",
            user_type_id=1, is_active=True,
        ))
        with pytest.raises(IntegrityError):
            await session.commit()
        await session.rollback()


async def test_creating_a_row_for_another_school_is_refused(make_session, schools):
    async with make_session(schools["sunrise_id"]) as session:
        session.add(Class(school_id=schools["other_id"], name="Sneaky", description="x"))
        with pytest.raises(TenantContextError):
            await session.flush()
        await session.rollback()


async def test_session_cannot_be_rebound_to_another_school(make_session, schools):
    session = make_session(schools["sunrise_id"])
    with pytest.raises(TenantContextError):
        set_session_school(session, schools["other_id"])
    await session.close()


# ---------------------------------------------------------------------------
# Fail closed
# ---------------------------------------------------------------------------

async def test_query_without_school_context_is_refused(make_session, schools):
    async with make_session() as session:
        with pytest.raises(TenantContextError):
            await session.execute(select(User))


async def test_write_without_school_context_is_refused(make_session, schools):
    async with make_session() as session:
        session.add(Class(name="Orphan", description="x"))
        with pytest.raises(TenantContextError):
            await session.flush()
        await session.rollback()


# ---------------------------------------------------------------------------
# API: login and tokens
# ---------------------------------------------------------------------------

async def _login(client, email):
    return await client.post("/api/v1/auth/login-json", json={"email": email, "password": TEST_PASSWORD})


async def test_login_is_scoped_to_the_requested_school(client_factory, schools):
    async with client_factory(schools["other_code"]) as client:
        response = await _login(client, schools["other_admin_email"])
        assert response.status_code == 200, response.text
        token = response.json()["access_token"]

        me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200, me.text
        assert me.json()["email"] == schools["other_admin_email"]

    # The same credentials do not exist in Sunrise
    async with client_factory(schools["sunrise_code"]) as client:
        response = await _login(client, schools["other_admin_email"])
        assert response.status_code == 401


async def test_token_is_rejected_on_another_schools_subdomain(client_factory, schools):
    async with client_factory(schools["other_code"]) as client:
        token = (await _login(client, schools["other_admin_email"])).json()["access_token"]

    async with client_factory(schools["sunrise_code"]) as client:
        response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401


async def test_token_without_school_claim_is_rejected(client_factory, schools):
    from datetime import datetime, timedelta

    from jose import jwt

    from app.core.config import settings

    legacy = jwt.encode(
        {"sub": str(schools["sunrise_user_id"]), "exp": datetime.utcnow() + timedelta(minutes=5)},
        settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM,
    )
    async with client_factory(schools["sunrise_code"]) as client:
        response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {legacy}"})
        assert response.status_code == 401


async def test_token_for_another_schools_user_id_finds_nothing(client_factory, schools):
    # A token claiming school 1 but carrying a user id from the other school
    forged = create_access_token(schools["other_admin_id"], school_id=schools["sunrise_id"])
    async with client_factory(schools["sunrise_code"]) as client:
        response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {forged}"})
        assert response.status_code in (401, 404)


async def test_unknown_school_code_is_rejected(client_factory, schools):
    async with client_factory("no-such-school") as client:
        response = await _login(client, schools["other_admin_email"])
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Subdomain parsing
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "host, expected",
    [
        ("sunrise.myschools.in", "sunrise"),
        ("Sunrise.MySchools.in:443", "sunrise"),
        ("oak-ridge.myschools.in", "oak-ridge"),
        ("api.myschools.in", None),          # reserved label
        ("www.myschools.in", None),          # reserved label
        ("myschools.in", None),              # the bare domain names no school
        ("a.b.myschools.in", None),          # only one label under the base domain
        ("sunrise.otherdomain.in", None),    # not our domain
        ("evilmyschools.in", None),          # suffix match must respect the dot
        ("localhost:8000", None),
        (None, None),
    ],
)
def test_school_code_from_host(host, expected):
    assert school_code_from_host(host, base_domain="myschools.in") == expected
