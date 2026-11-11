"""
Fixtures for the transport operations module tests.

Reuses the fee test fixtures (one rolled-back transaction per test, Sunrise plus
a second school "oakridge"). Needs a schema with migrations V002 and V003.

Transport writes generate dues "through this month". Tests fix today at
20 March 2027 (the last month of session 2026-27), so every billed month of the
session has its due and results do not depend on the real date.

Run from sunrise-backend-fastapi/:
    PYTHONIOENCODING=utf-8 python -m pytest tests -o addopts="" --asyncio-mode=auto
"""
from datetime import date

import pytest

from tests.fees.conftest import (  # noqa: F401  (fixtures)
    Api, OTHER_SCHOOL_CODE, SUNRISE_ADMIN_EMAIL, SUNRISE_STAFF_EMAIL, TEST_PASSWORD, add_student, admin_api,
    client_factory, connection, login, make_session, other_api, refs, schools, staff_api, sunrise_session,
    sunrise_users,
)
from app.modules.fees.service import dues as due_service
from app.modules.fees.service import plans as plan_service

TODAY = date(2027, 3, 20)


@pytest.fixture(autouse=True)
def frozen_today(monkeypatch):
    monkeypatch.setattr(plan_service, "today", lambda: TODAY)
    monkeypatch.setattr(due_service, "today", lambda: TODAY)
    return TODAY


class TransitApi(Api):
    """Paths are relative to /api/v1/transit, or absolute when they start with /api/."""

    async def call(self, method, path, **kw):
        url = path if path.startswith("/api/") else f"/api/v1/transit{path}"
        async with self._factory(self.code) as client:
            return await client.request(method, url, headers=self.headers, **kw)


def billing_api(api: Api) -> Api:
    return Api(api._factory, api.code, api.headers)


@pytest.fixture
async def transit(admin_api):
    return TransitApi(admin_api._factory, admin_api.code, admin_api.headers)


@pytest.fixture
async def transit_staff(staff_api):
    return TransitApi(staff_api._factory, staff_api.code, staff_api.headers)


@pytest.fixture
async def transit_other(other_api):
    return TransitApi(other_api._factory, other_api.code, other_api.headers)


async def ok(response, status=200):
    assert response.status_code == status, response.text
    return response.json()


@pytest.fixture
async def fleet(transit, refs):
    """
    A test vehicle type (no seeded rates touch it), one 2-seat vehicle and a
    route with three stops, priced for session 2026-27:
        stop A 3 km, stop B 9 km (has its own PER_STOP rate 950), stop C 14 km
        slabs (0, 5] 600 and (5, 12] 800 for the type; FLAT 500 for the type
    """
    year = refs["year_id"]
    type_ = await ok(await transit.post("/transport-types", json={"name": "Test Shuttle", "capacity": 3}), 201)
    vehicle = await ok(await transit.post("/vehicles", json={
        "transport_type_id": type_["id"], "registration_number": "up91 t 0001", "capacity": 2,
        "driver_name": "Driver", "driver_phone": "9000000000"}), 201)
    route = await ok(await transit.post("/routes", json={
        "name": "Test Route North", "vehicle_id": vehicle["id"], "stops": [
            {"name": "Stop A", "distance_km": "3.00", "pickup_time": "07:10:00"},
            {"name": "Stop B", "distance_km": "9.00", "pickup_time": "07:20:00"},
            {"name": "Stop C", "distance_km": "14.00", "pickup_time": "07:30:00"},
        ]}), 201)
    stops = {s["name"]: s["id"] for s in route["stops"]}
    t = type_["id"]
    rates = {
        "flat": await ok(await transit.post("/rates", json={
            "session_year_id": year, "basis": "FLAT", "transport_type_id": t, "monthly_amount": "500.00"}), 201),
        "near": await ok(await transit.post("/rates", json={
            "session_year_id": year, "basis": "DISTANCE_SLAB", "transport_type_id": t,
            "distance_from_km": "0", "distance_to_km": "5", "monthly_amount": "600.00"}), 201),
        "far": await ok(await transit.post("/rates", json={
            "session_year_id": year, "basis": "DISTANCE_SLAB", "transport_type_id": t,
            "distance_from_km": "5", "distance_to_km": "12", "monthly_amount": "800.00"}), 201),
        "stop_b": await ok(await transit.post("/rates", json={
            "session_year_id": year, "basis": "PER_STOP", "route_stop_id": stops["Stop B"],
            "monthly_amount": "950.00"}), 201),
    }
    return dict(year_id=year, type_id=t, vehicle_id=vehicle["id"], route_id=route["id"], stops=stops, rates=rates,
                transport_head_id=refs["heads"]["TRANSPORT"], class_ids=refs["class_ids"])


async def new_student(sunrise_session, fleet, **kw):
    kw.setdefault("class_id", fleet["class_ids"][0])
    async with sunrise_session() as session:
        s = await add_student(session, session_year_id=fleet["year_id"], **kw)
        await session.commit()
        return s.id


async def transport_dues(admin_api, student_id, head_id, *, include_cancelled=False):
    dues = await ok(await billing_api(admin_api).get(f"/students/{student_id}/dues"))
    return sorted(
        (d for d in dues if d["fee_head_id"] == head_id and (include_cancelled or d["status"] != "CANCELLED")),
        key=lambda d: d["period"],
    )


def months(dues):
    return [d["period"][:7] for d in dues]
