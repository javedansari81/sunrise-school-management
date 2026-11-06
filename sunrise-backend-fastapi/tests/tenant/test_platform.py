"""
Platform admin and school management tests.
See conftest.py for how the database is prepared and rolled back.
"""
import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError

from app.core.security import get_password_hash
from app.core.tenant import tenant_bypass
from app.models.metadata import Class
from app.models.user import PLATFORM_ADMIN_USER_TYPE_ID, User

from .conftest import TEST_PASSWORD

PLATFORM_EMAIL = "platform@example-platform.com"
PLATFORM_PASSWORD = "Platform-Pass-1"


@pytest.fixture
async def platform_admin(make_session, schools):
    async with make_session() as session:
        with tenant_bypass(session):
            user = User(
                school_id=None, email=PLATFORM_EMAIL, password=get_password_hash(PLATFORM_PASSWORD),
                first_name="Plat", last_name="Form", user_type_id=PLATFORM_ADMIN_USER_TYPE_ID, is_active=True,
            )
            session.add(user)
            await session.commit()
            return user.id


@pytest.fixture
async def platform_token(client_factory, platform_admin):
    async with client_factory() as client:
        r = await client.post("/api/v1/platform/auth/login", json={"email": PLATFORM_EMAIL, "password": PLATFORM_PASSWORD})
        assert r.status_code == 200, r.text
        return r.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


async def _school_token(client_factory, code, email, password=TEST_PASSWORD):
    async with client_factory(code) as client:
        r = await client.post("/api/v1/auth/login-json", json={"email": email, "password": password})
        return r


NEW_SCHOOL = {
    "code": "maplewood",
    "name": "Maplewood High School",
    "short_name": "Maplewood",
    "phone": "9876543210",
    "admin": {"email": "admin@maplewood.in", "password": "Maple-Admin-1", "first_name": "Maple", "last_name": "Admin"},
}


# ---------------------------------------------------------------------------
# Login and token separation
# ---------------------------------------------------------------------------

async def test_platform_login(client_factory, platform_admin):
    async with client_factory() as client:
        ok = await client.post("/api/v1/platform/auth/login", json={"email": PLATFORM_EMAIL, "password": PLATFORM_PASSWORD})
        assert ok.status_code == 200
        assert ok.json()["user"]["email"] == PLATFORM_EMAIL
        bad = await client.post("/api/v1/platform/auth/login", json={"email": PLATFORM_EMAIL, "password": "wrong-password"})
        assert bad.status_code == 401
        me = await client.get("/api/v1/platform/auth/me", headers=_auth(ok.json()["access_token"]))
        assert me.status_code == 200 and me.json()["email"] == PLATFORM_EMAIL


async def test_school_admin_cannot_log_in_as_platform_admin(client_factory, schools):
    async with client_factory() as client:
        r = await client.post("/api/v1/platform/auth/login", json={"email": schools["other_admin_email"], "password": TEST_PASSWORD})
        assert r.status_code == 401


async def test_platform_token_is_rejected_by_school_routes(client_factory, platform_token, schools):
    async with client_factory(schools["sunrise_code"]) as client:
        assert (await client.get("/api/v1/auth/me", headers=_auth(platform_token))).status_code == 401
        assert (await client.get("/api/v1/students/", headers=_auth(platform_token))).status_code == 401


async def test_school_token_is_rejected_by_platform_routes(client_factory, schools):
    token = (await _school_token(client_factory, schools["other_code"], schools["other_admin_email"])).json()["access_token"]
    async with client_factory() as client:
        assert (await client.get("/api/v1/platform/schools", headers=_auth(token))).status_code == 401
        assert (await client.get("/api/v1/platform/schools")).status_code in (401, 403)  # no token at all


async def test_platform_admin_is_invisible_to_school_sessions(make_session, platform_admin, schools):
    for school_id in (schools["sunrise_id"], schools["other_id"]):
        async with make_session(school_id) as session:
            assert await session.get(User, platform_admin) is None
            emails = set((await session.execute(select(User.email))).scalars())
            assert PLATFORM_EMAIL not in emails


async def test_database_endpoints_require_platform_admin(client_factory, platform_token, schools):
    school_token = (await _school_token(client_factory, schools["other_code"], schools["other_admin_email"])).json()["access_token"]
    async with client_factory() as client:
        assert (await client.get("/api/v1/database/status")).status_code in (401, 403)
        assert (await client.get("/api/v1/database/status", headers=_auth(school_token))).status_code == 401
        ok = await client.get("/api/v1/database/status", headers=_auth(platform_token))
        assert ok.status_code == 200 and ok.json()["status"] == "deployed"


# ---------------------------------------------------------------------------
# Database rules for platform admins
# ---------------------------------------------------------------------------

async def test_school_user_without_school_is_refused_by_the_database(make_session, schools):
    async with make_session() as session:
        with tenant_bypass(session):
            session.add(User(school_id=None, email="orphan@x.in", password="x", first_name="O", last_name="R",
                             user_type_id=1, is_active=True))
            with pytest.raises(IntegrityError):
                await session.commit()
            await session.rollback()


async def test_platform_admin_with_a_school_is_refused_by_the_database(make_session, schools):
    async with make_session() as session:
        with tenant_bypass(session):
            session.add(User(school_id=schools["sunrise_id"], email="bad-platform@x.in", password="x",
                             first_name="B", last_name="P", user_type_id=PLATFORM_ADMIN_USER_TYPE_ID, is_active=True))
            with pytest.raises(IntegrityError):
                await session.commit()
            await session.rollback()


# ---------------------------------------------------------------------------
# Schools
# ---------------------------------------------------------------------------

async def test_list_schools_with_counts(client_factory, platform_token, schools):
    async with client_factory() as client:
        r = await client.get("/api/v1/platform/schools", headers=_auth(platform_token))
        assert r.status_code == 200
        by_code = {s["code"]: s for s in r.json()["schools"]}
        assert {schools["sunrise_code"], schools["other_code"]} <= set(by_code)
        assert by_code[schools["other_code"]]["users"] == 2
        filtered = await client.get("/api/v1/platform/schools", params={"search": "oak"}, headers=_auth(platform_token))
        assert [s["code"] for s in filtered.json()["schools"]] == [schools["other_code"]]


async def test_create_school_copies_lists_and_its_admin_can_log_in(client_factory, make_session, platform_token, schools):
    async with client_factory() as client:
        r = await client.post("/api/v1/platform/schools", json=NEW_SCHOOL, headers=_auth(platform_token))
        assert r.status_code == 201, r.text
        body = r.json()
    new_id = body["school"]["id"]
    assert body["school"]["status"] == "ACTIVE"
    assert body["copied_from"] == schools["sunrise_code"]

    # Every list was copied with the same number of rows as the template
    async with make_session() as session:
        with tenant_bypass(session):
            for table, count in body["copied_lists"].items():
                template = (await session.execute(text(f"SELECT COUNT(*) FROM {table} WHERE school_id = :s"),
                                                  {"s": schools["sunrise_id"]})).scalar_one()
                assert count == template and count > 0, table
            # Inventory item types point at the NEW school's categories
            wrong = (await session.execute(text(
                "SELECT COUNT(*) FROM inventory_item_types t JOIN inventory_item_category c ON c.id = t.inventory_item_category_id "
                "WHERE t.school_id = :s AND c.school_id <> :s"), {"s": new_id})).scalar_one()
            assert wrong == 0

    # The new school sees its own classes, and its admin logs in on its subdomain
    async with make_session(new_id) as session:
        assert (await session.execute(select(func.count()).select_from(Class))).scalar_one() == body["copied_lists"]["classes"]
    login = await _school_token(client_factory, "maplewood", "admin@maplewood.in", "Maple-Admin-1")
    assert login.status_code == 200, login.text
    async with client_factory("maplewood") as client:
        students = await client.get("/api/v1/students/", headers=_auth(login.json()["access_token"]))
        assert students.status_code == 200 and students.json()["total"] == 0


async def test_create_school_validation(client_factory, platform_token, schools):
    async with client_factory() as client:
        h = _auth(platform_token)
        dup = await client.post("/api/v1/platform/schools", json={**NEW_SCHOOL, "code": schools["other_code"]}, headers=h)
        assert dup.status_code == 409
        for bad in ("api", "Bad_Code", "-edge", "x" * 64):
            r = await client.post("/api/v1/platform/schools", json={**NEW_SCHOOL, "code": bad}, headers=h)
            assert r.status_code == 422, bad
        missing = await client.post("/api/v1/platform/schools", json={**NEW_SCHOOL, "copy_lists_from": "no-such-school"}, headers=h)
        assert missing.status_code == 400
        listed = await client.get("/api/v1/platform/schools", headers=h)
        assert "maplewood" not in {s["code"] for s in listed.json()["schools"]}  # nothing half-created


async def test_update_school(client_factory, platform_token, schools):
    async with client_factory() as client:
        h = _auth(platform_token)
        r = await client.patch(f"/api/v1/platform/schools/{schools['other_id']}", json={"name": "Oakridge International", "phone": "12345"}, headers=h)
        assert r.status_code == 200 and r.json()["name"] == "Oakridge International"
        taken = await client.patch(f"/api/v1/platform/schools/{schools['other_id']}", json={"code": schools["sunrise_code"]}, headers=h)
        assert taken.status_code == 409
        renamed = await client.patch(f"/api/v1/platform/schools/{schools['other_id']}", json={"code": "oakridge-intl"}, headers=h)
        assert renamed.status_code == 200 and renamed.json()["code"] == "oakridge-intl"
        assert (await client.get("/api/v1/platform/schools/999999", headers=h)).status_code == 404
    # The login follows the new subdomain
    assert (await _school_token(client_factory, "oakridge-intl", schools["other_admin_email"])).status_code == 200


async def test_suspend_blocks_login_and_existing_tokens(client_factory, platform_token, schools):
    token = (await _school_token(client_factory, schools["other_code"], schools["other_admin_email"])).json()["access_token"]
    async with client_factory() as client:
        r = await client.post(f"/api/v1/platform/schools/{schools['other_id']}/suspend", headers=_auth(platform_token))
        assert r.status_code == 200 and r.json()["status"] == "SUSPENDED"
    async with client_factory(schools["other_code"]) as client:
        assert (await client.get("/api/v1/auth/me", headers=_auth(token))).status_code == 403
    assert (await _school_token(client_factory, schools["other_code"], schools["other_admin_email"])).status_code == 403
    # Other schools are not affected
    assert (await client_factory(schools["sunrise_code"]).get("/api/v1/public/gallery")).status_code == 200

    async with client_factory() as client:
        r = await client.post(f"/api/v1/platform/schools/{schools['other_id']}/activate", headers=_auth(platform_token))
        assert r.status_code == 200 and r.json()["status"] == "ACTIVE"
    async with client_factory(schools["other_code"]) as client:
        assert (await client.get("/api/v1/auth/me", headers=_auth(token))).status_code == 200


# ---------------------------------------------------------------------------
# Platform admins
# ---------------------------------------------------------------------------

async def test_create_platform_admin(client_factory, platform_token):
    async with client_factory() as client:
        h = _auth(platform_token)
        body = {"email": "second@example-platform.com", "password": "Second-Pass-1", "first_name": "Second", "last_name": "Admin"}
        assert (await client.post("/api/v1/platform/admins", json=body, headers=h)).status_code == 201
        assert (await client.post("/api/v1/platform/admins", json=body, headers=h)).status_code == 409
        emails = {a["email"] for a in (await client.get("/api/v1/platform/admins", headers=h)).json()}
        assert {PLATFORM_EMAIL, "second@example-platform.com"} <= emails
        login = await client.post("/api/v1/platform/auth/login", json={"email": body["email"], "password": body["password"]})
        assert login.status_code == 200
