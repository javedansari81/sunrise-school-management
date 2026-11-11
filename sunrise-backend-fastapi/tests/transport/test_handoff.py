"""
Transport to fee handoff: assign, change, discontinue, cancel, pause, plus the
cut-off day, capacity and the guards on the fee module's side.

Session 2026-27 runs April 2026 to March 2027; Sunrise's cut-off day is 15.
Prices come from the `fleet` fixture (stop A 600 by slab, stop B 950 per stop,
stop C 500 flat).
"""
from datetime import date

import pytest

from app.modules.transport import billing
from app.modules.transport.models import TransportAssignment, TransportPause

from .conftest import billing_api, months, new_student, ok, transport_dues

ALL_MONTHS = ["2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09",
              "2026-10", "2026-11", "2026-12", "2027-01", "2027-02", "2027-03"]


async def _assign(transit, fleet, student_id, stop="Stop A", start="2026-04-01", status=201, **kw):
    r = await transit.post("/assignments", json={
        "student_id": student_id, "session_year_id": fleet["year_id"], "route_stop_id": fleet["stops"][stop],
        "start_date": start, **kw})
    return await ok(r, status)


async def _plan(admin_api, student_id, fleet, include_inactive=False):
    lines = await ok(await billing_api(admin_api).get(
        f"/students/{student_id}/plan", params={"session_year_id": fleet["year_id"],
                                                "include_inactive": include_inactive}))
    return [line for line in lines if line["source"] == "TRANSPORT"]


async def _pay(admin_api, student_id, amount, **kw):
    return await ok(await billing_api(admin_api).post("/payments", json={
        "student_id": student_id, "amount": amount, "payment_method_id": 1, **kw}), 201)


# ---------------------------------------------------------------------------
# Month rules (no database)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("start, first", [
    (date(2026, 6, 1), date(2026, 6, 1)),
    (date(2026, 6, 15), date(2026, 6, 1)),   # on the cut-off day: that month
    (date(2026, 6, 16), date(2026, 7, 1)),   # after it: next month
    (date(2026, 12, 31), date(2027, 1, 1)),
])
def test_first_billed_month(start, first):
    assert billing.first_billed_period(start, 15) == first


@pytest.mark.parametrize("end, last", [
    (date(2026, 10, 14), date(2026, 9, 1)),   # stops before the cut-off day: month not billed
    (date(2026, 10, 15), date(2026, 10, 1)),  # rides on the cut-off day: billed
    (date(2026, 10, 31), date(2026, 10, 1)),
    (date(2026, 10, 1), date(2026, 9, 1)),
])
def test_last_billed_month(end, last):
    assert billing.last_billed_period(end, 15) == last


@pytest.mark.parametrize("change_day", [1, 10, 14, 15, 16, 17, 28])
def test_change_never_skips_or_doubles_a_month(change_day):
    effective = date(2026, 8, change_day)
    old_last = billing.last_billed_period(date(2026, 8, change_day - 1) if change_day > 1 else date(2026, 7, 31), 15)
    new_first = billing.first_billed_period(effective, 15)
    assert (new_first.year * 12 + new_first.month) - (old_last.year * 12 + old_last.month) == 1


def test_segments_cut_out_pauses():
    a = TransportAssignment(start_date=date(2026, 4, 1), end_date=None, monthly_amount=500, is_active=True, pauses=[
        TransportPause(from_period=date(2026, 7, 1), to_period=date(2026, 8, 1), is_active=True),
        TransportPause(from_period=date(2027, 3, 1), to_period=date(2027, 3, 1), is_active=True),
        TransportPause(from_period=date(2026, 5, 1), to_period=date(2026, 5, 1), is_active=False),
    ])
    first, last = date(2026, 4, 1), date(2027, 3, 1)
    assert billing.segments(a, cutoff=15, first=first, last=last) == [
        (date(2026, 4, 1), date(2026, 6, 1)), (date(2026, 9, 1), date(2027, 2, 1)),
    ]
    a.pauses[1].is_active = False
    assert billing.segments(a, cutoff=15, first=first, last=last)[-1] == (date(2026, 9, 1), None)
    a.is_active = False
    assert billing.segments(a, cutoff=15, first=first, last=last) == []


# ---------------------------------------------------------------------------
# Assign
# ---------------------------------------------------------------------------

async def test_assign_creates_plan_line_and_dues(transit, admin_api, fleet, sunrise_session):
    sid = await new_student(sunrise_session, fleet)
    result = await _assign(transit, fleet, sid, stop="Stop B")
    a = result["assignment"]
    assert a["monthly_amount"] == "950.00" and a["transport_rate_id"] == fleet["rates"]["stop_b"]["id"]
    assert a["route_id"] == fleet["route_id"] and a["transport_type_id"] == fleet["type_id"]
    assert a["distance_km"] == "9.00"
    assert a["billing"]["billed_from"] == "2026-04-01" and a["billing"]["billed_to"] == "2027-03-01"
    assert result["plan_lines"]["created"] == 1

    lines = await _plan(admin_api, sid, fleet)
    assert len(lines) == 1
    assert lines[0]["source_ref_id"] == a["id"] and lines[0]["end_period"] is None
    assert lines[0]["fee_head_id"] == fleet["transport_head_id"] and lines[0]["amount"] == "950.00"

    dues = await transport_dues(admin_api, sid, fleet["transport_head_id"])
    assert months(dues) == ALL_MONTHS
    assert {d["net_amount"] for d in dues} == {"950.00"}
    assert dues[0]["due_date"] == "2026-04-10"  # fee.transport.due_day


async def test_rate_lookup_order(transit, fleet, sunrise_session):
    """Stop rate first, then distance slab, then the flat rate; an amount given by hand wins."""
    s1, s2, s3, s4 = [await new_student(sunrise_session, fleet) for _ in range(4)]
    allow = {"allow_over_capacity": True}
    assert (await _assign(transit, fleet, s1, stop="Stop B"))["assignment"]["monthly_amount"] == "950.00"
    assert (await _assign(transit, fleet, s2, stop="Stop A"))["assignment"]["monthly_amount"] == "600.00"
    flat = (await _assign(transit, fleet, s3, stop="Stop C", **allow))["assignment"]
    assert flat["monthly_amount"] == "500.00" and flat["transport_rate_id"] == fleet["rates"]["flat"]["id"]
    manual = (await _assign(transit, fleet, s4, stop="Stop C", monthly_amount="300.00", **allow))["assignment"]
    assert manual["monthly_amount"] == "300.00" and manual["amount_overridden"] is True
    assert manual["transport_rate_id"] is None


async def test_cutoff_day_on_assign(transit, admin_api, fleet, sunrise_session):
    early, late = await new_student(sunrise_session, fleet), await new_student(sunrise_session, fleet)
    await _assign(transit, fleet, early, start="2026-06-15")
    await _assign(transit, fleet, late, start="2026-06-16")
    assert months(await transport_dues(admin_api, early, fleet["transport_head_id"]))[0] == "2026-06"
    assert months(await transport_dues(admin_api, late, fleet["transport_head_id"]))[0] == "2026-07"


async def test_assign_checks(transit, fleet, sunrise_session):
    sid = await new_student(sunrise_session, fleet)
    await _assign(transit, fleet, sid)
    clash = await _assign(transit, fleet, sid, start="2026-09-01", status=409)
    assert "already has transport assignment" in clash["detail"]

    other = await new_student(sunrise_session, fleet)
    outside = await _assign(transit, fleet, other, start="2027-04-01", status=422)
    assert "outside the session" in outside["detail"]
    bad_type = await transit.post("/transport-types", json={"name": "Other Kind"})
    mismatch = await _assign(transit, fleet, other, transport_type_id=bad_type.json()["id"], status=422)
    assert "another type" in mismatch["detail"]

    # No route: the type is needed, and some rate must match
    no_route = await ok(await transit.post("/assignments", json={
        "student_id": other, "session_year_id": fleet["year_id"], "start_date": "2026-04-01"}), 422)
    assert "transport_type_id" in no_route["detail"]
    no_rate = await ok(await transit.post("/assignments", json={
        "student_id": other, "session_year_id": fleet["year_id"], "start_date": "2026-04-01",
        "transport_type_id": bad_type.json()["id"]}), 422)
    assert "No transport rate" in no_rate["detail"]


async def test_vehicle_capacity(transit, fleet, sunrise_session):
    """The fleet vehicle has 2 seats."""
    s1, s2, s3 = [await new_student(sunrise_session, fleet) for _ in range(3)]
    await _assign(transit, fleet, s1)
    await _assign(transit, fleet, s2, stop="Stop B")
    full = await _assign(transit, fleet, s3, status=409)
    assert "2 riders for 2 seats" in full["detail"]
    forced = await _assign(transit, fleet, s3, allow_over_capacity=True)
    assert forced["warnings"] and "2 seats" in forced["warnings"][0]
    # Without a route there is no vehicle, so no seat check
    s4 = await new_student(sunrise_session, fleet)
    await ok(await transit.post("/assignments", json={
        "student_id": s4, "session_year_id": fleet["year_id"], "start_date": "2026-04-01",
        "transport_type_id": fleet["type_id"]}), 201)  # no route: no vehicle, no seat check


# ---------------------------------------------------------------------------
# Change
# ---------------------------------------------------------------------------

async def test_change_stop_keeps_paid_months(transit, admin_api, fleet, sunrise_session):
    sid = await new_student(sunrise_session, fleet)
    a = (await _assign(transit, fleet, sid, stop="Stop A"))["assignment"]
    await _pay(admin_api, sid, "1800.00")  # April to June at 600, oldest first

    result = await ok(await transit.post(f"/assignments/{a['id']}/change", json={
        "effective_date": "2026-05-10", "route_stop_id": fleet["stops"]["Stop C"], "reason": "Moved house"}))
    new, old = result["assignment"], result["previous"]
    assert old["end_date"] == "2026-05-09" and old["end_reason"] == "Moved house"
    assert old["billing"]["billed_to"] == "2026-04-01"
    assert new["previous_assignment_id"] == a["id"] and new["start_date"] == "2026-05-10"
    assert new["monthly_amount"] == "500.00" and new["route_stop_id"] == fleet["stops"]["Stop C"]

    dues = await transport_dues(admin_api, sid, fleet["transport_head_id"])
    assert months(dues) == ALL_MONTHS  # one due per month, none twice
    by_month = {d["period"][:7]: d for d in dues}
    for m in ("2026-04", "2026-05", "2026-06"):
        assert by_month[m]["net_amount"] == "600.00" and by_month[m]["status"] == "PAID"
    assert {by_month[m]["net_amount"] for m in ALL_MONTHS[3:]} == {"500.00"}
    assert {by_month[m]["status"] for m in ALL_MONTHS[3:]} == {"PENDING"}

    lines = await _plan(admin_api, sid, fleet)
    assert sorted((line["source_ref_id"], line["end_period"]) for line in lines) == [
        (a["id"], "2026-04-01"), (new["id"], None)]


async def test_change_picks_up_new_rate(transit, admin_api, fleet, sunrise_session):
    sid = await new_student(sunrise_session, fleet)
    a = (await _assign(transit, fleet, sid, stop="Stop B"))["assignment"]
    await ok(await transit.patch(f"/rates/{fleet['rates']['stop_b']['id']}", json={"monthly_amount": "1000.00"}))
    # Editing a rate does not touch existing assignments
    assert (await ok(await transit.get(f"/assignments/{a['id']}")))["monthly_amount"] == "950.00"

    new = (await ok(await transit.post(f"/assignments/{a['id']}/change",
                                       json={"effective_date": "2026-10-01"})))["assignment"]
    assert new["monthly_amount"] == "1000.00" and new["route_stop_id"] == a["route_stop_id"]
    by_month = {d["period"][:7]: d["net_amount"]
                for d in await transport_dues(admin_api, sid, fleet["transport_head_id"])}
    assert by_month["2026-09"] == "950.00" and by_month["2026-10"] == "1000.00"


async def test_change_checks(transit, fleet, sunrise_session):
    sid = await new_student(sunrise_session, fleet)
    a = (await _assign(transit, fleet, sid, start="2026-06-01"))["assignment"]
    same_day = await ok(await transit.post(f"/assignments/{a['id']}/change",
                                           json={"effective_date": "2026-06-01"}), 422)
    assert "cancel and assign again" in same_day["detail"]


# ---------------------------------------------------------------------------
# Discontinue and cancel
# ---------------------------------------------------------------------------

async def test_discontinue_mid_session(transit, admin_api, fleet, sunrise_session):
    sid = await new_student(sunrise_session, fleet)
    a = (await _assign(transit, fleet, sid))["assignment"]
    result = await ok(await transit.post(f"/assignments/{a['id']}/discontinue",
                                         json={"end_date": "2026-10-10", "reason": "Parent drops the child"}))
    assert result["assignment"]["end_date"] == "2026-10-10"
    assert result["assignment"]["billing"]["billed_to"] == "2026-09-01"
    assert result["plan_lines"]["dues_cancelled"] == 6  # October to March
    assert months(await transport_dues(admin_api, sid, fleet["transport_head_id"])) == ALL_MONTHS[:6]
    lines = await _plan(admin_api, sid, fleet)
    assert [line["end_period"] for line in lines] == ["2026-09-01"]

    # The student can be assigned again after the end
    await _assign(transit, fleet, sid, start="2026-12-01")
    assert months(await transport_dues(admin_api, sid, fleet["transport_head_id"])) == \
        ALL_MONTHS[:6] + ALL_MONTHS[8:]


async def test_discontinue_keeps_months_paid_in_advance(transit, admin_api, fleet, sunrise_session):
    sid = await new_student(sunrise_session, fleet)
    a = (await _assign(transit, fleet, sid))["assignment"]
    await _pay(admin_api, sid, "5400.00")  # April to December
    result = await ok(await transit.post(f"/assignments/{a['id']}/discontinue", json={"end_date": "2026-10-20"}))
    assert result["warnings"] and "Nov 2026, Dec 2026" in result["warnings"][0]
    dues = await transport_dues(admin_api, sid, fleet["transport_head_id"])
    assert months(dues) == ALL_MONTHS[:9]  # paid November and December stay
    assert {d["status"] for d in dues} == {"PAID"}


async def test_cancel_assignment(transit, admin_api, fleet, sunrise_session):
    sid = await new_student(sunrise_session, fleet)
    a = (await _assign(transit, fleet, sid))["assignment"]
    result = await ok(await transit.post(f"/assignments/{a['id']}/cancel", json={"reason": "Wrong student"}))
    assert result["assignment"]["is_active"] is False
    assert result["assignment"]["billing"]["billed_months"] == []
    assert await transport_dues(admin_api, sid, fleet["transport_head_id"]) == []
    assert await _plan(admin_api, sid, fleet) == []
    # Cancelled assignments do not block a new one
    b = (await _assign(transit, fleet, sid))["assignment"]

    await _pay(admin_api, sid, "600.00")
    paid = await ok(await transit.post(f"/assignments/{b['id']}/cancel", json={"reason": "Oops"}), 409)
    assert "Apr 2026" in paid["detail"]


# ---------------------------------------------------------------------------
# Pauses
# ---------------------------------------------------------------------------

async def test_pause_and_resume(transit, admin_api, fleet, sunrise_session):
    sid = await new_student(sunrise_session, fleet)
    a = (await _assign(transit, fleet, sid))["assignment"]
    result = await ok(await transit.post(f"/assignments/{a['id']}/pauses", json={
        "from_period": "2026-07-01", "to_period": "2026-08-31", "reason": "Away"}), 201)
    pause = result["assignment"]["pauses"][0]
    assert (pause["from_period"], pause["to_period"]) == ("2026-07-01", "2026-08-01")
    assert months(await transport_dues(admin_api, sid, fleet["transport_head_id"])) == \
        ALL_MONTHS[:3] + ALL_MONTHS[5:]
    assert sorted((line["start_period"], line["end_period"]) for line in await _plan(admin_api, sid, fleet)) == [
        ("2026-04-01", "2026-06-01"), ("2026-09-01", None)]

    overlap = await ok(await transit.post(f"/assignments/{a['id']}/pauses", json={
        "from_period": "2026-08-01", "to_period": "2026-09-01"}), 409)
    assert "Overlaps pause" in overlap["detail"]

    await ok(await transit.delete(f"/pauses/{pause['id']}"))
    assert months(await transport_dues(admin_api, sid, fleet["transport_head_id"])) == ALL_MONTHS
    lines = await _plan(admin_api, sid, fleet)
    assert [(line["start_period"], line["end_period"]) for line in lines] == [("2026-04-01", None)]


async def test_pause_refuses_paid_and_unbilled_months(transit, admin_api, fleet, sunrise_session):
    sid = await new_student(sunrise_session, fleet, admission_date=date(2024, 4, 1))
    a = (await _assign(transit, fleet, sid, start="2026-05-01"))["assignment"]
    await _pay(admin_api, sid, "600.00")  # May
    paid = await ok(await transit.post(f"/assignments/{a['id']}/pauses", json={
        "from_period": "2026-05-01", "to_period": "2026-06-01"}), 409)
    assert "May 2026" in paid["detail"]
    before = await ok(await transit.post(f"/assignments/{a['id']}/pauses", json={
        "from_period": "2026-04-01", "to_period": "2026-04-01"}), 422)
    assert "within the months" in before["detail"]


async def test_change_carries_future_pauses(transit, admin_api, fleet, sunrise_session):
    sid = await new_student(sunrise_session, fleet)
    a = (await _assign(transit, fleet, sid))["assignment"]
    await ok(await transit.post(f"/assignments/{a['id']}/pauses", json={
        "from_period": "2026-12-01", "to_period": "2027-01-01"}), 201)
    new = (await ok(await transit.post(f"/assignments/{a['id']}/change", json={
        "effective_date": "2026-10-01", "route_stop_id": fleet["stops"]["Stop B"]})))["assignment"]
    assert [(p["from_period"], p["to_period"]) for p in new["pauses"]] == [("2026-12-01", "2027-01-01")]
    assert "2026-12" not in months(await transport_dues(admin_api, sid, fleet["transport_head_id"]))


# ---------------------------------------------------------------------------
# Guards in the fee module
# ---------------------------------------------------------------------------

async def test_transport_lines_cannot_be_edited_in_billing(transit, admin_api, fleet, sunrise_session):
    sid = await new_student(sunrise_session, fleet)
    await _assign(transit, fleet, sid)
    billing_ = billing_api(admin_api)
    manual = await ok(await billing_.post(f"/students/{sid}/plan-lines", json={
        "session_year_id": fleet["year_id"], "fee_head_id": fleet["transport_head_id"], "amount": "100.00"}), 422)
    assert "transport module" in manual["detail"]
    line = (await _plan(admin_api, sid, fleet))[0]
    end = await ok(await billing_.post(f"/plan-lines/{line['id']}/end", json={"last_period": "2026-06-01"}), 422)
    assert "transport assignment" in end["detail"]


async def test_class_plan_build_leaves_transport_lines_alone(transit, admin_api, fleet, sunrise_session):
    sid = await new_student(sunrise_session, fleet)
    await _assign(transit, fleet, sid)
    h = (await ok(await billing_api(admin_api).get("/fee-heads")))
    tuition = next(x["id"] for x in h if x["code"] == "TUITION")
    s = await ok(await billing_api(admin_api).post("/fee-structures", json={
        "session_year_id": fleet["year_id"], "name": "Tuition only",
        "items": [{"fee_head_id": tuition, "amount": "1000.00"}]}), 201)
    await ok(await billing_api(admin_api).post(f"/fee-structures/{s['id']}/publish"))
    await ok(await billing_api(admin_api).post("/plans/build", json={
        "session_year_id": fleet["year_id"], "student_ids": [sid]}))
    assert len(await _plan(admin_api, sid, fleet)) == 1
    assert months(await transport_dues(admin_api, sid, fleet["transport_head_id"])) == ALL_MONTHS
