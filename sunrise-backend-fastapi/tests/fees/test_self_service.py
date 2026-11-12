"""A student's own fee statement and receipt, and the public school branding route."""
from sqlalchemy import update

from app.core.security import get_password_hash
from app.models.student import Student
from app.models.user import User
from tests.tenant.conftest import TEST_PASSWORD

from .conftest import Api, login
from .test_ledger import _build, _generate, _pay, _student, priced  # noqa: F401  (fixture)


async def _student_api(client_factory, schools, sunrise_session, student_id, email):
    """Give the student a login and return an Api logged in as that student."""
    async with sunrise_session() as session:
        user = User(email=email, password=get_password_hash(TEST_PASSWORD), first_name="Stu", last_name="Dent",
                    user_type_id=3, is_active=True)
        session.add(user)
        await session.flush()
        await session.execute(update(Student).where(Student.id == student_id).values(user_id=user.id))
        await session.commit()
    code = schools["sunrise_code"]
    return Api(client_factory, code, await login(client_factory, code, email))


async def test_student_sees_only_their_own_statement(admin_api, priced, sunrise_session, client_factory, schools):  # noqa: F811
    mine = await _student(sunrise_session, priced)
    other = await _student(sunrise_session, priced)
    await _build(admin_api, priced)
    await _generate(admin_api, priced, "2026-05-01")
    my_payment = await _pay(admin_api, mine, "1500.00")
    other_payment = await _pay(admin_api, other, "1000.00")
    api = await _student_api(client_factory, schools, sunrise_session, mine, "stu-self@sunrise-test.in")

    r = await api.get("/my/statement", params={"session_year_id": priced["year_id"]})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["student_id"] == mine
    assert {d["student_id"] for d in body["dues"]} == {mine}
    assert all(d["fee_head_name"] for d in body["dues"])
    assert [p["id"] for p in body["payments"]] == [my_payment["id"]]
    assert body["balance"]["total_paid"] == "1500.00"

    # Own receipt works, another student's does not, and the staff routes stay closed
    assert (await api.get(f"/my/payments/{my_payment['id']}/receipt.pdf")).content[:4] == b"%PDF"
    assert (await api.get(f"/my/payments/{other_payment['id']}/receipt.pdf")).status_code == 404
    assert (await api.get(f"/students/{other}/dues")).status_code == 403


async def test_statement_is_for_students_only(admin_api):
    assert (await admin_api.get("/my/statement")).status_code == 403


async def test_public_school_branding(client_factory, schools):
    async with client_factory(schools["sunrise_code"]) as client:
        r = await client.get("/api/v1/public/school")
    assert r.status_code == 200, r.text
    assert r.json()["code"] == schools["sunrise_code"] and r.json()["name"]
    async with client_factory(schools["other_code"]) as client:
        assert (await client.get("/api/v1/public/school")).json()["code"] == schools["other_code"]
