"""
Raw SQL (text()) scoping, Phase 5.

The guard in app/core/tenant.py refuses raw SQL on a school session unless it
filters by :school_id (filled in from the session) or is built with global_sql().
The module tests below seed a second school (Oakridge) and check that every
raw-SQL read in leave, attendance, expenses, teachers, metadata and the
dashboard returns only the calling school's rows.
"""
from datetime import date

import pytest
import pytest_asyncio
from sqlalchemy import text

from app.core.tenant import TenantContextError, global_sql, tenant_bypass

from .conftest import TEST_PASSWORD

TODAY = date.today()


# ---------------------------------------------------------------------------
# The guard
# ---------------------------------------------------------------------------


async def test_raw_sql_without_school_filter_is_refused(make_session, schools):
    async with make_session(schools["sunrise_id"]) as session:
        with pytest.raises(TenantContextError, match=":school_id"):
            await session.execute(text("SELECT COUNT(*) FROM students"))


async def test_school_id_is_filled_in_from_the_session(make_session, schools):
    async with make_session(schools["other_id"]) as session:
        value = (await session.execute(text("SELECT CAST(:school_id AS INTEGER)"))).scalar_one()
        assert value == schools["other_id"]
        # Works alongside the caller's own parameters too
        value = (await session.execute(
            text("SELECT CAST(:school_id AS INTEGER) + CAST(:n AS INTEGER)"), {"n": 1})).scalar_one()
        assert value == schools["other_id"] + 1


async def test_passing_another_schools_id_is_refused(make_session, schools):
    async with make_session(schools["sunrise_id"]) as session:
        with pytest.raises(TenantContextError, match="school_id="):
            await session.execute(
                text("SELECT COUNT(*) FROM students WHERE school_id = :school_id"),
                {"school_id": schools["other_id"]},
            )


async def test_global_sql_runs_without_a_school_filter(make_session, schools):
    async with make_session(schools["sunrise_id"]) as session:
        count = (await session.execute(global_sql("SELECT COUNT(*) FROM genders"))).scalar_one()
        assert count > 0


async def test_global_sql_cannot_filter_by_school(make_session, schools):
    async with make_session(schools["sunrise_id"]) as session:
        with pytest.raises(TenantContextError, match="global_sql"):
            await session.execute(global_sql("SELECT 1 WHERE CAST(:school_id AS INTEGER) > 0"))


async def test_raw_sql_without_a_school_is_refused(make_session, schools):
    async with make_session() as session:
        with pytest.raises(TenantContextError, match="without a school"):
            await session.execute(text("SELECT COUNT(*) FROM students WHERE school_id = :school_id"))
        # System lists stay readable before login
        assert (await session.execute(global_sql("SELECT 1"))).scalar_one() == 1


async def test_tenant_bypass_allows_cross_school_raw_sql(make_session, schools):
    async with make_session() as session:
        with tenant_bypass(session):
            count = (await session.execute(text("SELECT COUNT(DISTINCT school_id) FROM users"))).scalar_one()
        assert count >= 2


# ---------------------------------------------------------------------------
# Module queries: Oakridge rows never show up in Sunrise, and the reverse
# ---------------------------------------------------------------------------


async def _insert(session, sql, **params):
    return (await session.execute(text(sql + " RETURNING id"), params)).scalar_one()


@pytest_asyncio.fixture
async def oak(make_session, schools):
    """A small but complete Oakridge: lists, a student, a teacher, leave, attendance, an expense."""
    sid = schools["other_id"]
    async with make_session() as session:
        with tenant_bypass(session):
            ids = {"school_id": sid, "admin_id": schools["other_admin_id"]}
            ids["year_id"] = await _insert(
                session,
                "INSERT INTO session_years (school_id, name, description, start_date, end_date, is_current, is_active) "
                "VALUES (:s, 'OAK-YR', 'Oak year', :start, :end, TRUE, TRUE)",
                s=sid, start=date(TODAY.year - 1, 1, 1), end=date(TODAY.year + 1, 12, 31))
            ids["class_id"] = await _insert(
                session, "INSERT INTO classes (school_id, name, description) VALUES (:s, 'OAK-C1', 'Oak Class One')", s=sid)
            ids["department_id"] = await _insert(
                session, "INSERT INTO departments (school_id, name, description) VALUES (:s, 'OAK-D', 'Oak Department')", s=sid)
            ids["position_id"] = await _insert(
                session, "INSERT INTO positions (school_id, name, description) VALUES (:s, 'OAK-P', 'Oak Position')", s=sid)
            ids["leave_type_id"] = await _insert(
                session, "INSERT INTO leave_types (school_id, name, description) VALUES (:s, 'OAK-LT', 'Oak Leave')", s=sid)
            ids["expense_category_id"] = await _insert(
                session, "INSERT INTO expense_categories (school_id, name, description) VALUES (:s, 'OAK-EC', 'Oak Expense')", s=sid)
            ids["student_id"] = await _insert(
                session,
                "INSERT INTO students (school_id, admission_number, first_name, last_name, admission_date, "
                "class_id, session_year_id, gender_id, is_active) "
                "VALUES (:s, 'OAK-001', 'Oakie', 'Student', :d, :c, :y, 1, TRUE)",
                s=sid, d=TODAY, c=ids["class_id"], y=ids["year_id"])
            ids["teacher_id"] = await _insert(
                session,
                "INSERT INTO teachers (school_id, employee_id, first_name, last_name, phone, email, position_id, "
                "department_id, joining_date, class_teacher_of_id, is_active) "
                "VALUES (:s, 'OAK-T1', 'Oakie', 'Teacher', '9000000000', 'teacher@oakridgeschool.in', :p, :dep, :d, :c, TRUE)",
                s=sid, p=ids["position_id"], dep=ids["department_id"], d=TODAY, c=ids["class_id"])
            for applicant_type, applicant_id in (("student", ids["student_id"]), ("teacher", ids["teacher_id"])):
                ids[f"{applicant_type}_leave_id"] = await _insert(
                    session,
                    "INSERT INTO leave_requests (school_id, user_id, leave_type_id, start_date, end_date, total_days, "
                    "reason, applicant_type, applicant_id, session_year_id, leave_status_id, applied_by) "
                    "VALUES (:s, :u, :lt, :d, :d, 1, 'Oak reason', :at, :aid, :y, 1, :u)",
                    s=sid, u=ids["admin_id"], lt=ids["leave_type_id"], d=TODAY, at=applicant_type,
                    aid=applicant_id, y=ids["year_id"])
            absent = (await session.execute(text("SELECT id FROM attendance_statuses WHERE name = 'ABSENT'"))).scalar_one()
            for days_ago in range(3):
                await _insert(
                    session,
                    "INSERT INTO attendance_records (school_id, student_id, class_id, session_year_id, attendance_date, "
                    "attendance_status_id, marked_by) VALUES (:s, :st, :c, :y, :d, :a, :u)",
                    s=sid, st=ids["student_id"], c=ids["class_id"], y=ids["year_id"],
                    d=date.fromordinal(TODAY.toordinal() - days_ago), a=absent, u=ids["admin_id"])
            ids["expense_id"] = await _insert(
                session,
                "INSERT INTO expenses (school_id, expense_date, expense_category_id, description, amount, total_amount, "
                "payment_method_id, requested_by, session_year_id, expense_status_id, is_deleted) "
                "VALUES (:s, :d, :ec, 'Oak chalk', 100, 100, 1, :u, :y, 1, FALSE)",
                s=sid, d=TODAY, ec=ids["expense_category_id"], u=ids["admin_id"], y=ids["year_id"])
            await session.commit()
    return ids


async def test_leave_queries_are_scoped(make_session, schools, oak):
    from app.crud.crud_leave import leave_request_crud
    from app.schemas.leave import ApplicantTypeEnum, LeaveFilters

    oak_leaves = {oak["student_leave_id"], oak["teacher_leave_id"]}
    async with make_session(schools["sunrise_id"]) as session:
        assert await leave_request_crud.get_with_details(session, oak["student_leave_id"]) is None
        rows, _ = await leave_request_crud.get_multi_with_filters(session, filters=LeaveFilters(), limit=10000)
        assert not {r.id for r in rows} & oak_leaves
        assert not {r.id for r in await leave_request_crud.get_pending_requests(session)} & oak_leaves
        assert await leave_request_crud.get_by_applicant(
            session, applicant_id=oak["student_id"], applicant_type=ApplicantTypeEnum.STUDENT) == []
        rows, total = await leave_request_crud.get_student_leaves_by_class_teacher(session, teacher_id=oak["teacher_id"])
        assert rows == [] and total == 0

    async with make_session(schools["other_id"]) as session:
        detail = await leave_request_crud.get_with_details(session, oak["student_leave_id"])
        assert detail is not None and detail.applicant_name.startswith("Oakie Student")
        rows, total = await leave_request_crud.get_multi_with_filters(session, filters=LeaveFilters())
        assert {r.id for r in rows} == oak_leaves and total == 2
        assert {r.id for r in await leave_request_crud.get_pending_requests(session)} == oak_leaves
        rows, total = await leave_request_crud.get_student_leaves_by_class_teacher(session, teacher_id=oak["teacher_id"])
        assert [r.id for r in rows] == [oak["student_leave_id"]] and total == 1
        stats = await leave_request_crud.get_leave_statistics(session, year=TODAY.year)
        assert stats["total_requests"] == 2 and stats["pending_requests"] == 2
        trend = await leave_request_crud.get_monthly_leave_trend(session, year=TODAY.year)
        assert sum(m["count"] for m in trend) == 2
        by_class = await leave_request_crud.get_class_wise_leave_stats(session)
        assert by_class == [{"class_name": "OAK-C1", "total_requests": 1, "approved_requests": 0,
                             "rejected_requests": 0, "pending_requests": 1, "total_days": 1}]


async def test_leave_applicant_from_another_school_is_not_joined(make_session, schools, oak):
    """applicant_id has no foreign key: a leave pointing at a Sunrise student must not show its name."""
    from app.crud.crud_leave import leave_request_crud

    async with make_session() as session:
        with tenant_bypass(session):
            sunrise_student = (await session.execute(
                text("SELECT id FROM students WHERE school_id = :s LIMIT 1"), {"s": schools["sunrise_id"]})).scalar()
            if sunrise_student is None:
                pytest.skip("Sunrise has no students in this database")
            await session.execute(
                text("UPDATE leave_requests SET applicant_id = :a WHERE id = :id"),
                {"a": sunrise_student, "id": oak["student_leave_id"]})
            await session.commit()
    async with make_session(schools["other_id"]) as session:
        detail = await leave_request_crud.get_with_details(session, oak["student_leave_id"])
        assert detail.applicant_name.startswith("Unknown Applicant")


async def test_attendance_queries_are_scoped(make_session, schools, oak):
    from app.crud.crud_attendance import attendance_record_crud
    from app.schemas.attendance import AttendanceFilters

    async with make_session(schools["sunrise_id"]) as session:
        rows, total = await attendance_record_crud.get_multi_with_filters(
            session, filters=AttendanceFilters(student_id=oak["student_id"]))
        assert rows == [] and total == 0
        assert await attendance_record_crud.get_student_summary(
            session, student_id=oak["student_id"], session_year_id=oak["year_id"]) is None
        assert await attendance_record_crud.get_class_attendance_by_date(
            session, class_id=oak["class_id"], attendance_date=TODAY, session_year_id=oak["year_id"]) == []
        stats = await attendance_record_crud.get_attendance_statistics(
            session, filters=AttendanceFilters(session_year_id=oak["year_id"]))
        assert stats["total_records"] == 0
        assert await attendance_record_crud.get_consecutive_absences(session, session_year_id=oak["year_id"]) == []

    async with make_session(schools["other_id"]) as session:
        rows, total = await attendance_record_crud.get_multi_with_filters(
            session, filters=AttendanceFilters(session_year_id=oak["year_id"]))
        assert total == 3
        summary = await attendance_record_crud.get_student_summary(
            session, student_id=oak["student_id"], session_year_id=oak["year_id"])
        assert summary["days_absent"] == 3
        roster = await attendance_record_crud.get_class_attendance_by_date(
            session, class_id=oak["class_id"], attendance_date=TODAY, session_year_id=oak["year_id"])
        assert [r["student_id"] for r in roster] == [oak["student_id"]]
        absences = await attendance_record_crud.get_consecutive_absences(session, session_year_id=oak["year_id"])
        assert [(a["student_id"], a["consecutive_absent_days"]) for a in absences] == [(oak["student_id"], 3)]


async def test_expense_queries_are_scoped(make_session, schools, oak):
    from app.crud.crud_expense import expense_crud
    from app.schemas.expense import ExpenseFilters

    async with make_session(schools["sunrise_id"]) as session:
        assert await expense_crud.get_with_details(session, oak["expense_id"]) is None
        rows, _ = await expense_crud.get_multi_with_filters(session, filters=ExpenseFilters(), limit=10000)
        assert oak["expense_id"] not in {r.id for r in rows}
        assert oak["expense_id"] not in {r.id for r in await expense_crud.get_pending_expenses(session)}
        assert await expense_crud.get_by_requester(session, requester_id=oak["admin_id"]) == []

    async with make_session(schools["other_id"]) as session:
        assert (await expense_crud.get_with_details(session, oak["expense_id"])).id == oak["expense_id"]
        rows, total = await expense_crud.get_multi_with_filters(session, filters=ExpenseFilters())
        assert [r.id for r in rows] == [oak["expense_id"]] and total == 1
        stats = await expense_crud.get_expense_statistics(session, year=TODAY.year)
        assert stats["total_expenses"] == 1


async def test_teacher_queries_are_scoped(make_session, schools, oak):
    from app.crud.crud_teacher import teacher_crud

    async with make_session(schools["sunrise_id"]) as session:
        assert await teacher_crud.get_with_metadata(session, id=oak["teacher_id"]) is None
        rows, _ = await teacher_crud.get_multi_with_filters(session, limit=10000)
        assert oak["teacher_id"] not in {r["id"] for r in rows}

    async with make_session(schools["other_id"]) as session:
        assert (await teacher_crud.get_with_metadata(session, id=oak["teacher_id"]))["id"] == oak["teacher_id"]
        rows, total = await teacher_crud.get_multi_with_filters(session)
        assert [r["id"] for r in rows] == [oak["teacher_id"]] and total == 1
        stats = await teacher_crud.get_dashboard_stats(session)
        assert stats["total_teachers"] == 1


async def test_configuration_lists_are_per_school(make_session, schools, oak):
    from app.crud.metadata import get_all_metadata_async

    async with make_session(schools["other_id"]) as session:
        metadata = await get_all_metadata_async(session)
    assert [c.name for c in metadata["classes"]] == ["OAK-C1"]
    assert [y.name for y in metadata["session_years"]] == ["OAK-YR"]
    assert [d.name for d in metadata["departments"]] == ["OAK-D"]
    assert metadata["genders"], "global lists are still returned"

    async with make_session(schools["sunrise_id"]) as session:
        metadata = await get_all_metadata_async(session)
    assert "OAK-C1" not in {c.name for c in metadata["classes"]}
    assert "OAK-YR" not in {y.name for y in metadata["session_years"]}


async def _login_oak_admin(client, schools):
    response = await client.post(
        "/api/v1/auth/login-json", json={"email": schools["other_admin_email"], "password": TEST_PASSWORD})
    assert response.status_code == 200, response.text
    client.headers["Authorization"] = f"Bearer {response.json()['access_token']}"


async def test_dashboard_counts_only_the_callers_school(client_factory, make_session, schools, oak):
    async with make_session() as session:
        with tenant_bypass(session):
            sunrise_year = (await session.execute(text(
                "SELECT id FROM session_years WHERE school_id = :s ORDER BY is_current DESC, id DESC LIMIT 1"),
                {"s": schools["sunrise_id"]})).scalar_one()

    async with client_factory(schools["other_code"]) as client:
        await _login_oak_admin(client, schools)
        for path in ("admin-dashboard-stats", "admin-dashboard-enhanced-stats"):
            # Another school's session year is not found, so none of its numbers leak
            foreign = await client.get(f"/api/v1/dashboard/{path}", params={"session_year_id": sunrise_year})
            assert foreign.status_code == 404, foreign.text
        response = await client.get("/api/v1/dashboard/admin-dashboard-enhanced-stats")  # current session
        assert response.status_code == 200, response.text
        own = response.json()

    assert own["session_info"]["id"] == oak["year_id"]
    for section in ("student_management", "leave_management", "expense_management"):
        assert "error" not in own[section], (section, own[section])
    assert own["student_management"]["total_students"] == 1
    assert own["leave_management"]["total_requests"] == 2
    assert own["expense_management"]["total_expenses"] == 100.0


async def test_attendance_defaults_to_the_schools_current_session(client_factory, schools, oak):
    """The old default was Sunrise's session year id 4; now it is the caller's current session."""
    async with client_factory(schools["other_code"]) as client:
        await _login_oak_admin(client, schools)
        response = await client.get("/api/v1/attendance")
    assert response.status_code == 200, response.text
    assert response.json()["total"] == 3


async def test_student_and_teacher_dashboards_are_scoped(client_factory, make_session, schools, oak):
    from app.core.security import get_password_hash

    users = {}
    async with make_session() as session:
        with tenant_bypass(session):
            for kind, type_id, table, row_id in (("student", 3, "students", oak["student_id"]),
                                                 ("teacher", 2, "teachers", oak["teacher_id"])):
                users[kind] = f"{kind}.login@oakridgeschool.in"
                user_id = await _insert(
                    session,
                    "INSERT INTO users (school_id, email, password, first_name, last_name, user_type_id, is_active) "
                    "VALUES (:s, :e, :p, 'Oakie', :k, :t, TRUE)",
                    s=oak["school_id"], e=users[kind], p=get_password_hash(TEST_PASSWORD), k=kind, t=type_id)
                await session.execute(text(f"UPDATE {table} SET user_id = :u WHERE id = :id"), {"u": user_id, "id": row_id})
            # An approved teacher leave shows under upcoming leaves
            await session.execute(text("UPDATE leave_requests SET leave_status_id = 2 WHERE id = :id"),
                                  {"id": oak["teacher_leave_id"]})
            await session.commit()

    for kind in ("student", "teacher"):
        async with client_factory(schools["other_code"]) as client:
            login = await client.post("/api/v1/auth/login-json", json={"email": users[kind], "password": TEST_PASSWORD})
            assert login.status_code == 200, login.text
            response = await client.get(f"/api/v1/{kind}s/my-dashboard-stats",
                                        headers={"Authorization": f"Bearer {login.json()['access_token']}"})
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["leave_stats"]["total"] == 1, (kind, body["leave_stats"])
        if kind == "student":
            assert body["academic_info"]["class_name"] == "Oak Class One"
        else:
            assert [leave["id"] for leave in body["upcoming_leaves"]] == [oak["teacher_leave_id"]]
