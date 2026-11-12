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


async def test_public_admissions(admin_api, priced, sunrise_session, client_factory, schools, monkeypatch):  # noqa: F811
    from datetime import date

    from app.models.metadata import SessionYear
    from app.services import admissions

    async with sunrise_session() as session:
        year = await session.get(SessionYear, priced["year_id"])
        assert year.start_date == date(2026, 4, 1)
        # Only sessions up to 2026-27 exist, so 2027-28 is worked out from it
        await session.execute(update(SessionYear).where(SessionYear.start_date > date(2026, 4, 1)).values(is_active=False))
        await session.commit()

        info = await admissions.admissions_info(session, today=date(2026, 11, 12))
        assert info["session"] == {"name": "2027-28", "start_date": date(2027, 4, 1)}
        dates = {d["key"]: (d["date"], d["end_date"]) for d in info["dates"]}
        assert dates["forms"] == (date(2026, 11, 15), None)
        assert dates["last_date"] == (date(2027, 1, 31), None)
        assert dates["test"] == (date(2027, 2, 15), date(2027, 2, 20))
        assert dates["confirmation"] == (date(2027, 3, 1), date(2027, 3, 15))
        assert dates["begins"] == (date(2027, 4, 1), None)
        # 2027-28 has no prices yet: the latest published ones (2026-27) are shown and named
        assert info["fees"]["session_year"] == "2026-27"
        first = next(c for c in info["fees"]["classes"] if c["class_id"] == priced["class_ids"][0])
        # Tuition 1000 a month, exam 600 twice a year, admission 5000 once (new students)
        assert (first["monthly"], first["one_time"], first["first_year_total"]) == (1000, 5000, 18200)

        # Before the session starts, it is the one families apply for
        info = await admissions.admissions_info(session, today=date(2026, 1, 10))
        assert info["session"]["name"] == "2026-27" and info["fees"]["session_year"] == "2026-27"

    async with client_factory(schools["sunrise_code"]) as client:
        r = await client.get("/api/v1/public/admissions")
    assert r.status_code == 200, r.text
    assert set(r.json()) == {"session", "dates", "fees"} and len(r.json()["dates"]) == 6
    # A school with nothing published shows no prices, never another school's
    async with client_factory(schools["other_code"]) as client:
        assert (await client.get("/api/v1/public/admissions")).json()["fees"]["classes"] == []
