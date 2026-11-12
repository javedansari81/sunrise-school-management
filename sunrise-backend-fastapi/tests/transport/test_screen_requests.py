"""
The request bodies the admin screens send (fees, transport, platform) and the
response fields they read. Fails when the API and the frontend drift apart.
"""
from tests.fees.test_ledger import _student  # noqa: F401

from .conftest import billing_api, new_student, ok
from tests.tenant.test_platform import platform_admin, platform_token  # noqa: F401


async def test_fee_screens(admin_api, refs, sunrise_session, fleet):
    year, c1 = refs["year_id"], refs["class_ids"][0]
    h = refs["heads"]
    sid = await new_student(sunrise_session, fleet, first_name="Zed")

    # Lookups the screens rely on
    cfg = await ok(await admin_api.get("/api/v1/configuration/fee-management/"))
    assert {"session_years", "classes", "payment_methods", "reversal_reasons"} <= set(cfg)
    assert "requires_reference" in cfg["payment_methods"][0] and "is_current" in cfg["session_years"][0]
    found = await ok(await admin_api.get("/api/v1/students", params={"is_active": "true", "per_page": 30, "search": "Zed"}))
    student = next(s for s in found["students"] if s["id"] == sid)
    assert {"admission_number", "first_name", "last_name", "class_id", "class_name"} <= set(student) and "total" in found

    heads = await ok(await admin_api.get("/fee-heads", params={"include_inactive": "true"}))
    assert {"is_system", "default_frequency", "category"} <= set(heads[0])

    # Structure editor: create, then save a draft (PATCH + PUT), publish
    s = await ok(await admin_api.post("/fee-structures", json={
        "session_year_id": year, "name": "Fee structure 2026-27", "description": None, "items": []}), 201)
    await ok(await admin_api.patch(f"/fee-structures/{s['id']}", json={"name": "FS", "description": None}))
    await ok(await admin_api.put(f"/fee-structures/{s['id']}/items", json=[
        {"fee_head_id": h["TUITION"], "class_id": c1, "amount": "1000.00", "frequency": "MONTHLY",
         "billing_months": None, "due_day": 10, "applies_to": "ALL"},
        {"fee_head_id": h["EXAM"], "class_id": None, "amount": "600.00", "frequency": "HALF_YEARLY",
         "billing_months": [9, 3], "due_day": 10, "applies_to": "ALL"},
    ]))
    await ok(await admin_api.post(f"/fee-structures/{s['id']}/publish"))
    listed = await ok(await admin_api.get("/fee-structures", params={"session_year_id": year}))
    assert {"status", "published_at", "created_at"} <= set(listed[0])
    await ok(await admin_api.post(f"/fee-structures/{s['id']}/copy", json={"session_year_id": year}), 201)

    # Billing run
    built = await ok(await admin_api.post("/plans/build", json={"session_year_id": year}))
    assert {"students", "created", "replaced", "ended", "unchanged", "dues_cancelled"} <= set(built)
    gen = await ok(await admin_api.post("/dues/generate", json={"session_year_id": year, "through_period": "2026-06-01"}))
    assert {"through_period", "created", "total_amount", "students", "repriced", "late_fees", "credit_applied"} <= set(gen)
    late = await ok(await admin_api.post("/late-fees/apply", json={"as_of": "2026-07-01", "session_year_id": year}))
    assert {"enabled", "as_of", "created", "total_amount"} <= set(late)

    # Desk
    dues = await ok(await admin_api.get(f"/students/{sid}/dues", params={"session_year_id": year}))
    open_dues = [d for d in dues if d["status"] in ("PENDING", "PARTIAL")]
    assert {"balance", "net_amount", "concession_amount", "line_type", "period", "due_date"} <= set(dues[0])
    method = cfg["payment_methods"][0]["id"]
    pay = await ok(await admin_api.post("/payments", json={
        "student_id": sid, "session_year_id": year, "amount": "1500.00", "payment_method_id": method,
        "payment_date": "2026-06-05", "due_ids": [open_dues[0]["id"]], "send_receipt": False}), 201)
    assert {"receipt_number", "unallocated"} <= set(pay) and pay["unallocated"] == "500.00"
    assert (await admin_api.get(f"/payments/{pay['id']}/receipt.pdf")).content[:4] == b"%PDF"
    bal = await ok(await admin_api.get(f"/students/{sid}/balance"))
    assert {"balance", "overdue", "total_paid", "total_due", "credit", "open_dues"} <= set(bal)
    ledger = await ok(await admin_api.get(f"/students/{sid}/ledger", params={"session_year_id": year}))
    assert {"entries", "total_debit", "total_credit", "balance"} <= set(ledger)
    assert {"date", "type", "description", "debit", "credit", "balance", "reference"} <= set(ledger["entries"][0])
    plan = await ok(await admin_api.get(f"/students/{sid}/plan", params={"session_year_id": year}))
    assert {"source", "start_period", "end_period", "frequency", "is_active"} <= set(plan[0])
    line = await ok(await admin_api.post(f"/students/{sid}/plan-lines", json={
        "session_year_id": year, "fee_head_id": h["EXAM"], "amount": "250.00", "frequency": "ONE_TIME",
        "start_period": "2026-06-01"}), 201)
    await ok(await admin_api.post("/dues/generate", json={"session_year_id": year, "student_id": sid}))
    await ok(await admin_api.post(f"/plan-lines/{line['id']}/end", json={}))
    rev = await ok(await admin_api.post(f"/payments/{pay['id']}/reverse", json={
        "reversal_reason_id": cfg["reversal_reasons"][0]["id"]}), 201)
    assert rev["kind"] == "REVERSAL" and rev["reverses_payment_id"] == pay["id"]
    pays = await ok(await admin_api.get(f"/students/{sid}/payments", params={"session_year_id": year}))
    assert [p["kind"] for p in pays] == ["PAYMENT", "REVERSAL"]
    unpaid = next(d for d in await ok(await admin_api.get(f"/students/{sid}/dues", params={"session_year_id": year}))
                  if d["status"] == "PENDING")
    await ok(await admin_api.post(f"/dues/{unpaid['id']}/cancel", json={"reason": "test"}))

    # Reports
    col = await ok(await admin_api.get("/reports/collection", params={"date_from": "2026-06-01", "date_to": "2026-06-30"}))
    assert {"net", "received", "reversed", "payments", "by_day", "by_method", "by_head", "not_allocated"} <= set(col)
    pend = await ok(await admin_api.get("/reports/pending-by-class", params={"session_year_id": year}))
    assert {"classes", "total_pending", "total_overdue", "as_of"} <= set(pend)
    assert {"class_name", "students_with_dues", "pending", "overdue"} <= set(pend["classes"][0])
    assert {"ok", "dues_checked", "payments_checked"} <= set(await ok(await admin_api.get("/reports/consistency")))


async def test_transport_screens(transit, fleet, sunrise_session):
    year, t = fleet["year_id"], fleet["type_id"]
    sid = await new_student(sunrise_session, fleet)

    # Setup dialogs, with the nulls the forms send
    v = await ok(await transit.patch(f"/vehicles/{fleet['vehicle_id']}", json={
        "transport_type_id": t, "registration_number": "UP91 T 0001", "capacity": None, "driver_name": None,
        "driver_phone": None, "remarks": None, "is_active": True}))
    assert v["capacity"] is None
    r = await ok(await transit.post("/routes", json={"name": "South", "is_active": True}), 201)
    await ok(await transit.patch(f"/routes/{r['id']}", json={"name": "South", "description": None, "vehicle_id": None, "is_active": True}))
    s1 = await ok(await transit.post(f"/routes/{r['id']}/stops", json={"name": "S1", "pickup_time": "07:05", "is_active": True}), 201)
    s2 = await ok(await transit.post(f"/routes/{r['id']}/stops", json={"name": "S2", "distance_km": "4.00", "is_active": True}), 201)
    await ok(await transit.patch(f"/stops/{s1['id']}", json={"name": "S1", "distance_km": None, "pickup_time": None, "drop_time": "14:10", "is_active": True}))
    assert [x["id"] for x in (await ok(await transit.put(f"/routes/{r['id']}/stops/order", json={"stop_ids": [s2["id"], s1["id"]]})))["stops"]]
    assert (await transit.delete(f"/stops/{s1['id']}")).status_code == 204
    await ok(await transit.patch(f"/rates/{fleet['rates']['flat']['id']}", json={"monthly_amount": "550.00", "description": None}))
    await ok(await transit.patch(f"/rates/{fleet['rates']['near']['id']}", json={
        "monthly_amount": "600.00", "description": None, "distance_from_km": "0.00", "distance_to_km": "5.00"}))
    await ok(await transit.patch(f"/rates/{fleet['rates']['flat']['id']}", json={"is_active": True}))

    # Assign dialog
    q = await ok(await transit.post("/rates/quote", json={"session_year_id": year, "route_id": fleet["route_id"], "route_stop_id": fleet["stops"]["Stop A"], "transport_type_id": t}))
    assert q["monthly_amount"] == "600.00"
    res = await ok(await transit.post("/assignments", json={
        "transport_type_id": t, "route_id": fleet["route_id"], "route_stop_id": fleet["stops"]["Stop A"],
        "allow_over_capacity": False, "student_id": sid, "session_year_id": year, "start_date": "2026-04-01"}), 201)
    a = res["assignment"]
    assert {"student_name", "admission_number", "pauses", "amount_overridden"} <= set(a) and "warnings" in res
    # Change dialog: every field sent, nulls included
    ch = await ok(await transit.post(f"/assignments/{a['id']}/change", json={
        "transport_type_id": t, "route_id": fleet["route_id"], "route_stop_id": fleet["stops"]["Stop B"], "distance_km": None,
        "pickup_location": None, "drop_location": None, "monthly_amount": None, "remarks": None,
        "allow_over_capacity": False, "effective_date": "2026-08-01"}))
    new = ch["assignment"]
    assert new["monthly_amount"] == "950.00" and new["route_stop_id"] == fleet["stops"]["Stop B"]
    # No fixed route: route cleared, priced by the vehicle type
    ch2 = await ok(await transit.post(f"/assignments/{new['id']}/change", json={
        "transport_type_id": t, "route_id": None, "route_stop_id": None, "distance_km": None,
        "pickup_location": "Gate", "drop_location": None, "monthly_amount": "700.00", "remarks": None,
        "allow_over_capacity": False, "effective_date": "2026-10-01"}))
    cur = ch2["assignment"]
    assert cur["route_id"] is None and cur["monthly_amount"] == "700.00" and cur["amount_overridden"]

    p = await ok(await transit.post(f"/assignments/{cur['id']}/pauses", json={"from_period": "2026-12-01", "to_period": "2026-12-01"}), 201)
    pause = p["assignment"]["pauses"][0]
    assert {"id", "from_period", "to_period", "is_active"} <= set(pause)
    await ok(await transit.delete(f"/pauses/{pause['id']}"))
    await ok(await transit.post(f"/assignments/{cur['id']}/discontinue", json={"end_date": "2027-01-31"}))
    rows = await ok(await transit.get("/assignments", params={"session_year_id": year, "active_on": "2026-11-15"}))
    assert [x["id"] for x in rows] == [cur["id"]]
    roster = await ok(await transit.get(f"/routes/{fleet['route_id']}/roster", params={"on_date": "2026-09-01"}))
    assert roster["riding"] == 1 and roster["stops"][1]["riders"][0]["student_name"]
    assert (await transit.post("/rates/copy", json={"from_session_year_id": year, "to_session_year_id": year})).status_code == 422


async def test_platform_screen(client_factory, platform_token, schools):  # noqa: F811
    auth = {"Authorization": f"Bearer {platform_token}"}
    async with client_factory() as client:
        r = await client.post("/api/v1/platform/schools", headers=auth, json={
            "code": "greenfield", "name": "Greenfield School", "short_name": None, "phone": None, "email": None,
            "address": None, "website": None, "logo_url": None, "academic_year_start_month": 4,
            "admin": {"first_name": "A", "last_name": "B", "email": "admin@greenfieldschool.in", "password": "secret-123"}})
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["admin"]["email"] == "admin@greenfieldschool.in" and "copied_lists" in body
        sid = body["school"]["id"]
        r = await client.patch(f"/api/v1/platform/schools/{sid}", headers=auth, json={
            "code": "greenfield", "name": "Greenfield High", "short_name": "Greenfield", "phone": "999", "email": None,
            "address": None, "website": None, "logo_url": None, "academic_year_start_month": 4})
        assert r.status_code == 200 and r.json()["short_name"] == "Greenfield", r.text
        rows = (await client.get("/api/v1/platform/schools", headers=auth, params={"search": "green"})).json()["schools"]
        assert {"students", "teachers", "users", "status", "created_at"} <= set(rows[0])
        assert (await client.post(f"/api/v1/platform/schools/{sid}/suspend", headers=auth)).json()["status"] == "SUSPENDED"
    async with client_factory("greenfield") as client:
        assert (await client.get("/api/v1/public/school")).status_code == 403
    async with client_factory("nosuchschool") as client:
        assert (await client.get("/api/v1/public/school")).status_code == 404
