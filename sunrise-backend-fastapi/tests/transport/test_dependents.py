"""
Phase 4: the modules that used to read the old fee and transport tables now read
the unified fee ledger and the transport operations module.

Covers the dashboard, the fee tracking and daily collection reports, student
pages, the configuration endpoint, the sibling waiver recalculation, and that
the old /fees and /transport routes are gone.

The local database may already hold Sunrise students and dues, so school-wide
figures are checked as the change a test makes, not as absolute values.

Setup per test (session 2026-27, dues generated through March 2027, see conftest):
    tuition 1000 / month for the first class, 12 months = 12000
    transport at stop A of the test route: 600 / month from April = 7200
"""
from datetime import date
from decimal import Decimal

import pytest

from app.modules.fees.service import summary as fee_summary
from app.modules.transport.service import summary as transport_summary

from .conftest import billing_api, new_student, ok

D = Decimal
TODAY = date.today()


@pytest.fixture
async def tuition(admin_api, refs):
    """Publish a tuition-only price list for 2026-27: 1000 / month for the first class."""
    api = billing_api(admin_api)
    structure = await ok(await api.post("/fee-structures", json={
        "session_year_id": refs["year_id"], "name": "Phase 4 test", "items": [
            {"fee_head_id": refs["heads"]["TUITION"], "class_id": refs["class_ids"][0], "amount": "1000.00"},
        ]}), 201)
    await ok(await api.post(f"/fee-structures/{structure['id']}/publish"))
    return refs


async def _rider(admin_api, transit, sunrise_session, fleet, tuition, **student):
    """A student with tuition and transport (stop A from April) dues for the whole session."""
    sid = await new_student(sunrise_session, fleet, **student)
    api = billing_api(admin_api)
    await ok(await api.post("/plans/build", json={"session_year_id": fleet["year_id"], "student_id": sid}))
    await ok(await transit.post("/assignments", json={
        "student_id": sid, "session_year_id": fleet["year_id"], "route_stop_id": fleet["stops"]["Stop A"],
        "start_date": "2026-04-01"}), 201)
    await ok(await api.post("/dues/generate", json={"session_year_id": fleet["year_id"], "student_id": sid}))
    return sid


async def _pay(admin_api, student_id, amount, **kw):
    return await ok(await billing_api(admin_api).post("/payments", json={
        "student_id": student_id, "amount": amount, "payment_method_id": 1, **kw}), 201)


async def _dashboard(admin_api, year_id):
    return await ok(await admin_api.get("/api/v1/dashboard/admin-dashboard-enhanced-stats",
                                        params={"session_year_id": year_id}))


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

async def test_dashboard_reads_the_ledger(admin_api, transit, sunrise_session, fleet, tuition):
    year = fleet["year_id"]
    before = await _dashboard(admin_api, year)
    assert "error" not in before["fee_management"], before["fee_management"]
    assert "error" not in before["transport_service"], before["transport_service"]

    sid = await _rider(admin_api, transit, sunrise_session, fleet, tuition)
    # Allocation goes oldest due date first across both heads, so the transport share
    # of the payment is read back from the ledger, not assumed.
    await _pay(admin_api, sid, "3000.00")
    after = await _dashboard(admin_api, year)

    fees_before, fees_after = before["fee_management"], after["fee_management"]
    assert D(str(fees_after["total_collected"])) - D(str(fees_before["total_collected"])) == D("3000")
    billed = D("12000") + D("7200")
    assert D(str(fees_after["pending_fees"])) - D(str(fees_before["pending_fees"])) == billed - D("3000")
    assert fees_after["total_records"] - fees_before["total_records"] == 1
    assert sum(m["count"] for m in fees_after["monthly_trends"]) - sum(m["count"] for m in fees_before["monthly_trends"]) == 1

    tr_before, tr_after = before["transport_service"], after["transport_service"]
    assert tr_after["total_enrollments"] - tr_before["total_enrollments"] == 1
    paid_transport = D(str(tr_after["collected_fees"])) - D(str(tr_before["collected_fees"]))
    pending_transport = D(str(tr_after["pending_fees"])) - D(str(tr_before["pending_fees"]))
    assert paid_transport + pending_transport == D("7200")
    # Riders are counted on today (or the session's last day once it has ended); the
    # assignment runs all session, so the student rides either way.
    shuttle = [t for t in tr_after["transport_type_breakdown"] if t["name"] == "Test Shuttle"]
    assert shuttle and shuttle[0]["count"] == 1
    assert len(tr_after["monthly_trends"]) >= 12


async def test_admin_dashboard_fee_section(admin_api, transit, sunrise_session, fleet, tuition):
    before = await ok(await admin_api.get("/api/v1/dashboard/admin-dashboard-stats",
                                          params={"session_year_id": fleet["year_id"]}))
    sid = await _rider(admin_api, transit, sunrise_session, fleet, tuition)
    await _pay(admin_api, sid, "1500.00")
    after = await ok(await admin_api.get("/api/v1/dashboard/admin-dashboard-stats",
                                         params={"session_year_id": fleet["year_id"]}))
    assert "error" not in after["fees"], after["fees"]
    assert D(str(after["fees"]["collected_this_week"])) - D(str(before["fees"]["collected_this_week"])) == D("1500")
    assert D(str(after["fees"]["total_collected"])) - D(str(before["fees"]["total_collected"])) == D("1500")


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

async def test_fee_tracking_report_splits_fee_and_transport(admin_api, transit, sunrise_session, fleet, tuition):
    sid = await _rider(admin_api, transit, sunrise_session, fleet, tuition, first_name="Trackme")
    await _pay(admin_api, sid, "1000.00")
    report = await ok(await admin_api.get("/api/v1/reports/fee-tracking", params={
        "session_year_id": fleet["year_id"], "search": "Trackme"}))
    rows = [r for r in report["records"] if r["student_id"] == sid]
    assert len(rows) == 1
    row = rows[0]
    assert D(row["total_fee_amount"]) == D("12000")
    assert D(row["total_transport_amount"]) == D("7200")
    assert row["transport_opted"] is True and row["transport_type"] == "Test Shuttle"
    assert D(row["monthly_transport_fee"]) == D("600")
    assert D(row["total_paid"]) == D("1000")
    assert D(row["total_pending"]) == D("18200")

    no_transport = await ok(await admin_api.get("/api/v1/reports/fee-tracking", params={
        "session_year_id": fleet["year_id"], "search": "Trackme", "transport_opted": False}))
    assert all(r["student_id"] != sid for r in no_transport["records"])


async def test_daily_collection_report(admin_api, transit, sunrise_session, fleet, tuition):
    sid = await _rider(admin_api, transit, sunrise_session, fleet, tuition, first_name="Collectme")
    dues = await ok(await billing_api(admin_api).get(f"/students/{sid}/dues"))
    transport_due = next(d for d in dues if d["fee_head_id"] == fleet["transport_head_id"])
    tuition_due = next(d for d in dues if d["fee_head_id"] == tuition["heads"]["TUITION"])
    payment = await _pay(admin_api, sid, "1600.00", allocations=[
        {"due_id": transport_due["id"], "amount": "600.00"},
        {"due_id": tuition_due["id"], "amount": "1000.00"},
    ])
    report = await ok(await admin_api.get("/api/v1/reports/daily-collection", params={
        "from_date": TODAY.isoformat(), "to_date": TODAY.isoformat(), "search": "Collectme"}))
    rows = [r for r in report["records"] if r["payment_id"] == payment["id"]]
    assert len(rows) == 1
    row = rows[0]
    assert row["payment_type"] == "Fee + Transport"
    assert D(str(row["amount"])) == D("1600")
    assert D(str(row["transport_amount"])) == D("600") and D(str(row["fee_amount"])) == D("1000")
    assert row["receipt_number"] == payment["receipt_number"]

    # A fully reversed payment drops out of the report
    await ok(await billing_api(admin_api).post(f"/payments/{payment['id']}/reverse", json={
        "reversal_reason_id": 1, "remarks": "test"}), 201)
    report = await ok(await admin_api.get("/api/v1/reports/daily-collection", params={
        "from_date": TODAY.isoformat(), "to_date": TODAY.isoformat(), "search": "Collectme"}))
    assert all(r["payment_id"] != payment["id"] for r in report["records"])


# ---------------------------------------------------------------------------
# Students
# ---------------------------------------------------------------------------

async def test_student_profile_fee_status(admin_api, transit, sunrise_session, fleet, tuition):
    sid = await _rider(admin_api, transit, sunrise_session, fleet, tuition)
    await _pay(admin_api, sid, "2000.00")
    profile = await ok(await admin_api.get(f"/api/v1/students/{sid}/profile"))
    fee_status = profile["profile"]["fee_status"]
    assert D(str(fee_status["total_fees_paid"])) == D("2000")
    assert D(str(fee_status["total_fees_due"])) == D("17200")
    assert fee_status["fee_records_count"] == 24
    assert fee_status["status"] in ("Pending", "Overdue")


async def test_student_summaries(admin_api, transit, sunrise_session, fleet, tuition):
    sid = await _rider(admin_api, transit, sunrise_session, fleet, tuition)
    await _pay(admin_api, sid, "500.00")
    async with sunrise_session() as session:
        balance = (await fee_summary.student_balances(session, [sid], session_year_id=fleet["year_id"]))[sid]
        assert (balance["billed"], balance["paid"], balance["pending"]) == (D("19200"), D("500"), D("18700"))
        assert balance["last_payment_date"] == TODAY
        assert balance["dues"] == 24

        riding = await transport_summary.current_assignments(session, [sid], on_date=date(2026, 10, 1))
        assert riding[sid]["transport_type"] == "Test Shuttle" and riding[sid]["stop"] == "Stop A"
        assert riding[sid]["monthly_amount"] == D("600")
        assert await transport_summary.current_assignments(session, [sid], on_date=date(2026, 3, 31)) == {}  # before it starts


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

async def test_transport_types_come_from_the_school(admin_api, other_api, fleet):
    config = await ok(await admin_api.get("/api/v1/configuration/transport-management/"))
    names = {t["name"] for t in config["transport_types"]}
    assert {"E-Rickshaw", "Van", "Bus", "Test Shuttle"} <= names
    assert all("base_monthly_fee" not in t for t in config["transport_types"])

    other = await ok(await other_api.get("/api/v1/configuration/transport-management/"))
    assert "Test Shuttle" not in {t["name"] for t in other["transport_types"]}


# ---------------------------------------------------------------------------
# Sibling waiver recalculation
# ---------------------------------------------------------------------------

async def test_recalculate_waiver_reprices_unpaid_dues(admin_api, sunrise_session, fleet, tuition):
    """Sunrise's rule: in a family of 3, the youngest pays no tuition."""
    api = billing_api(admin_api)
    family = [
        await new_student(sunrise_session, fleet, date_of_birth=date(2012, 1, 1), first_name="Elder"),
        await new_student(sunrise_session, fleet, date_of_birth=date(2014, 1, 1), first_name="Middle"),
        await new_student(sunrise_session, fleet, date_of_birth=date(2016, 1, 1), first_name="Youngest"),
    ]
    for sid in family:
        await ok(await api.post("/plans/build", json={"session_year_id": fleet["year_id"], "student_id": sid}))
        await ok(await api.post("/dues/generate", json={"session_year_id": fleet["year_id"], "student_id": sid}))
    youngest = family[2]
    assert all(d["net_amount"] == "1000.00" for d in await ok(await api.get(f"/students/{youngest}/dues")))

    for sid in family[1:]:
        await ok(await admin_api.post(f"/api/v1/students/{family[0]}/siblings/link/{sid}"))
    result = await ok(await admin_api.put(f"/api/v1/students/{youngest}/siblings/recalculate-waiver"))
    assert "12 unpaid dues re-priced" in result["message"]
    dues = await ok(await api.get(f"/students/{youngest}/dues"))
    assert len(dues) == 12 and all(d["net_amount"] == "0.00" for d in dues)
    elder_dues = await ok(await api.get(f"/students/{family[0]}/dues"))
    assert all(d["net_amount"] == "1000.00" for d in elder_dues)


# ---------------------------------------------------------------------------
# Old routes
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("path", [
    "/api/v1/fees/structure", "/api/v1/fees/", "/api/v1/transport/enrollments", "/api/v1/transport/",
    "/api/v1/database/deploy-function",
])
async def test_old_routes_are_gone(admin_api, path):
    response = await admin_api.get(path)
    assert response.status_code in (404, 405), (path, response.status_code)
