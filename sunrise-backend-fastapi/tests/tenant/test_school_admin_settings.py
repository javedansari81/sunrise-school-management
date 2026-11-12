"""
School Shop switch and the school admin's Settings screen (/school-settings).

Oakridge is the test school from conftest; Sunrise is school 1. Every change is
rolled back with the test transaction.
"""
from sqlalchemy import select, text

from app.core.tenant import tenant_bypass
from app.models.metadata import Department, SessionYear
from app.models.school import School, SchoolSetting
from app.services import school_settings
from tests.tenant.conftest import TEST_PASSWORD


async def _admin(client, schools):
    response = await client.post(
        "/api/v1/auth/login-json", json={"email": schools["other_admin_email"], "password": TEST_PASSWORD})
    assert response.status_code == 200, response.text
    client.headers["Authorization"] = f"Bearer {response.json()['access_token']}"


# ------------------------------------------------------------ School Shop

async def test_shop_is_off_unless_the_school_turns_it_on(client_factory, schools):
    async with client_factory(schools["other_code"]) as client:
        public = await client.get("/api/v1/public/school")
        assert public.json()["features"] == {"shop": False}

        await _admin(client, schools)
        refused = await client.get("/api/v1/inventory/pricing/")
        assert refused.status_code == 403
        assert "turned off" in refused.json()["detail"]

        turned_on = await client.put(f"/api/v1/school-settings/values/{school_settings.SHOP_ENABLED}", json={"value": True})
        assert turned_on.status_code == 200, turned_on.text
        assert turned_on.json()["value"] == "true"

        assert (await client.get("/api/v1/public/school")).json()["features"] == {"shop": True}
        assert (await client.get("/api/v1/inventory/pricing/")).status_code != 403

        # Reset to the default (off)
        reset = await client.put(f"/api/v1/school-settings/values/{school_settings.SHOP_ENABLED}", json={"value": None})
        assert reset.json()["value"] is None
        assert (await client.get("/api/v1/inventory/pricing/")).status_code == 403


async def test_shop_switch_is_per_school(make_session, schools):
    async with make_session(schools["other_id"]) as session:
        session.add(SchoolSetting(key=school_settings.SHOP_ENABLED, value="true"))
        await session.commit()
    async with make_session(schools["other_id"]) as session:
        assert await school_settings.shop_enabled(session) is True
    async with make_session(schools["sunrise_id"]) as session:
        await session.execute(SchoolSetting.__table__.delete().where(
            SchoolSetting.school_id == schools["sunrise_id"], SchoolSetting.key == school_settings.SHOP_ENABLED))
        await session.commit()
        assert await school_settings.shop_enabled(session) is False


# ------------------------------------------------------------ settings

async def test_settings_are_validated(client_factory, schools):
    async with client_factory(schools["other_code"]) as client:
        await _admin(client, schools)
        values = (await client.get("/api/v1/school-settings/values")).json()
        keys = {item["key"] for item in values}
        assert {school_settings.SHOP_ENABLED, "fee.late_fee.grace_days", "fee.transport.cutoff_day"} <= keys

        assert (await client.put("/api/v1/school-settings/values/fee.transport.cutoff_day", json={"value": "40"})).status_code == 422
        assert (await client.put("/api/v1/school-settings/values/fee.late_fee.mode", json={"value": "SOMETIMES"})).status_code == 422
        assert (await client.put("/api/v1/school-settings/values/not.a.setting", json={"value": "1"})).status_code == 404
        ok = await client.put("/api/v1/school-settings/values/fee.late_fee.mode", json={"value": "percent"})
        assert ok.json()["value"] == "PERCENT"


async def test_settings_need_an_admin(client_factory, schools):
    async with client_factory(schools["other_code"]) as client:
        assert (await client.get("/api/v1/school-settings/values")).status_code in (401, 403)


async def test_profile_changes_only_the_callers_school(client_factory, make_session, schools):
    async with client_factory(schools["other_code"]) as client:
        await _admin(client, schools)
        response = await client.patch("/api/v1/school-settings/profile", json={"short_name": "Oakridge", "phone": "98765 43210"})
        assert response.status_code == 200, response.text
        assert response.json()["short_name"] == "Oakridge"
        assert response.json()["code"] == schools["other_code"]
        # code and status are not editable here
        await client.patch("/api/v1/school-settings/profile", json={"code": "hijack", "status": "SUSPENDED"})

    async with make_session() as session:
        with tenant_bypass(session):
            oak = await session.get(School, schools["other_id"])
            sunrise = await session.get(School, schools["sunrise_id"])
            assert (oak.code, oak.status, oak.phone) == (schools["other_code"], "ACTIVE", "98765 43210")
            assert sunrise.short_name != "Oakridge"


# ------------------------------------------------------------ lists

async def test_lists_are_added_and_changed_for_the_callers_school(client_factory, make_session, schools):
    async with client_factory(schools["other_code"]) as client:
        await _admin(client, schools)
        kinds = {item["kind"] for item in (await client.get("/api/v1/school-settings/lists")).json()}
        assert "departments" in kinds and "inventory_item_types" not in kinds  # shop lists hidden while the shop is off

        created = await client.post("/api/v1/school-settings/lists/departments", json={"name": "Robotics", "description": "STEM lab"})
        assert created.status_code == 201, created.text
        row = created.json()
        assert (await client.post("/api/v1/school-settings/lists/departments", json={"name": "robotics"})).status_code == 409
        assert (await client.post("/api/v1/school-settings/lists/departments", json={"description": "no name"})).status_code == 422

        changed = await client.patch(f"/api/v1/school-settings/lists/departments/{row['id']}", json={"is_active": False})
        assert changed.json()["is_active"] is False
        listed = (await client.get("/api/v1/school-settings/lists/departments")).json()
        assert any(item["id"] == row["id"] and not item["is_active"] for item in listed)

        # The configuration endpoint sees the change at once (cache cleared)
        config = (await client.get("/api/v1/configuration/teacher-management/")).json()
        assert all(item["id"] != row["id"] for item in config["departments"])  # not in use, so not offered

    async with make_session(schools["sunrise_id"]) as session:
        sunrise_rows = (await session.execute(select(Department.id))).scalars().all()
        assert row["id"] not in sunrise_rows
        sunrise_dept = sunrise_rows[0] if sunrise_rows else None

    if sunrise_dept is not None:
        async with client_factory(schools["other_code"]) as client:
            await _admin(client, schools)
            other = await client.patch(f"/api/v1/school-settings/lists/departments/{sunrise_dept}", json={"name": "Taken over"})
            assert other.status_code == 404


async def test_one_session_year_is_current(client_factory, make_session, schools):
    async with make_session(schools["other_id"]) as session:
        session.add(SessionYear(name="2026-27", description="Academic Year 2026-27", start_date=text("'2026-04-01'"),
                                end_date=text("'2027-03-31'"), is_current=True, is_active=True))
        await session.commit()

    async with client_factory(schools["other_code"]) as client:
        await _admin(client, schools)
        bad = await client.post("/api/v1/school-settings/lists/session_years",
                                json={"name": "2027-28", "description": "x", "start_date": "2028-04-01", "end_date": "2027-04-01"})
        assert bad.status_code == 422
        new = await client.post("/api/v1/school-settings/lists/session_years",
                                json={"name": "2027-28", "description": "Academic Year 2027-28",
                                      "start_date": "2027-04-01", "end_date": "2028-03-31", "is_current": True})
        assert new.status_code == 201, new.text
        years = (await client.get("/api/v1/school-settings/lists/session_years")).json()
        assert [year["name"] for year in years if year["is_current"]] == ["2027-28"]

        unset = await client.patch(f"/api/v1/school-settings/lists/session_years/{new.json()['id']}", json={"is_current": False})
        assert unset.status_code == 422
