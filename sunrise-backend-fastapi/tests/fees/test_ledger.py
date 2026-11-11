"""
Steps C and D: plans, dues, siblings, concessions, late fees, payments, credit,
reversals and receipt numbering.

Session 2026-27 runs April 2026 to March 2027. Every test publishes this price list:
    class 1: tuition 1000 / month        class 2: tuition 1700 / month
    all classes: exam 600 in September and March, admission 5000 once (new students)
"""
import asyncio
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import select, text, update
from sqlalchemy.exc import DBAPIError

from app.core.tenant import global_sql
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import settings
from app.core.tenant import set_session_school
from app.models.school import SchoolSetting
from app.models.student import Student
from app.modules.fees.service.payments import next_receipt_number

from .conftest import add_student

D = Decimal


@pytest.fixture
async def priced(admin_api, refs):
    c1, c2 = refs["class_ids"]
    h = refs["heads"]
    r = await admin_api.post("/fee-structures", json={
        "session_year_id": refs["year_id"], "name": "2026-27", "items": [
            {"fee_head_id": h["TUITION"], "class_id": c1, "amount": "1000.00"},
            {"fee_head_id": h["TUITION"], "class_id": c2, "amount": "1700.00"},
            {"fee_head_id": h["EXAM"], "amount": "600.00", "frequency": "HALF_YEARLY", "billing_months": [9, 3]},
            {"fee_head_id": h["ADMISSION"], "amount": "5000.00", "frequency": "ONE_TIME", "applies_to": "NEW_STUDENTS"},
        ]})
    assert r.status_code == 201, r.text
    assert (await admin_api.post(f"/fee-structures/{r.json()['id']}/publish")).status_code == 200
    return refs


async def _student(sunrise_session, refs, **kw):
    kw.setdefault("class_id", refs["class_ids"][0])
    async with sunrise_session() as session:
        s = await add_student(session, session_year_id=refs["year_id"], **kw)
        await session.commit()
        return s.id


async def _build(api, refs, **kw):
    r = await api.post("/plans/build", json={"session_year_id": refs["year_id"], **kw})
    assert r.status_code == 200, r.text
    return r.json()


async def _generate(api, refs, through, **kw):
    r = await api.post("/dues/generate", json={"session_year_id": refs["year_id"], "through_period": through, **kw})
    assert r.status_code == 200, r.text
    return r.json()


async def _dues(api, student_id, **params):
    r = await api.get(f"/students/{student_id}/dues", params=params)
    assert r.status_code == 200, r.text
    return r.json()


def _by(dues, head_id):
    return [d for d in dues if d["fee_head_id"] == head_id]


async def _pay(api, student_id, amount, **kw):
    r = await api.post("/payments", json={"student_id": student_id, "amount": amount, "payment_method_id": 1, **kw})
    assert r.status_code == 201, r.text
    return r.json()


# ---------------------------------------------------------------------------
# Plans and dues
# ---------------------------------------------------------------------------

async def test_build_plans_and_generate_dues(admin_api, priced, sunrise_session):
    h = priced["heads"]
    old = await _student(sunrise_session, priced, admission_date=date(2024, 4, 1))
    new = await _student(sunrise_session, priced, admission_date=date(2026, 6, 15))

    built = await _build(admin_api, priced)
    assert (built["students"], built["created"]) == (2, 5)  # old: tuition, exam; new: + admission
    again = await _build(admin_api, priced)
    assert (again["created"], again["unchanged"], again["replaced"]) == (0, 5, 0)

    gen = await _generate(admin_api, priced, "2026-06-01")
    assert gen["created"] == 5  # old: tuition Apr-Jun; new: tuition Jun, admission Jun
    assert D(gen["total_amount"]) == D("9000.00")
    assert (await _generate(admin_api, priced, "2026-06-01"))["created"] == 0  # nothing twice

    new_dues = await _dues(admin_api, new)
    assert [d["period"] for d in _by(new_dues, h["TUITION"])] == ["2026-06-01"]
    admission = _by(new_dues, h["ADMISSION"])[0]
    assert admission["net_amount"] == "5000.00" and admission["due_date"] == "2026-06-10"

    await _generate(admin_api, priced, "2027-03-01")
    old_dues = await _dues(admin_api, old)
    assert len(_by(old_dues, h["TUITION"])) == 12
    assert [d["period"] for d in _by(old_dues, h["EXAM"])] == ["2026-09-01", "2027-03-01"]
    assert not _by(old_dues, h["ADMISSION"])


async def test_build_without_published_structure_fails(admin_api, refs):
    r = await admin_api.post("/plans/build", json={"session_year_id": refs["year_id"]})
    assert r.status_code == 422


async def test_class_change_mid_session(admin_api, priced, sunrise_session):
    h = priced["heads"]
    c2 = priced["class_ids"][1]
    sid = await _student(sunrise_session, priced)
    await _build(admin_api, priced)
    await _generate(admin_api, priced, "2026-08-01")  # Apr-Aug at 1000
    july = next(d for d in _by(await _dues(admin_api, sid), h["TUITION"]) if d["period"] == "2026-07-01")
    await _pay(admin_api, sid, "1000.00", due_ids=[july["id"]])  # July is paid in advance

    async with sunrise_session() as session:
        await session.execute(update(Student).where(Student.id == sid).values(class_id=c2))
        await session.commit()
    built = await _build(admin_api, priced, effective_from="2026-07-01")
    assert built["replaced"] == 1 and built["dues_cancelled"] == 1  # August (unpaid); July is paid, kept

    await _generate(admin_api, priced, "2026-09-01")
    tuition = {d["period"]: d for d in _by(await _dues(admin_api, sid), h["TUITION"]) if d["status"] != "CANCELLED"}
    assert tuition["2026-06-01"]["net_amount"] == "1000.00"
    assert tuition["2026-07-01"]["net_amount"] == "1000.00" and tuition["2026-07-01"]["status"] == "PAID"
    assert tuition["2026-08-01"]["net_amount"] == "1700.00"
    assert tuition["2026-09-01"]["net_amount"] == "1700.00"

    plan = (await admin_api.get(f"/students/{sid}/plan", params={"session_year_id": priced["year_id"]})).json()
    tuition_lines = sorted((p for p in plan if p["fee_head_id"] == h["TUITION"]), key=lambda p: p["start_period"])
    assert [(p["start_period"], p["end_period"], p["amount"]) for p in tuition_lines] == [
        ("2026-04-01", "2026-06-01", "1000.00"), ("2026-07-01", None, "1700.00")]


async def test_manual_plan_line_and_ending_it(admin_api, priced, sunrise_session):
    h = priced["heads"]
    sid = await _student(sunrise_session, priced)
    r = await admin_api.post(f"/students/{sid}/plan-lines", json={
        "session_year_id": priced["year_id"], "fee_head_id": h["EXAM"], "amount": "300.00",
        "start_period": "2026-07-01", "remarks": "Re-exam"})
    assert r.status_code == 201, r.text
    line = r.json()
    await _generate(admin_api, priced, "2026-07-01")
    re_exam = [d for d in await _dues(admin_api, sid) if d["student_fee_plan_id"] == line["id"]]
    assert [(d["period"], d["net_amount"]) for d in re_exam] == [("2026-07-01", "300.00")]

    ended = await admin_api.post(f"/plan-lines/{line['id']}/end", json={"reason": "Charged by mistake"})
    assert ended.status_code == 200 and ended.json()["is_active"] is False
    re_exam = [d for d in await _dues(admin_api, sid) if d["student_fee_plan_id"] == line["id"]]
    assert re_exam[0]["status"] == "CANCELLED"


async def test_cancel_due(admin_api, priced, sunrise_session):
    sid = await _student(sunrise_session, priced)
    await _build(admin_api, priced)
    await _generate(admin_api, priced, "2026-05-01")
    april, may = await _dues(admin_api, sid)
    await _pay(admin_api, sid, "100.00", due_ids=[may["id"]])
    assert (await admin_api.post(f"/dues/{april['id']}/cancel", json={"reason": "Fee holiday"})).json()["status"] == "CANCELLED"
    assert (await admin_api.post(f"/dues/{may['id']}/cancel", json={"reason": "x"})).status_code == 409


# ---------------------------------------------------------------------------
# Siblings and concessions
# ---------------------------------------------------------------------------

async def test_sibling_concession_follows_linked_siblings(admin_api, priced, sunrise_session):
    """Sunrise rule: with 3 siblings the youngest gets 100% off tuition."""
    h = priced["heads"]
    eldest = await _student(sunrise_session, priced, date_of_birth=date(2012, 1, 1), first_name="Eldest")
    middle = await _student(sunrise_session, priced, date_of_birth=date(2014, 1, 1), first_name="Middle")
    youngest = await _student(sunrise_session, priced, date_of_birth=date(2016, 1, 1), first_name="Youngest")

    # Linking is by hand; linking the youngest to the eldest pulls in the eldest's family
    assert (await admin_api.post(f"/api/v1/students/{eldest}/siblings/link/{middle}")).status_code == 200
    assert (await admin_api.post(f"/api/v1/students/{youngest}/siblings/link/{eldest}")).status_code == 200
    family = (await admin_api.get(f"/api/v1/students/{middle}/siblings")).json()
    assert sorted(s["sibling_student_id"] for s in family) == sorted([eldest, youngest])

    preview = (await admin_api.get(f"/students/{youngest}/sibling-concession",
                                   params={"session_year_id": priced["year_id"]})).json()
    assert (preview["family_size"], preview["position_from_eldest"], preview["percent"]) == (3, 3, "100.00")
    assert preview["sibling_ids_eldest_first"] == [eldest, middle, youngest]

    await _build(admin_api, priced)
    await _generate(admin_api, priced, "2026-09-01")
    young_dues = await _dues(admin_api, youngest)
    april = next(d for d in _by(young_dues, h["TUITION"]) if d["period"] == "2026-04-01")
    assert (april["concession_amount"], april["net_amount"], april["status"]) == ("1000.00", "0.00", "WAIVED")
    exam = _by(young_dues, h["EXAM"])[0]
    assert exam["concession_amount"] == "0.00"  # the rule covers tuition only
    assert all(d["concession_amount"] == "0.00" for d in await _dues(admin_api, eldest))

    # Remove the middle child: 2 siblings left, no concession; unpaid dues are re-priced
    assert (await admin_api.delete(f"/api/v1/students/{eldest}/siblings/{middle}")).status_code == 200
    regen = await _generate(admin_api, priced, "2026-09-01")
    assert regen["repriced"] == 6  # youngest's tuition April-September
    april = next(d for d in _by(await _dues(admin_api, youngest), h["TUITION"]) if d["period"] == "2026-04-01")
    assert (april["net_amount"], april["status"]) == ("1000.00", "PENDING")


async def test_sibling_links_are_admin_only_and_suggestions_do_not_link(admin_api, staff_api, priced, sunrise_session):
    a = await _student(sunrise_session, priced, father_phone="9000000001")
    b = await _student(sunrise_session, priced, father_phone="9000000001")
    suggested = await admin_api.get(f"/api/v1/students/{a}/siblings/suggestions")
    assert suggested.status_code == 200, suggested.text
    assert [s["student_id"] for s in suggested.json()["detected_siblings"]] == [b]
    assert (await admin_api.get(f"/api/v1/students/{a}/siblings")).json() == []  # nothing linked

    assert (await staff_api.post(f"/api/v1/students/{a}/siblings/link/{b}")).status_code == 403
    r = await admin_api.post(f"/api/v1/students/{a}/siblings/link/{b}", params={"relationship_type": "TWIN"})
    assert r.status_code == 200, r.text
    assert (await admin_api.get(f"/api/v1/students/{a}/siblings/suggestions")).json()["detected_siblings"] == []
    r = await admin_api.patch(f"/api/v1/students/{a}/siblings/{b}", json={"relationship_type": "HALF_SIBLING"})
    assert r.status_code == 200
    rel = (await admin_api.get(f"/api/v1/students/{b}/siblings")).json()[0]
    assert rel["relationship_type"] == "HALF_SIBLING"


async def test_student_concessions(admin_api, priced, sunrise_session):
    h = priced["heads"]
    sid = await _student(sunrise_session, priced)
    r = await admin_api.post(f"/students/{sid}/concessions", json={
        "session_year_id": priced["year_id"], "concession_type": "SCHOLARSHIP", "value_type": "PERCENT",
        "value": "50", "fee_head_ids": [h["TUITION"]], "reason": "Merit scholarship"})
    assert r.status_code == 201, r.text
    scholarship = r.json()
    assert scholarship["approved_by"] is not None
    staff_rule = await admin_api.post("/concession-rules", json={
        "name": "Staff child", "concession_type": "STAFF", "value_type": "FIXED", "value": "200"})
    assert staff_rule.status_code == 201, staff_rule.text
    r = await admin_api.post(f"/students/{sid}/concessions", json={
        "session_year_id": priced["year_id"], "concession_rule_id": staff_rule.json()["id"],
        "fee_head_ids": [h["TUITION"]], "reason": "Parent is a teacher", "start_period": "2026-05-01"})
    assert r.status_code == 201, r.text

    await _build(admin_api, priced)
    await _generate(admin_api, priced, "2026-05-01")
    april, may = _by(await _dues(admin_api, sid), h["TUITION"])
    assert april["concession_amount"] == "500.00"  # 50%
    assert may["concession_amount"] == "700.00"  # 50% + 200 fixed

    await admin_api.post(f"/student-concessions/{scholarship['id']}/revoke", json={"reason": "Ended"})
    assert (await _generate(admin_api, priced, "2026-05-01"))["repriced"] == 2
    april, may = _by(await _dues(admin_api, sid), h["TUITION"])
    assert (april["concession_amount"], may["concession_amount"]) == ("0.00", "200.00")


async def test_concession_rule_validation(admin_api, refs):
    # Only one active sibling rule (Sunrise already has one)
    r = await admin_api.post("/concession-rules", json={
        "name": "Second sibling rule", "concession_type": "SIBLING",
        "tiers": [{"min_siblings": 2, "position_from": 2, "percent": "10"}]})
    assert r.status_code == 409
    r = await admin_api.post("/concession-rules", json={"name": "No tiers", "concession_type": "SIBLING"})
    assert r.status_code == 422
    r = await admin_api.post("/concession-rules", json={
        "name": "Too much", "concession_type": "CUSTOM", "value_type": "PERCENT", "value": "150"})
    assert r.status_code == 422

    # The sibling tiers are editable, e.g. the plan's default: 2nd child onwards 25%
    rules = (await admin_api.get("/concession-rules")).json()
    sibling = next(x for x in rules if x["concession_type"] == "SIBLING")
    r = await admin_api.patch(f"/concession-rules/{sibling['id']}", json={
        "tiers": [{"min_siblings": 2, "position_basis": "ELDEST", "position_from": 2, "percent": "25"}]})
    assert r.status_code == 200 and r.json()["tiers"][0]["percent"] == "25"


# ---------------------------------------------------------------------------
# Late fees
# ---------------------------------------------------------------------------

async def _late_fee_settings(sunrise_session, **values):
    async with sunrise_session() as session:
        for key, value in values.items():
            await session.execute(update(SchoolSetting).where(SchoolSetting.key == f"fee.late_fee.{key}").values(value=value))
        await session.commit()


async def test_late_fees(admin_api, priced, sunrise_session):
    h = priced["heads"]
    sid = await _student(sunrise_session, priced)
    await _build(admin_api, priced)
    await _generate(admin_api, priced, "2026-05-01")

    off = await admin_api.post("/late-fees/apply", json={"as_of": "2026-06-01"})
    assert off.json()["enabled"] is False and off.json()["created"] == 0

    await _late_fee_settings(sunrise_session, enabled="true", mode="FIXED", value="50", grace_days="7")
    # April is due 10 April: 7 grace days end on the 17th
    assert (await admin_api.post("/late-fees/apply", json={"as_of": "2026-04-17"})).json()["created"] == 0
    r = (await admin_api.post("/late-fees/apply", json={"as_of": "2026-04-18"})).json()
    assert (r["created"], r["total_amount"]) == (1, "50.00")
    assert (await admin_api.post("/late-fees/apply", json={"as_of": "2026-04-30"})).json()["created"] == 0  # once a month

    await _late_fee_settings(sunrise_session, mode="PERCENT", value="10")
    r = (await admin_api.post("/late-fees/apply", json={"as_of": "2026-05-20"})).json()
    assert (r["created"], r["total_amount"]) == (1, "100.00")  # 10% of May's 1000
    late = _by(await _dues(admin_api, sid), h["LATE_FEE"])
    assert [(d["period"], d["net_amount"], d["line_type"]) for d in late] == [
        ("2026-04-01", "50.00", "LATE_FEE"), ("2026-05-01", "100.00", "LATE_FEE")]


# ---------------------------------------------------------------------------
# Payments, credit, reversals
# ---------------------------------------------------------------------------

async def _three_months(admin_api, priced, sunrise_session):
    sid = await _student(sunrise_session, priced)
    await _build(admin_api, priced)
    await _generate(admin_api, priced, "2026-06-01")
    return sid


async def test_payment_allocates_oldest_first_with_one_receipt_series(admin_api, priced, sunrise_session):
    sid = await _three_months(admin_api, priced, sunrise_session)
    first = await _pay(admin_api, sid, "2500.00")
    assert first["receipt_number"] == "SUN/2026-27/000001"
    assert (first["allocated"], first["unallocated"]) == ("2500.00", "0.00")
    april, may, june = await _dues(admin_api, sid)
    assert [april["status"], may["status"], june["status"]] == ["PAID", "PAID", "PARTIAL"]
    assert june["paid_amount"] == "500.00"

    second = await _pay(admin_api, sid, "100.00")
    assert second["receipt_number"] == "SUN/2026-27/000002"
    balance = (await admin_api.get(f"/students/{sid}/balance", params={"as_of": "2026-07-01"})).json()
    assert (balance["total_due"], balance["total_paid"], balance["balance"], balance["overdue"]) == (
        "3000.00", "2600.00", "400.00", "400.00")


async def test_payment_to_chosen_dues(admin_api, priced, sunrise_session):
    sid = await _three_months(admin_api, priced, sunrise_session)
    april, may, june = await _dues(admin_api, sid)
    paid = await _pay(admin_api, sid, "1300.00", allocations=[
        {"due_id": june["id"], "amount": "1000.00"}, {"due_id": april["id"], "amount": "300.00"}])
    assert sorted((a["student_due_id"], a["amount"]) for a in paid["allocations"]) == sorted(
        [(june["id"], "1000.00"), (april["id"], "300.00")])
    april, may, june = await _dues(admin_api, sid)
    assert [april["status"], may["status"], june["status"]] == ["PARTIAL", "PENDING", "PAID"]

    bad = await admin_api.post("/payments", json={"student_id": sid, "amount": "100.00", "payment_method_id": 1,
                                                  "allocations": [{"due_id": may["id"], "amount": "200.00"}]})
    assert bad.status_code == 422  # allocations above the amount paid
    paid_due = await admin_api.post("/payments", json={"student_id": sid, "amount": "10.00", "payment_method_id": 1,
                                                       "due_ids": [june["id"]]})
    assert paid_due.status_code == 422  # June is no longer open


async def test_advance_payment_is_credit_applied_to_new_dues(admin_api, priced, sunrise_session):
    sid = await _three_months(admin_api, priced, sunrise_session)
    paid = await _pay(admin_api, sid, "4500.00")
    assert paid["unallocated"] == "1500.00"
    assert (await admin_api.get(f"/students/{sid}/balance")).json()["credit"] == "1500.00"

    gen = await _generate(admin_api, priced, "2026-08-01")  # July, August
    assert gen["credit_applied"] == "1500.00"
    july, august = (await _dues(admin_api, sid))[3:]
    assert (july["status"], august["status"], august["paid_amount"]) == ("PAID", "PARTIAL", "500.00")
    assert (await admin_api.get(f"/students/{sid}/balance")).json()["credit"] == "0.00"


async def test_full_and_partial_reversals(admin_api, priced, sunrise_session):
    sid = await _three_months(admin_api, priced, sunrise_session)
    paid = await _pay(admin_api, sid, "3300.00")  # all 3 months + 300 credit

    # Partial: 500 = 300 from credit, then 200 from the latest due (June)
    r = await admin_api.post(f"/payments/{paid['id']}/reverse", json={"amount": "500.00", "reversal_reason_id": 1})
    assert r.status_code == 201, r.text
    reversal = r.json()
    assert (reversal["kind"], reversal["amount"], reversal["receipt_number"]) == ("REVERSAL", "-500.00", None)
    assert [(a["amount"], a["is_reversal"]) for a in reversal["reversal_allocations"]] == [("-200.00", True)]
    april, may, june = await _dues(admin_api, sid)
    assert (june["status"], june["paid_amount"]) == ("PARTIAL", "800.00")

    detail = (await admin_api.get(f"/payments/{paid['id']}")).json()
    assert (detail["reversed"], detail["unallocated"]) == ("500.00", "0.00")

    too_much = await admin_api.post(f"/payments/{paid['id']}/reverse", json={"amount": "5000.00", "reversal_reason_id": 1})
    assert too_much.status_code == 422
    # Full: the remaining 2800
    full = await admin_api.post(f"/payments/{paid['id']}/reverse", json={"reversal_reason_id": 2, "remarks": "Bounced"})
    assert full.status_code == 201 and full.json()["amount"] == "-2800.00"
    assert all(d["status"] == "PENDING" and d["paid_amount"] == "0.00" for d in await _dues(admin_api, sid))
    assert (await admin_api.post(f"/payments/{paid['id']}/reverse", json={"reversal_reason_id": 1})).status_code == 409
    assert (await admin_api.post(f"/payments/{full.json()['id']}/reverse", json={"reversal_reason_id": 1})).status_code == 422

    balance = (await admin_api.get(f"/students/{sid}/balance")).json()
    assert (balance["total_paid"], balance["credit"]) == ("0.00", "0.00")
    payments = (await admin_api.get(f"/students/{sid}/payments")).json()
    assert [p["kind"] for p in payments] == ["PAYMENT", "REVERSAL", "REVERSAL"]


async def test_payment_permissions_and_isolation(admin_api, staff_api, other_api, priced, sunrise_session):
    sid = await _three_months(admin_api, priced, sunrise_session)
    denied = await staff_api.post("/payments", json={"student_id": sid, "amount": "10.00", "payment_method_id": 1})
    assert denied.status_code == 403
    paid = await _pay(admin_api, sid, "10.00")
    assert (await other_api.get(f"/payments/{paid['id']}")).status_code == 404
    assert (await other_api.get(f"/students/{sid}/dues")).status_code == 404
    assert (await other_api.post("/payments", json={"student_id": sid, "amount": "10.00", "payment_method_id": 1})).status_code == 404
    assert (await other_api.post(f"/payments/{paid['id']}/reverse", json={"reversal_reason_id": 1})).status_code == 404


async def test_receipt_numbers_are_per_school_and_session(admin_api, priced, sunrise_session, make_session, schools):
    sid = await _three_months(admin_api, priced, sunrise_session)
    assert (await _pay(admin_api, sid, "10.00"))["receipt_number"] == "SUN/2026-27/000001"
    async with sunrise_session() as session:
        assert await next_receipt_number(session, priced["year_id"] - 1) == "SUN/2025-26/000001"
        assert await next_receipt_number(session, priced["year_id"]) == "SUN/2026-27/000002"


async def test_receipt_number_is_locked_until_the_payment_commits(priced, schools):
    """
    Two cashiers at once: the second waits for the first one's receipt number
    instead of taking the same one. Uses two real connections; both roll back.
    """
    connect_args = {"server_settings": {"search_path": settings.DB_SCHEMA}}
    if settings.DB_SSL:
        connect_args["ssl"] = settings.DB_SSL
    engine = create_async_engine(
        settings.ASYNCPG_DSN.replace("postgresql://", "postgresql+asyncpg://", 1), connect_args=connect_args)
    try:
        async with engine.connect() as c1, engine.connect() as c2:
            t1, t2 = await c1.begin(), await c2.begin()
            s1, s2 = AsyncSession(bind=c1), AsyncSession(bind=c2)
            set_session_school(s1, schools["sunrise_id"])
            set_session_school(s2, schools["sunrise_id"])
            # The test transaction (another connection) is open too, so use a session it never touched
            year = priced["year_id"] - 2
            first = await next_receipt_number(s1, year)
            assert first.endswith("/000001")
            await s2.execute(global_sql("SET LOCAL lock_timeout = '300ms'"))
            with pytest.raises(DBAPIError, match="lock"):
                await next_receipt_number(s2, year)
            await t2.rollback()
            await t1.rollback()
            await asyncio.gather(s1.close(), s2.close())
    finally:
        await engine.dispose()
