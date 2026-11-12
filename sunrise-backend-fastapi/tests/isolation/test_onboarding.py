"""
A second school onboarded end to end (Phase 7), through the API only:

platform admin creates the school -> its admin logs in on its own subdomain ->
branding and copied lists -> fee structure, plans, dues -> transport fleet, rate and
rider -> payment with the school's own receipt series -> the student logs in and
sees their statement -> Settings turns the shop on for this school only.

At every step Sunrise (school 1) and the new school must not see each other.
Everything runs in the test transaction and is rolled back.
"""
import pytest

from app.modules.fees.provisioning import default_receipt_prefix
from tests.tenant.test_platform import (  # noqa: F401  (fixtures)
    PLATFORM_EMAIL, PLATFORM_PASSWORD, platform_admin, platform_token,
)

from .conftest import Api, TransitApi, ok

CODE = "pinecrest"
ADMIN = {"email": "admin@pinecrest.in", "password": "Pine-Admin-1", "first_name": "Pine", "last_name": "Admin"}
SCHOOL = {"code": CODE, "name": "Pinecrest Academy", "short_name": "Pinecrest", "phone": "9123456780",
          "admin": ADMIN}


async def _login(client_factory, code, email, password) -> dict:
    async with client_factory(code) as client:
        r = await client.post("/api/v1/auth/login-json", json={"email": email, "password": password})
        assert r.status_code == 200, r.text
        return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
async def pinecrest(client_factory, platform_token, schools):
    async with client_factory() as client:
        created = await ok(await client.post("/api/v1/platform/schools", json=SCHOOL,
                                             headers={"Authorization": f"Bearer {platform_token}"}), 201)
    headers = await _login(client_factory, CODE, ADMIN["email"], ADMIN["password"])
    return {"id": created["school"]["id"], "api": Api(client_factory, CODE, headers),
            "transit": TransitApi(client_factory, CODE, headers)}


async def test_second_school_onboarded_end_to_end(client_factory, pinecrest, admin_api, schools):
    api, transit = pinecrest["api"], pinecrest["transit"]

    # Branding and the admin's own school
    async with client_factory(CODE) as client:
        public = await ok(await client.get("/api/v1/public/school"))
    assert public["name"] == SCHOOL["name"]
    me = await ok(await api.get("/api/v1/auth/me"))
    assert me["email"] == ADMIN["email"]

    # Lists copied from the template school, owned by the new school
    config = await ok(await api.get("/api/v1/configuration/student-management/"))
    classes = config["classes"]
    year = next(y for y in config["session_years"] if y["name"] == "2026-27")
    assert classes and year
    heads = {h["code"]: h["id"] for h in await ok(await api.get("/fee-heads"))}
    assert {"TUITION", "TRANSPORT"} <= set(heads)
    types = await ok(await transit.get("/transport-types"))
    assert {t["name"] for t in types} >= {"E-Rickshaw", "Van", "Bus"}

    # A fee structure for one class, published
    structure = await ok(await api.post("/fee-structures", json={
        "session_year_id": year["id"], "name": "Pinecrest 2026-27", "items": [
            {"fee_head_id": heads["TUITION"], "class_id": classes[0]["id"], "amount": "1200.00"}]}), 201)
    await ok(await api.post(f"/fee-structures/{structure['id']}/publish"))

    # The school's email domain for generated logins. Without BASE_DOMAIN (local, CI) the
    # default is "<code>.local", which email validation refuses, so onboarding sets it first.
    await ok(await api.put("/api/v1/school-settings/values/user.email_domain", json={"value": "pinecrest.in"}))

    # A student, admitted through the students API
    student = await ok(await api.post("/api/v1/students/", json={
        "admission_number": "PC-0001", "first_name": "Ivy", "last_name": "Pine", "date_of_birth": "2016-05-01",
        "gender_id": 2, "class_id": classes[0]["id"], "session_year_id": year["id"],
        "father_name": "Oak Pine", "mother_name": "Fern Pine", "father_phone": "9123400001",
        "admission_date": "2026-04-01"}))
    student_id = student["id"]

    # Plans and dues: tuition April to June 2026
    built = await ok(await api.post("/plans/build", json={"session_year_id": year["id"]}))
    assert built["students"] == 1
    await ok(await api.post("/dues/generate", json={"session_year_id": year["id"], "through_period": "2026-06-01"}))

    # Transport: own vehicle, route, flat rate, and a rider
    van = next(t for t in types if t["name"] == "Van")
    vehicle = await ok(await transit.post("/vehicles", json={
        "transport_type_id": van["id"], "registration_number": "PC 01 0001", "capacity": 10}), 201)
    route = await ok(await transit.post("/routes", json={
        "name": "Pinecrest Route", "vehicle_id": vehicle["id"],
        "stops": [{"name": "Pine Gate", "distance_km": "2.00"}]}), 201)
    await ok(await transit.post("/rates", json={
        "session_year_id": year["id"], "basis": "FLAT", "transport_type_id": van["id"],
        "monthly_amount": "400.00"}), 201)
    await ok(await transit.post("/assignments", json={
        "student_id": student_id, "session_year_id": year["id"], "route_stop_id": route["stops"][0]["id"],
        "start_date": "2026-04-01"}), 201)
    dues = await ok(await api.get(f"/students/{student_id}/dues"))
    assert {d["fee_head_id"] for d in dues} >= {heads["TUITION"], heads["TRANSPORT"]}

    # A payment, numbered in the new school's own receipt series
    payment = await ok(await api.post("/payments", json={
        "student_id": student_id, "amount": "1600.00", "payment_method_id": 1}), 201)
    assert payment["receipt_number"] == f"{default_receipt_prefix(CODE)}/2026-27/000001"

    # The student logs in on the school's subdomain and sees the same balance
    balance = await ok(await api.get(f"/students/{student_id}/balance"))
    student_headers = await _login(client_factory, CODE, student["email"], "Sunrise@001")
    statement = await ok(await Api(client_factory, CODE, student_headers).get("/my/statement"))
    assert statement["student_id"] == student_id and statement["admission_number"] == "PC-0001"
    assert statement["balance"]["balance"] == balance["balance"]
    assert [p["receipt_number"] for p in statement["payments"]] == [payment["receipt_number"]]

    # Settings: the shop is turned on for this school only
    await ok(await api.put("/api/v1/school-settings/values/module.shop.enabled", json={"value": "true"}))
    assert (await api.get("/api/v1/inventory/stock/levels/")).status_code == 200
    assert (await admin_api.get("/api/v1/inventory/stock/levels/")).status_code == 403

    # Neither school sees the other
    for path in (f"/students/{student_id}/dues", f"/payments/{payment['id']}"):
        assert (await admin_api.get(path)).status_code == 404, path
    assert (await admin_api.get(f"/api/v1/students/{student_id}")).status_code == 404
    sunrise_students = await ok(await admin_api.get("/api/v1/students/", params={"per_page": 100}))
    assert student_id not in {s["id"] for s in sunrise_students["students"]}
    pine_students = await ok(await api.get("/api/v1/students/"))
    assert [s["id"] for s in pine_students["students"]] == [student_id]
    assert (await api.get("/api/v1/transit/routes")).json()[0]["name"] == "Pinecrest Route"

    # Sunrise's token is refused on the new school's subdomain, and the other way round
    async with client_factory(CODE) as client:
        assert (await client.get("/api/v1/auth/me", headers=admin_api.headers)).status_code == 401
    async with client_factory(schools["sunrise_code"]) as client:
        assert (await client.get("/api/v1/auth/me", headers=api.headers)).status_code == 401
