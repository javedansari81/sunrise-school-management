"""
Fixtures for the cross-school isolation suite (Phase 7).

Reuses the tenant, fee and transport fixtures: one rolled-back transaction per
test, Sunrise (school 1) plus a second school "oakridge". `sunrise_world` fills
Sunrise with one row of every kind a route can show (student, teacher, payment,
transport assignment, leave, expense, attendance, alert, gallery image, shop
purchase), each carrying a marker text that must never reach the other school.

Run from sunrise-backend-fastapi/:
    PYTHONIOENCODING=utf-8 python -m pytest tests/isolation -o addopts="" --asyncio-mode=auto
"""
from datetime import date

import pytest
from sqlalchemy import text

from tests.transport.conftest import (  # noqa: F401  (fixtures)
    Api, TransitApi, add_student, admin_api, billing_api, client_factory, connection, fleet, frozen_today,
    login, make_session, ok, other_api, refs, schools, staff_api, sunrise_session, sunrise_users, transit,
)

MARK = "Quillfeather"  # in every Sunrise marker text; never used by the second school


async def _one(session, sql: str, **params) -> int:
    return (await session.execute(text(sql), params)).scalar_one()


@pytest.fixture
async def sunrise_world(admin_api, transit, fleet, refs, sunrise_session, sunrise_users, schools):
    """One Sunrise row of every kind, with the ids and the texts the second school must never see."""
    year = refs["year_id"]
    heads = refs["heads"]
    structure = await ok(await admin_api.post("/fee-structures", json={
        "session_year_id": year, "name": f"{MARK} fees", "items": [
            {"fee_head_id": heads["TUITION"], "class_id": fleet["class_ids"][0], "amount": "1000.00"}]}), 201)
    await ok(await admin_api.post(f"/fee-structures/{structure['id']}/publish"))

    async with sunrise_session() as session:
        student = await add_student(session, class_id=fleet["class_ids"][0], session_year_id=year,
                                    first_name=f"{MARK}Kid")
        await session.commit()
        student_id, admission_number = student.id, student.admission_number

    await ok(await admin_api.post("/plans/build", json={"session_year_id": year}))
    await ok(await admin_api.post("/dues/generate", json={"session_year_id": year, "through_period": "2026-06-01"}))
    payment = await ok(await admin_api.post("/payments", json={
        "student_id": student_id, "amount": "1500.00", "payment_method_id": 1}), 201)
    assignment = await ok(await transit.post("/assignments", json={
        "student_id": student_id, "session_year_id": year, "route_stop_id": fleet["stops"]["Stop A"],
        "start_date": "2026-04-01"}), 201)
    assignment_id = assignment["assignment"]["id"]
    paused = await ok(await transit.post(f"/assignments/{assignment_id}/pauses", json={
        "from_period": "2027-01-01", "to_period": "2027-01-31", "reason": f"{MARK} away"}), 201)
    concession = await ok(await admin_api.post(f"/students/{student_id}/concessions", json={
        "session_year_id": year, "concession_type": "SCHOLARSHIP", "value_type": "PERCENT", "value": "10",
        "fee_head_ids": [heads["TUITION"]], "reason": f"{MARK} scholarship"}), 201)
    async with sunrise_session() as session:
        sibling = await add_student(session, class_id=fleet["class_ids"][0], session_year_id=year,
                                    first_name=f"{MARK}Sibling")
        await session.commit()
        sibling_id = sibling.id

    admin_id = sunrise_users["admin_id"]
    async with sunrise_session() as session:
        sid = {"school_id": schools["sunrise_id"]}
        position = await _one(session, "SELECT MIN(id) FROM positions WHERE school_id = :school_id")
        leave_type = await _one(session, "SELECT MIN(id) FROM leave_types WHERE school_id = :school_id")
        category = await _one(session, "SELECT MIN(id) FROM expense_categories WHERE school_id = :school_id")
        gallery_category = await _one(session, "SELECT MIN(id) FROM gallery_categories WHERE school_id = :school_id")
        ids = {
            "due_id": await _one(session, "SELECT MIN(id) FROM student_dues WHERE school_id = :school_id "
                                          "AND student_id = :student_id", student_id=student_id),
            "line_id": await _one(session, "SELECT MIN(id) FROM student_fee_plans WHERE school_id = :school_id "
                                           "AND student_id = :student_id", student_id=student_id),
            "rule_id": await _one(session, "SELECT MIN(id) FROM concession_rules WHERE school_id = :school_id"),
            "item_type_id": await _one(session, "SELECT MIN(id) FROM inventory_item_types WHERE school_id = :school_id"),
            "stock_id": await _one(session, "SELECT MIN(id) FROM inventory_stock WHERE school_id = :school_id"),
            "pricing_id": await _one(session, """
                INSERT INTO inventory_pricing (school_id, inventory_item_type_id, session_year_id, unit_price,
                                               effective_from)
                VALUES (:school_id, (SELECT MIN(id) FROM inventory_item_types WHERE school_id = :school_id),
                        :year, 10, '2026-04-01') RETURNING id""", year=year),
            "procurement_id": await _one(session, """
                INSERT INTO inventory_stock_procurements (school_id, procurement_date, total_amount, payment_method_id)
                VALUES (:school_id, '2026-07-01', 10, 1) RETURNING id"""),
            "teacher_id": await _one(session, f"""
                INSERT INTO teachers (school_id, employee_id, first_name, last_name, phone, email, position_id,
                                      joining_date, is_active)
                VALUES (:school_id, '{MARK}-EMP-1', '{MARK}Teacher', 'Sunrise', '9000000001',
                        '{MARK.lower()}.teacher@sunrise-test.in', :position, '2024-04-01', TRUE) RETURNING id""",
                position=position, **sid),
            "leave_id": await _one(session, f"""
                INSERT INTO leave_requests (school_id, user_id, leave_type_id, start_date, end_date, total_days,
                                            reason, applied_by, applicant_id, applicant_type)
                VALUES (:school_id, :user_id, :leave_type, '2026-07-01', '2026-07-02', 2, '{MARK} leave',
                        :user_id, :user_id, 'teacher') RETURNING id""",
                user_id=admin_id, leave_type=leave_type, **sid),
            "expense_id": await _one(session, f"""
                INSERT INTO expenses (school_id, expense_date, expense_category_id, description, amount,
                                      total_amount, payment_method_id, requested_by, session_year_id)
                VALUES (:school_id, '2026-07-01', :category, '{MARK} expense', 10, 10, 1, :user_id, :year)
                RETURNING id""",
                category=category, user_id=admin_id, year=year, **sid),
            "attendance_id": await _one(session, """
                INSERT INTO attendance_records (school_id, student_id, class_id, session_year_id, attendance_date,
                                                attendance_status_id, marked_by)
                VALUES (:school_id, :student_id, :class_id, :year, '2026-07-01', 1, :user_id) RETURNING id""",
                student_id=student_id, class_id=fleet["class_ids"][0], year=year, user_id=admin_id, **sid),
            "alert_id": await _one(session, f"""
                INSERT INTO alerts (school_id, alert_type_id, title, message, entity_type, entity_id)
                VALUES (:school_id, (SELECT MIN(id) FROM alert_types), '{MARK} alert', '{MARK} alert message',
                        'student', :student_id) RETURNING id""",
                student_id=student_id, **sid),
            "image_id": await _one(session, f"""
                INSERT INTO gallery_images (school_id, category_id, title, cloudinary_public_id, cloudinary_url)
                VALUES (:school_id, :category, '{MARK} photo', '{MARK.lower()}/photo',
                        'https://res.cloudinary.test/{MARK.lower()}/photo.jpg') RETURNING id""",
                category=gallery_category, **sid),
            "purchase_id": await _one(session, """
                INSERT INTO inventory_purchases (school_id, student_id, session_year_id, purchase_date,
                                                 total_amount, payment_method_id, payment_date)
                VALUES (:school_id, :student_id, :year, '2026-07-01', 10, 1, '2026-07-01') RETURNING id""",
                student_id=student_id, year=year, **sid),
        }
        await session.commit()

    return {
        **ids,
        "student_id": student_id,
        "user_id": admin_id,
        "payment_id": payment["id"],
        "structure_id": structure["id"],
        "assignment_id": assignment_id,
        "pause_id": paused["assignment"]["pauses"][0]["id"],
        "concession_id": concession["id"],
        "sibling_id": sibling_id,
        "head_id": heads["TUITION"],
        "rate_id": fleet["rates"]["flat"]["id"],
        "stop_id": fleet["stops"]["Stop A"],
        "type_id": fleet["type_id"],
        "route_id": fleet["route_id"],
        "vehicle_id": fleet["vehicle_id"],
        "class_id": fleet["class_ids"][0],
        "year_id": year,
        # Texts that identify Sunrise's rows. Any of them in a response to the other school is a leak.
        "fingerprints": [MARK, admission_number, payment["receipt_number"], "Test Route North",
                         "UP91 T 0001", "fee-admin@sunrise-test.in", "fee-staff@sunrise-test.in"],
    }


@pytest.fixture
async def other_with_shop(other_api, make_session, schools):
    """The second school's admin, with the School Shop on so its routes answer instead of refusing."""
    async with make_session(schools["other_id"]) as session:
        await session.execute(text(
            "INSERT INTO school_settings (school_id, key, value) VALUES (:school_id, 'module.shop.enabled', 'true') "
            "ON CONFLICT (school_id, key) DO UPDATE SET value = 'true'"))
        await session.commit()
    return other_api
