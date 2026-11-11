"""
Fixtures for the unified fee module tests.

Reuses the tenant fixtures (one rolled-back transaction per test, school 1
Sunrise plus a second school "oakridge"). Needs a schema with migration V002.

Run from sunrise-backend-fastapi/:
    PYTHONIOENCODING=utf-8 python -m pytest tests -o addopts="" --asyncio-mode=auto
(UTF-8 output: main.py prints emoji, which the Windows console code page cannot encode.)
"""
import itertools
from datetime import date

import pytest
from sqlalchemy import select

from tests.tenant.conftest import (  # noqa: F401  (fixtures)
    OTHER_SCHOOL_CODE, TEST_PASSWORD, client_factory, connection, make_session, schools,
)
from app.core.security import get_password_hash
from app.models.metadata import Class, SessionYear
from app.models.student import Student
from app.models.user import User
from app.modules.fees.models import FeeHead

_admission_numbers = itertools.count(1)


async def add_student(session, *, class_id, session_year_id, date_of_birth=date(2015, 6, 1),
                      first_name="Test", admission_date=date(2024, 4, 1), **extra) -> Student:
    """Create a student in the session's school. Returns the flushed Student."""
    student = Student(
        admission_number=f"FEE-T-{next(_admission_numbers):05d}",
        first_name=first_name, last_name="Student", date_of_birth=date_of_birth,
        gender_id=1, class_id=class_id, session_year_id=session_year_id,
        father_name="Father", mother_name="Mother", admission_date=admission_date,
        is_active=True, is_deleted=False, **extra,
    )
    session.add(student)
    await session.flush()
    return student


@pytest.fixture
def sunrise_session(make_session, schools):
    """Factory for sessions bound to Sunrise (school 1)."""
    return lambda: make_session(schools["sunrise_id"])


SUNRISE_ADMIN_EMAIL = "fee-admin@sunrise-test.in"
SUNRISE_STAFF_EMAIL = "fee-staff@sunrise-test.in"


@pytest.fixture
async def sunrise_users(make_session, schools):
    """A Sunrise admin and a Sunrise staff member (staff may view fees but not configure them)."""
    async with make_session(schools["sunrise_id"]) as session:
        password = get_password_hash(TEST_PASSWORD)
        admin = User(email=SUNRISE_ADMIN_EMAIL, password=password, first_name="Fee", last_name="Admin",
                     user_type_id=1, is_active=True)
        staff = User(email=SUNRISE_STAFF_EMAIL, password=password, first_name="Fee", last_name="Staff",
                     user_type_id=4, is_active=True)
        session.add_all([admin, staff])
        await session.commit()
        return {"admin_id": admin.id, "staff_id": staff.id}


async def login(client_factory, school_code: str, email: str) -> dict:
    async with client_factory(school_code) as client:
        r = await client.post("/api/v1/auth/login-json", json={"email": email, "password": TEST_PASSWORD})
        assert r.status_code == 200, r.text
        return {"Authorization": f"Bearer {r.json()['access_token']}"}


class Api:
    """Small HTTP helper: one school, one login."""

    def __init__(self, client_factory, school_code, headers):
        self._factory, self.code, self.headers = client_factory, school_code, headers

    async def call(self, method, path, **kw):
        """`path` is relative to /api/v1/billing, or absolute when it starts with /api/."""
        url = path if path.startswith("/api/") else f"/api/v1/billing{path}"
        async with self._factory(self.code) as client:
            return await client.request(method, url, headers=self.headers, **kw)

    async def get(self, path, **kw):
        return await self.call("GET", path, **kw)

    async def post(self, path, **kw):
        return await self.call("POST", path, **kw)

    async def put(self, path, **kw):
        return await self.call("PUT", path, **kw)

    async def patch(self, path, **kw):
        return await self.call("PATCH", path, **kw)

    async def delete(self, path, **kw):
        return await self.call("DELETE", path, **kw)


@pytest.fixture
async def admin_api(client_factory, schools, sunrise_users):
    return Api(client_factory, schools["sunrise_code"], await login(client_factory, schools["sunrise_code"], SUNRISE_ADMIN_EMAIL))


@pytest.fixture
async def staff_api(client_factory, schools, sunrise_users):
    return Api(client_factory, schools["sunrise_code"], await login(client_factory, schools["sunrise_code"], SUNRISE_STAFF_EMAIL))


@pytest.fixture
async def other_api(client_factory, schools):
    """Admin of the second school (oakridge)."""
    return Api(client_factory, schools["other_code"], await login(client_factory, schools["other_code"], schools["other_admin_email"]))


@pytest.fixture
async def refs(sunrise_session):
    """Ids of Sunrise reference data: session 2026-27, two classes, fee heads by code."""
    async with sunrise_session() as session:
        year = (await session.execute(select(SessionYear).where(SessionYear.name == "2026-27"))).scalar_one()
        classes = (await session.execute(select(Class).order_by(Class.sort_order).limit(2))).scalars().all()
        heads = {h.code: h.id for h in (await session.execute(select(FeeHead))).scalars()}
        return {"year_id": year.id, "class_ids": [c.id for c in classes], "heads": heads}
