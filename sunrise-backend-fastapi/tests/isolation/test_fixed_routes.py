"""
Routes the isolation sweep found broken for every school (Phase 7). Each now
answers for the school's own data.
"""
from .conftest import MARK, ok


async def test_routes_fixed_by_the_sweep_answer_for_own_data(sunrise_world, admin_api):
    student_id = sunrise_world["student_id"]

    detail = await ok(await admin_api.get(f"/api/v1/students/{student_id}"))  # imported a missing module
    assert detail["first_name"] == f"{MARK}Kid"

    by_class = await ok(await admin_api.get("/api/v1/students/class/Class 1"))  # used Student.current_class
    assert by_class["total_students"] == len(by_class["students"])

    history = await ok(await admin_api.get(f"/api/v1/session-progression/history/{student_id}"))
    assert (history["student_id"], history["student_name"]) == (student_id, f"{MARK}Kid Student")
    assert (await admin_api.get("/api/v1/session-progression/history/999999999")).status_code == 404

    by_department = await ok(await admin_api.get("/api/v1/teachers/department/Mathematics"))  # wrong CRUD argument
    assert "teachers" in by_department

    for report in ("/api/v1/expenses/reports/yearly", "/api/v1/expenses/reports/monthly?year=2026"):
        summary = (await ok(await admin_api.get(report)))["summary"]  # read a missing statistics key
        assert summary["pending_count"] >= 1  # the fixture's expense is pending

    deleted = await ok(await admin_api.delete(f"/api/v1/expenses/{sunrise_world['expense_id']}"))  # queried a schema
    assert deleted["expense_id"] == sunrise_world["expense_id"]
