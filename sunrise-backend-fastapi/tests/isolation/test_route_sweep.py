"""
Every route, called by the second school's admin, against Sunrise's data.

* Every GET route without path parameters answers with none of Sunrise's marker texts.
* Every GET route with an id in its path, given a Sunrise id, does not answer 200.
* Every write route (POST, PUT, PATCH, DELETE) with an id in its path, given a
  Sunrise id, changes nothing of Sunrise's.

The routes come from the app itself, so a new route is swept automatically. A
new path parameter name must be added to `path_values` below, or the sweep fails.
"""
import re

import pytest
from fastapi.routing import APIRoute
from sqlalchemy import text

from app.services.cloudinary_receipt_service import CloudinaryReceiptService
from app.services.whatsapp_service import WhatsAppService

# Only a platform admin token is accepted here; school tokens are checked separately
PLATFORM_PREFIXES = ("/api/v1/platform", "/api/v1/database")

# Parameters that are not ids: a value the route can take for any school
NAME_PARAMS = {
    "kind": "classes",
    "class_name": "Class 1",
    "department": "Mathematics",
    "subject": "Mathematics",
    "applicant_type": "teacher",
    "attendance_date": "2026-07-01",
    "key": "fee.late_fee.enabled",
}

# A route listed here is allowed to answer 200 to a Sunrise id, because it does
# not look the id up as a record. The reason is part of the test.
ANSWERS_200_ON_PURPOSE = {
    # Lists the second school's own leave requests for that applicant id: none
    ("GET", "/api/v1/leaves/applicant/{applicant_type}/{applicant_id}"),
    # Summary of the second school's attendance rows for that student id: all zero
    ("GET", "/api/v1/attendance/student/{student_id}/summary"),
    # The second school's attendance for that class id and date: none
    ("GET", "/api/v1/attendance/class/{class_id}/date/{attendance_date}"),
}

_PARAM = re.compile(r"{(\w+)(?::\w+)?}")


@pytest.fixture(autouse=True)
def no_external_calls(monkeypatch):
    """A leak must show up as a failed assertion, not as a real upload or message."""
    def refuse(*args, **kwargs):
        raise AssertionError("A route called Cloudinary or WhatsApp during the isolation sweep")

    monkeypatch.setattr(CloudinaryReceiptService, "__init__", refuse)
    monkeypatch.setattr(WhatsAppService, "__init__", refuse)


def _api_routes(methods: set):
    from main import app

    for route in app.routes:
        if not isinstance(route, APIRoute) or not route.path.startswith("/api/v1/"):
            continue
        if route.path.startswith(PLATFORM_PREFIXES):
            continue
        for method in sorted(route.methods & methods):
            yield method, route.path


def path_values(world: dict) -> dict:
    ids = {
        "user_id": world["user_id"],
        "applicant_id": world["user_id"],
        "teacher_id": world["teacher_id"],
        "student_id": world["student_id"],
        "leave_id": world["leave_id"],
        "expense_id": world["expense_id"],
        "structure_id": world["structure_id"],
        "payment_id": world["payment_id"],
        "purchase_id": world["purchase_id"],
        "route_id": world["route_id"],
        "assignment_id": world["assignment_id"],
        "vehicle_id": world["vehicle_id"],
        "image_id": world["image_id"],
        "alert_id": world["alert_id"],
        "class_id": world["class_id"],
        "row_id": world["class_id"],  # /school-settings/lists/classes/{row_id}
        "id": world["attendance_id"],  # /attendance/{id}
    }
    for name in ("concession_id", "due_id", "head_id", "item_type_id", "line_id", "pause_id", "pricing_id",
                 "procurement_id", "rate_id", "rule_id", "sibling_id", "stock_id", "stop_id", "type_id"):
        ids[name] = world[name]
    return {**ids, **NAME_PARAMS}


def _has_id_param(path: str) -> bool:
    return any(p not in NAME_PARAMS for p in _PARAM.findall(path))


def _fill(path: str, values: dict) -> str:
    missing = [p for p in _PARAM.findall(path) if p not in values]
    assert not missing, (
        f"{path}: no Sunrise value for path parameter(s) {missing}. "
        "Add them to path_values() in tests/isolation/test_route_sweep.py.")
    return _PARAM.sub(lambda m: str(values[m.group(1)]), path)


async def _request(api, method: str, url: str, problems: list, label: str):
    """The response, or None after noting the exception the route raised."""
    try:
        if method == "GET":
            return await api.get(url)
        return await api.call(method, url, json={})
    except Exception as error:  # the test client re-raises a route's unhandled exception
        problems.append(f"{label} raised {type(error).__name__}: {error}")
        return None


def _leaks(body: str, fingerprints: list) -> list:
    return [f for f in fingerprints if f.lower() in body.lower()]


async def test_list_routes_show_nothing_of_another_school(sunrise_world, other_with_shop):
    problems, swept = [], 0
    for method, path in _api_routes({"GET"}):
        if _PARAM.search(path):
            continue
        r = await _request(other_with_shop, "GET", path, problems, f"GET {path}")
        swept += 1
        if r is None:
            continue
        leaked = _leaks(r.text, sunrise_world["fingerprints"])
        if leaked:
            problems.append(f"GET {path} -> {r.status_code} shows Sunrise data {leaked}")
        elif r.status_code >= 500:
            problems.append(f"GET {path} -> {r.status_code}")
    assert swept > 80
    assert problems == [], "\n".join(problems)


async def test_detail_routes_refuse_another_schools_ids(sunrise_world, other_with_shop):
    values = path_values(sunrise_world)
    problems, swept = [], 0
    for method, path in _api_routes({"GET"}):
        if not _PARAM.search(path):
            continue
        r = await _request(other_with_shop, "GET", _fill(path, values), problems, f"GET {path}")
        swept += 1
        if r is None:
            continue
        leaked = _leaks(r.text, sunrise_world["fingerprints"])
        if leaked:
            problems.append(f"GET {path} -> {r.status_code} shows Sunrise data {leaked}")
        elif (r.status_code == 200 and _has_id_param(path)
              and (method, path) not in ANSWERS_200_ON_PURPOSE):
            problems.append(f"GET {path} -> 200 for a Sunrise id (expected 403 or 404)")
        elif r.status_code >= 500:
            problems.append(f"GET {path} -> {r.status_code}")
    assert swept > 30
    assert problems == [], "\n".join(problems)


async def _sunrise_snapshot(make_session, schools, world) -> dict:
    """Everything a write route could change about Sunrise's rows."""
    queries = {
        "student": ("SELECT first_name, class_id, is_active, is_deleted FROM students "
                    "WHERE id = :id AND school_id = :school_id", world["student_id"]),
        "teacher": ("SELECT first_name, is_active, is_deleted FROM teachers "
                    "WHERE id = :id AND school_id = :school_id", world["teacher_id"]),
        "user": ("SELECT email, is_active, password FROM users WHERE id = :id AND school_id = :school_id",
                 world["user_id"]),
        "payment": ("SELECT amount, kind, receipt_url FROM payments WHERE id = :id AND school_id = :school_id",
                    world["payment_id"]),
        "reversals": ("SELECT COUNT(*) FROM payments WHERE reverses_payment_id = :id AND school_id = :school_id",
                      world["payment_id"]),
        "allocations": ("SELECT COUNT(*), SUM(amount) FROM payment_allocations "
                        "WHERE payment_id = :id AND school_id = :school_id", world["payment_id"]),
        "structure": ("SELECT name, status FROM fee_structures WHERE id = :id AND school_id = :school_id",
                      world["structure_id"]),
        "assignment": ("SELECT end_date, monthly_amount FROM student_transport_assignments "
                       "WHERE id = :id AND school_id = :school_id", world["assignment_id"]),
        "route": ("SELECT name, is_active FROM routes WHERE id = :id AND school_id = :school_id", world["route_id"]),
        "vehicle": ("SELECT registration_number, is_active FROM vehicles WHERE id = :id AND school_id = :school_id",
                    world["vehicle_id"]),
        "leave": ("SELECT leave_status_id, reason FROM leave_requests WHERE id = :id AND school_id = :school_id",
                  world["leave_id"]),
        "expense": ("SELECT expense_status_id, description, is_deleted FROM expenses "
                    "WHERE id = :id AND school_id = :school_id", world["expense_id"]),
        "attendance": ("SELECT attendance_status_id FROM attendance_records WHERE id = :id AND school_id = :school_id",
                       world["attendance_id"]),
        "alert": ("SELECT alert_status_id, title FROM alerts WHERE id = :id AND school_id = :school_id",
                  world["alert_id"]),
        "image": ("SELECT title, is_active FROM gallery_images WHERE id = :id AND school_id = :school_id",
                  world["image_id"]),
        "purchase": ("SELECT total_amount FROM inventory_purchases WHERE id = :id AND school_id = :school_id",
                     world["purchase_id"]),
        "dues": ("SELECT COUNT(*), SUM(net_amount), SUM(paid_amount) FROM student_dues "
                 "WHERE student_id = :id AND school_id = :school_id", world["student_id"]),
        "siblings": ("SELECT COUNT(*) FROM student_siblings WHERE (student_id = :id OR sibling_student_id = :id) "
                     "AND school_id = :school_id", world["student_id"]),
    }
    snapshot = {}
    async with make_session(schools["sunrise_id"]) as session:
        for name, (sql, row_id) in queries.items():
            snapshot[name] = [tuple(r) for r in (await session.execute(text(sql), {"id": row_id})).all()]
    return snapshot


async def test_write_routes_cannot_change_another_schools_rows(sunrise_world, other_with_shop, make_session, schools):
    values = path_values(sunrise_world)
    before = await _sunrise_snapshot(make_session, schools, sunrise_world)
    assert all(before.values()), before  # every Sunrise row exists

    problems, swept = [], 0
    for method, path in _api_routes({"POST", "PUT", "PATCH", "DELETE"}):
        if not _PARAM.search(path):
            continue
        r = await _request(other_with_shop, method, _fill(path, values), problems, f"{method} {path}")
        swept += 1
        if r is None:
            continue
        if r.status_code < 300 and _has_id_param(path):
            problems.append(f"{method} {path} -> {r.status_code} for a Sunrise id")
        elif r.status_code >= 500:
            problems.append(f"{method} {path} -> {r.status_code}")
    assert swept > 30
    assert problems == [], "\n".join(problems)
    assert await _sunrise_snapshot(make_session, schools, sunrise_world) == before


async def test_school_admin_token_is_refused_on_platform_routes(sunrise_world, other_with_shop):
    from main import app

    platform = [(m, r.path) for r in app.routes if isinstance(r, APIRoute) and r.path.startswith(PLATFORM_PREFIXES)
                and r.path != "/api/v1/platform/auth/login" for m in r.methods if m != "HEAD"]
    assert platform
    for method, path in platform:
        r = await other_with_shop.call(method, _PARAM.sub("1", path), json={})
        assert r.status_code in (401, 403), f"{method} {path} -> {r.status_code}"
