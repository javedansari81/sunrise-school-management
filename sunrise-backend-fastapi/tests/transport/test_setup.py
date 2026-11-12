"""
Transport setup (types, vehicles, routes, stops, rates), rosters, permissions,
tenant isolation, seed data and the legacy table rename.
"""
from sqlalchemy import select, text

from app.core.tenant import global_sql

from app.core.tenant import tenant_bypass
from app.models.metadata import SessionYear
from app.models.tenant import TenantMixin
from app.modules.transport import models as m
from app.modules.transport.provisioning import seed_transport_defaults

from .conftest import new_student, ok

TRANSPORT_MODELS = [m.TransportType, m.Vehicle, m.Route, m.RouteStop, m.TransportRate, m.TransportAssignment,
                    m.TransportPause]


def test_every_transport_model_is_tenant_scoped():
    assert all(issubclass(model, TenantMixin) for model in TRANSPORT_MODELS)


# ---------------------------------------------------------------------------
# Schema, seeds and the legacy table
# ---------------------------------------------------------------------------

async def test_seeded_types_rates_and_settings(sunrise_session, refs):
    async with sunrise_session() as session:
        types = {t.name: t for t in (await session.execute(select(m.TransportType))).scalars()}
        assert {"E-Rickshaw", "Van", "Bus"} <= set(types)
        rates = (await session.execute(select(m.TransportRate).where(
            m.TransportRate.session_year_id == refs["year_id"]))).scalars().all()
        flat = {r.transport_type_id: str(r.monthly_amount) for r in rates if r.basis == "FLAT"}
        # Carried over from the old price list for 2026-27
        assert flat[types["E-Rickshaw"].id] == "500.00" and flat[types["Van"].id] == "700.00"
        slabs = sorted((str(r.distance_from_km), str(r.distance_to_km), str(r.monthly_amount))
                       for r in rates if r.basis == "DISTANCE_SLAB")
        assert slabs[:2] == [("0.00", "8.00", "700.00"), ("10.00", "12.00", "900.00")]
        due_day = (await session.execute(text(
            "SELECT value FROM school_settings WHERE key = 'fee.transport.due_day' AND school_id = :school_id"))).scalar_one()
        assert due_day == "10"


LEGACY_TABLES = {
    "legacy_fee_structures", "fee_records", "fee_payments", "fee_payment_audit_log", "monthly_fee_tracking",
    "monthly_payment_allocations", "legacy_transport_types", "transport_type_pricing", "transport_distance_slabs",
    "student_transport_enrollment", "transport_monthly_tracking", "transport_payments",
    "transport_payment_allocations",
}


async def test_legacy_tables_dropped(sunrise_session):
    """Migration V004 dropped the 13 pre-redesign fee and transport tables and their functions."""
    async with sunrise_session() as session:
        tables = set((await session.execute(global_sql(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = current_schema()"))).scalars())
        functions = set((await session.execute(global_sql(
            "SELECT p.proname FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace "
            "WHERE n.nspname = current_schema()"))).scalars())
    assert "transport_types" in tables
    assert not tables & LEGACY_TABLES
    assert functions == {"calculate_sibling_fee_waiver", "get_waiver_reason_text",
                         "enable_tenant_row_level_security"}


async def test_seed_defaults_for_new_school(make_session, schools):
    async with make_session() as session:
        with tenant_bypass(session):
            created = await seed_transport_defaults(session, school_id=schools["other_id"],
                                                    template_school_id=schools["sunrise_id"])
            await session.commit()
    assert created["transport_types"] >= 3
    async with make_session(schools["other_id"]) as session:
        names = {t.name for t in (await session.execute(select(m.TransportType))).scalars()}
    assert {"E-Rickshaw", "Van", "Bus"} <= names


# ---------------------------------------------------------------------------
# Types and vehicles
# ---------------------------------------------------------------------------

async def test_types_and_vehicles(transit, fleet):
    dup = await ok(await transit.post("/transport-types", json={"name": "test shuttle"}), 409)
    assert "already exists" in dup["detail"]
    in_use = await ok(await transit.delete(f"/transport-types/{fleet['type_id']}"), 409)
    assert "deactivate" in in_use["detail"]
    spare = await ok(await transit.post("/transport-types", json={"name": "Spare Kind"}), 201)
    assert (await transit.delete(f"/transport-types/{spare['id']}")).status_code == 204

    vehicles = await ok(await transit.get("/vehicles", params={"transport_type_id": fleet["type_id"]}))
    assert [v["registration_number"] for v in vehicles] == ["UP91 T 0001"]
    dup_v = await transit.post("/vehicles", json={"transport_type_id": fleet["type_id"],
                                                  "registration_number": "UP91 t 0001"})
    assert dup_v.status_code == 409
    serving = await ok(await transit.delete(f"/vehicles/{fleet['vehicle_id']}"), 409)
    assert "serves a route" in serving["detail"]

    await ok(await transit.patch(f"/transport-types/{fleet['type_id']}", json={"is_active": False}))
    assert fleet["type_id"] not in {t["id"] for t in await ok(await transit.get("/transport-types"))}
    listed = await ok(await transit.get("/transport-types", params={"include_inactive": True}))
    assert fleet["type_id"] in {t["id"] for t in listed}


# ---------------------------------------------------------------------------
# Routes and stops
# ---------------------------------------------------------------------------

async def test_route_stops_insert_reorder_delete(transit, fleet):
    rid = fleet["route_id"]
    route = await ok(await transit.get(f"/routes/{rid}"))
    assert [(s["name"], s["sequence"]) for s in route["stops"]] == [("Stop A", 1), ("Stop B", 2), ("Stop C", 3)]

    await ok(await transit.post(f"/routes/{rid}/stops", json={"name": "Stop A2", "sequence": 2,
                                                               "distance_km": "5.50"}), 201)
    names = [s["name"] for s in (await ok(await transit.get(f"/routes/{rid}")))["stops"]]
    assert names == ["Stop A", "Stop A2", "Stop B", "Stop C"]
    assert (await transit.post(f"/routes/{rid}/stops", json={"name": "stop b"})).status_code == 409

    stops = {s["name"]: s["id"] for s in (await ok(await transit.get(f"/routes/{rid}")))["stops"]}
    order = [stops["Stop C"], stops["Stop B"], stops["Stop A2"], stops["Stop A"]]
    reordered = await ok(await transit.put(f"/routes/{rid}/stops/order", json={"stop_ids": order}))
    assert [s["id"] for s in reordered["stops"]] == order
    assert [s["sequence"] for s in reordered["stops"]] == [1, 2, 3, 4]
    partial = await transit.put(f"/routes/{rid}/stops/order", json={"stop_ids": order[:2]})
    assert partial.status_code == 422

    assert (await transit.delete(f"/stops/{stops['Stop A2']}")).status_code == 204
    after = (await ok(await transit.get(f"/routes/{rid}")))["stops"]
    assert [(s["name"], s["sequence"]) for s in after] == [("Stop C", 1), ("Stop B", 2), ("Stop A", 3)]

    dup = await transit.post("/routes", json={"name": "test route north"})
    assert dup.status_code == 409
    twice = await transit.post("/routes", json={"name": "Twice", "stops": [{"name": "X"}, {"name": "x"}]})
    assert twice.status_code == 422


async def test_route_with_riders_cannot_be_deleted(transit, fleet, sunrise_session):
    sid = await new_student(sunrise_session, fleet)
    await ok(await transit.post("/assignments", json={
        "student_id": sid, "session_year_id": fleet["year_id"], "route_stop_id": fleet["stops"]["Stop A"],
        "start_date": "2026-04-01"}), 201)
    assert (await transit.delete(f"/routes/{fleet['route_id']}")).status_code == 409
    assert (await transit.delete(f"/stops/{fleet['stops']['Stop A']}")).status_code == 409
    # An inactive stop keeps its riders but takes no new ones
    await ok(await transit.patch(f"/stops/{fleet['stops']['Stop A']}", json={"is_active": False}))
    other = await new_student(sunrise_session, fleet)
    refused = await ok(await transit.post("/assignments", json={
        "student_id": other, "session_year_id": fleet["year_id"], "route_stop_id": fleet["stops"]["Stop A"],
        "start_date": "2026-04-01"}), 422)
    assert "inactive" in refused["detail"]


# ---------------------------------------------------------------------------
# Rates
# ---------------------------------------------------------------------------

async def test_rate_validation(transit, fleet):
    year, t = fleet["year_id"], fleet["type_id"]
    overlap = await ok(await transit.post("/rates", json={
        "session_year_id": year, "basis": "DISTANCE_SLAB", "transport_type_id": t,
        "distance_from_km": "4", "distance_to_km": "6", "monthly_amount": "700"}), 409)
    assert "overlaps" in overlap["detail"]
    # Touching ends do not overlap: (12, 20]
    await ok(await transit.post("/rates", json={
        "session_year_id": year, "basis": "DISTANCE_SLAB", "transport_type_id": t,
        "distance_from_km": "12", "distance_to_km": "20", "monthly_amount": "900"}), 201)
    second_flat = await transit.post("/rates", json={
        "session_year_id": year, "basis": "FLAT", "transport_type_id": t, "monthly_amount": "1"})
    assert second_flat.status_code == 409
    second_stop = await transit.post("/rates", json={
        "session_year_id": year, "basis": "PER_STOP", "route_stop_id": fleet["stops"]["Stop B"],
        "monthly_amount": "1"})
    assert second_stop.status_code == 409
    for bad in (
        {"basis": "FLAT", "monthly_amount": "1"},
        {"basis": "PER_STOP", "monthly_amount": "1"},
        {"basis": "DISTANCE_SLAB", "distance_from_km": "5", "distance_to_km": "5", "monthly_amount": "1"},
        {"basis": "FLAT", "transport_type_id": t, "monthly_amount": "-1"},
    ):
        assert (await transit.post("/rates", json={"session_year_id": year, **bad})).status_code == 422
    widen = await transit.patch(f"/rates/{fleet['rates']['near']['id']}", json={"distance_to_km": "7"})
    assert widen.status_code == 409


async def test_quote(transit, fleet):
    async def quote(**placement):
        return await ok(await transit.post("/rates/quote", json={"session_year_id": fleet["year_id"], **placement}))

    by_stop = await quote(route_stop_id=fleet["stops"]["Stop B"])
    assert (by_stop["basis"], by_stop["monthly_amount"]) == ("PER_STOP", "950.00")
    assert by_stop["route_id"] == fleet["route_id"] and by_stop["transport_type_id"] == fleet["type_id"]
    t = fleet["type_id"]
    assert (await quote(transport_type_id=t, distance_km="0"))["monthly_amount"] == "600.00"
    assert (await quote(transport_type_id=t, distance_km="5"))["monthly_amount"] == "600.00"
    assert (await quote(transport_type_id=t, distance_km="5.01"))["monthly_amount"] == "800.00"
    assert (await quote(transport_type_id=t, distance_km="30"))["basis"] == "FLAT"
    assert (await quote(transport_type_id=t))["monthly_amount"] == "500.00"


async def test_copy_rates_to_new_session(transit, fleet, sunrise_session):
    async with sunrise_session() as session:
        year = SessionYear(name="2031-32", description="Test session", is_current=False, is_active=True)
        session.add(year)
        await session.commit()
        new_year = year.id
    copied = await ok(await transit.post("/rates/copy", json={
        "from_session_year_id": fleet["year_id"], "to_session_year_id": new_year}))
    source = await ok(await transit.get("/rates", params={"session_year_id": fleet["year_id"]}))
    assert copied["copied"] == len(source)
    again = await transit.post("/rates/copy", json={
        "from_session_year_id": fleet["year_id"], "to_session_year_id": new_year})
    assert again.status_code == 409


# ---------------------------------------------------------------------------
# Rosters
# ---------------------------------------------------------------------------

async def test_route_and_vehicle_rosters(transit, fleet, sunrise_session):
    a1 = await new_student(sunrise_session, fleet, first_name="Aman")
    b1 = await new_student(sunrise_session, fleet, first_name="Bina")
    later = await new_student(sunrise_session, fleet, first_name="Chetan")
    year = fleet["year_id"]
    for sid, stop, start in ((a1, "Stop A", "2026-04-01"), (b1, "Stop C", "2026-04-01"),
                             (later, "Stop A", "2026-12-01")):
        await ok(await transit.post("/assignments", json={
            "student_id": sid, "session_year_id": year, "route_stop_id": fleet["stops"][stop],
            "start_date": start, "allow_over_capacity": True}), 201)
    b_assignment = (await ok(await transit.get("/assignments", params={"student_id": b1})))[0]
    await ok(await transit.post(f"/assignments/{b_assignment['id']}/pauses", json={
        "from_period": "2026-09-01", "to_period": "2026-09-01"}), 201)

    roster = await ok(await transit.get(f"/routes/{fleet['route_id']}/roster", params={"on_date": "2026-09-10"}))
    assert roster["seats"] == 2 and roster["riding"] == 1 and roster["paused"] == 1
    assert roster["over_capacity"] is False
    stops = [(s["stop"]["name"], [r["student_id"] for r in s["riders"]]) for s in roster["stops"]]
    assert stops == [("Stop A", [a1]), ("Stop B", []), ("Stop C", [b1])]
    assert roster["stops"][2]["riders"][0]["paused"] is True
    assert roster["stops"][0]["riders"][0]["student_name"] == "Aman Student"

    december = await ok(await transit.get(f"/vehicles/{fleet['vehicle_id']}/roster",
                                          params={"on_date": "2026-12-05"}))
    assert december["riding"] == 3 and december["over_capacity"] is True
    assert [r["route_id"] for r in december["routes"]] == [fleet["route_id"]]

    riding = await ok(await transit.get("/assignments", params={"vehicle_id": fleet["vehicle_id"],
                                                                "active_on": "2026-09-10"}))
    assert {a["student_id"] for a in riding} == {a1, b1}


# ---------------------------------------------------------------------------
# Permissions and isolation
# ---------------------------------------------------------------------------

async def test_staff_can_view_but_not_manage(transit_staff, fleet):
    assert (await transit_staff.get("/routes")).status_code == 200
    assert (await transit_staff.get(f"/routes/{fleet['route_id']}/roster")).status_code == 200
    assert (await transit_staff.post("/transport-types", json={"name": "Nope"})).status_code == 403
    assert (await transit_staff.post("/assignments", json={})).status_code == 403


async def test_other_school_sees_nothing(transit_other, fleet, sunrise_session):
    assert fleet["route_id"] not in {r["id"] for r in await ok(await transit_other.get("/routes"))}
    assert (await transit_other.get(f"/routes/{fleet['route_id']}")).status_code == 404
    assert (await transit_other.get(f"/routes/{fleet['route_id']}/roster")).status_code == 404
    assert (await transit_other.patch(f"/vehicles/{fleet['vehicle_id']}", json={"remarks": "x"})).status_code == 404
    assert (await transit_other.delete(f"/rates/{fleet['rates']['flat']['id']}")).status_code == 404
    sid = await new_student(sunrise_session, fleet)
    cross = await transit_other.post("/assignments", json={
        "student_id": sid, "session_year_id": fleet["year_id"], "route_stop_id": fleet["stops"]["Stop A"],
        "start_date": "2026-04-01"})
    assert cross.status_code == 404
