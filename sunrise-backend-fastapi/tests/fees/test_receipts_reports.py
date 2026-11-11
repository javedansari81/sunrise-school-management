"""
Steps E and F: reversal audit trail, receipts (PDF, Cloudinary, WhatsApp with
per-school settings) and reports. Cloudinary and WhatsApp are replaced by fakes.
"""
from datetime import date

import pytest
from sqlalchemy import select, update

from app.models.school import SchoolSetting
from app.modules.fees import receipts
from app.modules.fees.models import FeeAuditLog
from app.services.cloudinary_receipt_service import CloudinaryReceiptService
from app.services.whatsapp_service import WhatsAppService

from .test_ledger import _build, _generate, _pay, _student, priced  # noqa: F401  (fixture)


@pytest.fixture
async def billed(admin_api, priced, sunrise_session):  # noqa: F811
    """One class-1 student with tuition April to June 2026 (3 x 1000)."""
    sid = await _student(sunrise_session, priced, father_phone="9876543210")
    await _build(admin_api, priced)
    await _generate(admin_api, priced, "2026-06-01")
    return {"student_id": sid, **priced}


@pytest.fixture
def fakes(monkeypatch):
    calls = {"upload": [], "whatsapp": []}

    def fake_upload(self, pdf_buffer, payment_id, receipt_number, folder=None):
        assert pdf_buffer.read(4) == b"%PDF"
        calls["upload"].append({"payment_id": payment_id, "receipt_number": receipt_number, "folder": folder})
        return f"https://res.cloudinary.test/{folder}/receipt_{payment_id}.pdf", f"{folder}/receipt_{payment_id}"

    async def fake_send(self, phone_number, student_name, amount, receipt_url=None, payment_id=None, template_sid=None):
        calls["whatsapp"].append({"phone": phone_number, "amount": amount, "url": receipt_url, "template": template_sid})
        return {"success": True, "status": "SENT", "message_sid": "SM-test"}

    monkeypatch.setattr(CloudinaryReceiptService, "__init__", lambda self: None)
    monkeypatch.setattr(CloudinaryReceiptService, "upload_receipt", fake_upload)
    monkeypatch.setattr(WhatsAppService, "__init__", lambda self: None)
    monkeypatch.setattr(WhatsAppService, "send_fee_media_receipt", fake_send)
    return calls


# ---------------------------------------------------------------------------
# Reversal audit (step E)
# ---------------------------------------------------------------------------

async def test_reversals_are_audited(admin_api, billed, sunrise_session):
    paid = await _pay(admin_api, billed["student_id"], "1500.00")
    await admin_api.post(f"/payments/{paid['id']}/reverse", json={"amount": "200.00", "reversal_reason_id": 1,
                                                                  "remarks": "Wrong amount"})
    async with sunrise_session() as session:
        entries = (await session.execute(
            select(FeeAuditLog).where(FeeAuditLog.entity_type == "payment", FeeAuditLog.entity_id == paid["id"])
            .order_by(FeeAuditLog.id))).scalars().all()
    assert [e.action for e in entries] == ["PAY", "REVERSE"]
    reverse = entries[1]
    assert reverse.remarks == "Wrong amount" and reverse.performed_by is not None
    assert reverse.new_values["amount"] == "200.00" and reverse.new_values["full"] is False
    assert reverse.new_values["from_dues"][0]["amount"] == "200.00"


# ---------------------------------------------------------------------------
# Receipts
# ---------------------------------------------------------------------------

async def test_receipt_pdf_uses_school_branding(admin_api, billed, sunrise_session):
    paid = await _pay(admin_api, billed["student_id"], "1500.00")
    r = await admin_api.get(f"/payments/{paid['id']}/receipt.pdf")
    assert r.status_code == 200 and r.headers["content-type"] == "application/pdf"
    assert r.content[:4] == b"%PDF"
    assert "SUN-2026-27-000001.pdf" in r.headers["content-disposition"]

    async with sunrise_session() as session:
        data = await receipts.receipt_data(session, paid["id"])
    assert data.school_name == "Sunrise National Public School"
    assert data.logo == "static:images/school_logo_bw.jpeg"
    assert receipts._logo_image(data.logo) is not None
    assert [(line.period.month, str(line.paid_now), str(line.balance_after)) for line in data.lines] == [
        (4, "1000.00", "0.00"), (5, "500.00", "500.00")]
    assert (str(data.balance), str(data.credit)) == ("1500.00", "0.00")


async def test_receipt_upload_and_whatsapp_use_school_settings(admin_api, billed, sunrise_session, fakes):
    async with sunrise_session() as session:
        session.add(SchoolSetting(key="whatsapp.media_receipt_template_sid", value="HX-sunrise-template"))
        await session.commit()
    paid = await _pay(admin_api, billed["student_id"], "1000.00")

    r = await admin_api.post(f"/payments/{paid['id']}/receipt/send", json={})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["uploaded"] is True and body["whatsapp"]["status"] == "SENT"
    assert fakes["upload"] == [{"payment_id": paid["id"], "receipt_number": "SUN/2026-27/000001",
                                "folder": "sunrise/receipts"}]
    assert fakes["whatsapp"][0]["template"] == "HX-sunrise-template"
    assert fakes["whatsapp"][0]["phone"] == "9876543210"
    assert (await admin_api.get(f"/payments/{paid['id']}")).json()["receipt_url"] == body["receipt_url"]

    async with sunrise_session() as session:
        await session.execute(update(SchoolSetting).where(SchoolSetting.key == "whatsapp.media_receipt_template_sid")
                              .values(key="whatsapp.receipts_enabled", value="false"))
        await session.commit()
    again = (await admin_api.post(f"/payments/{paid['id']}/receipt/send", json={"upload": False})).json()
    assert again["whatsapp"] == {"status": "DISABLED"}


async def test_receipt_upload_failure_is_reported_not_raised(admin_api, billed, monkeypatch):
    def broken(self, *args, **kwargs):
        raise RuntimeError("Cloudinary is down")
    monkeypatch.setattr(CloudinaryReceiptService, "__init__", lambda self: None)
    monkeypatch.setattr(CloudinaryReceiptService, "upload_receipt", broken)
    paid = await _pay(admin_api, billed["student_id"], "1000.00")
    r = (await admin_api.post(f"/payments/{paid['id']}/receipt/send", json={})).json()
    assert r["uploaded"] is False and "Cloudinary is down" in r["upload_error"]
    assert r["whatsapp"] == {"status": "NO_RECEIPT_URL"}


async def test_no_receipt_for_a_reversal(admin_api, billed):
    paid = await _pay(admin_api, billed["student_id"], "1000.00")
    rev = (await admin_api.post(f"/payments/{paid['id']}/reverse", json={"reversal_reason_id": 1})).json()
    assert (await admin_api.get(f"/payments/{rev['id']}/receipt.pdf")).status_code == 422


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

async def test_collection_report(admin_api, billed):
    h = billed["heads"]
    sid = billed["student_id"]
    first = await _pay(admin_api, sid, "1500.00", payment_date="2026-06-02")
    await _pay(admin_api, sid, "2000.00", payment_date="2026-06-03", payment_method_id=2)  # 1500 dues + 500 credit
    await admin_api.post(f"/payments/{first['id']}/reverse", json={"amount": "300.00", "reversal_reason_id": 1})

    r = await admin_api.get("/reports/collection", params={"date_from": "2026-06-01", "date_to": "2026-06-03"})
    assert r.status_code == 200, r.text
    rep = r.json()
    assert (rep["received"], rep["reversed"], rep["net"], rep["payments"]) == ("3500.00", "0.00", "3500.00", 2)
    assert [(d["date"], d["amount"]) for d in rep["by_day"]] == [("2026-06-02", "1500.00"), ("2026-06-03", "2000.00")]
    assert {m["method"]: m["amount"] for m in rep["by_method"]} == {"CASH": "1500.00", "UPI": "2000.00"}
    assert [(x["fee_head_id"], x["amount"]) for x in rep["by_head"]] == [(h["TUITION"], "3000.00")]
    assert rep["not_allocated"] == "500.00"

    # The reversal (made today) is counted on its own date
    today = date.today().isoformat()
    rep = (await admin_api.get("/reports/collection", params={"date_from": today, "date_to": today})).json()
    assert (rep["reversed"], rep["net"]) == ("300.00", "-300.00")
    assert [(x["fee_head_id"], x["amount"]) for x in rep["by_head"]] == [(h["TUITION"], "-300.00")]


async def test_pending_by_class_and_ledger(admin_api, billed, sunrise_session):
    sid = billed["student_id"]
    await _student(sunrise_session, billed, class_id=billed["class_ids"][1])
    await _build(admin_api, billed)
    await _generate(admin_api, billed, "2026-06-01")
    await _pay(admin_api, sid, "1200.00", payment_date="2026-05-05")

    rep = (await admin_api.get("/reports/pending-by-class",
                               params={"session_year_id": billed["year_id"], "as_of": "2026-06-05"})).json()
    by_class = {c["class_id"]: c for c in rep["classes"]}
    c1, c2 = billed["class_ids"]
    assert (by_class[c1]["students_with_dues"], by_class[c1]["pending"], by_class[c1]["overdue"]) == (1, "1800.00", "800.00")
    assert (by_class[c2]["pending"], by_class[c2]["overdue"]) == ("5100.00", "3400.00")
    assert rep["total_pending"] == "6900.00"

    ledger = (await admin_api.get(f"/students/{sid}/ledger", params={"session_year_id": billed["year_id"]})).json()
    assert [(e["type"], e["debit"], e["credit"], e["balance"]) for e in ledger["entries"]] == [
        ("DUE", "1000.00", "0.00", "1000.00"),
        ("PAYMENT", "0.00", "1200.00", "-200.00"),
        ("DUE", "1000.00", "0.00", "800.00"),
        ("DUE", "1000.00", "0.00", "1800.00"),
    ]
    assert ledger["balance"] == "1800.00"


async def test_consistency_check_and_report_permissions(admin_api, staff_api, billed):
    paid = await _pay(admin_api, billed["student_id"], "2500.00")
    await admin_api.post(f"/payments/{paid['id']}/reverse", json={"amount": "700.00", "reversal_reason_id": 1})
    check = (await admin_api.get("/reports/consistency")).json()
    assert check["ok"] is True and check["dues_checked"] >= 3 and check["payments_checked"] == 2
    assert (await staff_api.get("/reports/consistency")).status_code == 403
    assert (await staff_api.get(f"/students/{billed['student_id']}/ledger")).status_code == 200  # VIEW_FEES


async def test_reports_are_per_school(admin_api, other_api, billed):
    await _pay(admin_api, billed["student_id"], "1000.00", payment_date="2026-06-02")
    rep = (await other_api.get("/reports/collection", params={"date_from": "2026-06-01", "date_to": "2026-06-30"})).json()
    assert rep["received"] == "0.00" and rep["by_head"] == []
    assert (await other_api.get(f"/students/{billed['student_id']}/ledger")).status_code == 404
