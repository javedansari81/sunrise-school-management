"""
Receipts of the unified fee module: one PDF per payment, whatever fee heads it paid.

Branding comes from the school (schools row: name, address, phone, email,
website) and school_settings, never from code:

    receipt.logo                          static:<path under app/static> or an https URL
    cloudinary.receipt_folder             default "<school code>/receipts"
    whatsapp.media_receipt_template_sid   default TWILIO_WHATSAPP_MEDIA_RECEIPT_SID
    whatsapp.receipts_enabled             "false" turns WhatsApp receipts off

Generating a receipt never changes money. Uploading stores the receipt URL on
the payment; sending is best effort and reports what happened.
"""
import io
import logging
import os
import urllib.request
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import List, Optional

from fastapi.concurrency import run_in_threadpool
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from xml.sax.saxutils import escape

from app.core.tenant import get_session_school
from app.models.metadata import Class, PaymentMethod
from app.models.school import School
from app.modules.fees import audit, repository as repo
from app.modules.fees.constants import AuditAction, PaymentKind
from app.modules.fees.errors import Invalid
from app.modules.fees.models import FeeHead, PaymentAllocation, StudentDue
from app.modules.fees.service.payments import load_payment, student_balance

logger = logging.getLogger(__name__)

SETTING_LOGO = "receipt.logo"
SETTING_CLOUDINARY_FOLDER = "cloudinary.receipt_folder"
SETTING_WHATSAPP_TEMPLATE = "whatsapp.media_receipt_template_sid"
SETTING_WHATSAPP_ENABLED = "whatsapp.receipts_enabled"

STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "static")


@dataclass
class ReceiptLine:
    head: str
    period: date
    net_amount: Decimal
    paid_before: Decimal
    paid_now: Decimal
    balance_after: Decimal


@dataclass
class ReceiptData:
    school_name: str
    school_lines: List[str]
    logo: Optional[str]
    receipt_number: str
    payment_date: date
    amount: Decimal
    method: str
    transaction_id: Optional[str]
    student_name: str
    father_name: str
    admission_number: str
    class_name: str
    phone: Optional[str]
    lines: List[ReceiptLine] = field(default_factory=list)
    credit_added: Decimal = Decimal("0.00")
    balance: Decimal = Decimal("0.00")
    credit: Decimal = Decimal("0.00")


async def receipt_data(db: AsyncSession, payment_id: int) -> ReceiptData:
    payment = await load_payment(db, payment_id)
    if payment.kind != PaymentKind.PAYMENT.value:
        raise Invalid("Receipts are issued for payments, not reversals")
    school = await db.get(School, get_session_school(db))
    student = await repo.student_or_404(db, payment.student_id)
    klass = await db.get(Class, student.class_id)
    method = await db.get(PaymentMethod, payment.payment_method_id)

    rows = (await db.execute(
        select(PaymentAllocation, StudentDue, FeeHead)
        .join(StudentDue, StudentDue.id == PaymentAllocation.student_due_id)
        .join(FeeHead, FeeHead.id == StudentDue.fee_head_id)
        .where(PaymentAllocation.payment_id == payment.id, PaymentAllocation.is_reversal == False)  # noqa: E712
        .order_by(StudentDue.period, FeeHead.sort_order, StudentDue.id)
    )).all()
    lines = []
    for alloc, due, head in rows:
        # Paid before = everything allocated to this due by earlier allocation rows
        before = (await db.execute(
            select(PaymentAllocation.amount).where(
                PaymentAllocation.student_due_id == due.id, PaymentAllocation.id < alloc.id)
        )).scalars().all()
        paid_before = sum(before, Decimal("0.00"))
        lines.append(ReceiptLine(
            head=head.name, period=due.period, net_amount=due.net_amount, paid_before=paid_before,
            paid_now=alloc.amount, balance_after=due.net_amount - paid_before - alloc.amount,
        ))
    allocated_now = sum((line.paid_now for line in lines), Decimal("0.00"))
    balance = await student_balance(db, student.id)

    contact = " | ".join(x for x in (
        f"Phone: {school.phone}" if school.phone else None,
        f"Email: {school.email}" if school.email else None,
        f"Web: {school.website}" if school.website else None,
    ) if x)
    return ReceiptData(
        school_name=school.name, school_lines=[x for x in (school.address, contact) if x],
        logo=await repo.setting(db, SETTING_LOGO) or school.logo_url,
        receipt_number=payment.receipt_number, payment_date=payment.payment_date, amount=payment.amount,
        method=(method.description or method.name) if method is not None else "",
        transaction_id=payment.transaction_id,
        student_name=f"{student.first_name} {student.last_name}", father_name=student.father_name or "",
        admission_number=student.admission_number, class_name=(klass.description if klass else ""),
        phone=student.father_phone or student.phone or student.mother_phone,
        lines=lines, credit_added=payment.amount - allocated_now,
        balance=balance["balance"], credit=balance["credit"],
    )


def _logo_image(logo: Optional[str]):
    if not logo:
        return None
    try:
        if logo.startswith("static:"):
            path = os.path.normpath(os.path.join(STATIC_DIR, logo[len("static:"):]))
            if not path.startswith(os.path.normpath(STATIC_DIR)) or not os.path.exists(path):
                return None
            return Image(path, width=0.9 * inch, height=0.9 * inch)
        if logo.startswith("https://"):
            with urllib.request.urlopen(logo, timeout=5) as response:  # noqa: S310 (https only)
                data = io.BytesIO(response.read())
            ImageReader(data)  # validates the image
            data.seek(0)
            return Image(data, width=0.9 * inch, height=0.9 * inch)
    except Exception as error:  # a missing logo never blocks a receipt
        logger.warning("Receipt logo %r could not be loaded: %s", logo, error)
    return None


def _rs(amount: Decimal) -> str:
    return f"Rs. {amount:,.2f}"


def render_pdf(data: ReceiptData) -> io.BytesIO:
    styles = getSampleStyleSheet()
    centre = ParagraphStyle("centre", parent=styles["Normal"], alignment=TA_CENTER, fontSize=9, leading=12)
    section = ParagraphStyle("section", parent=styles["Normal"], alignment=TA_CENTER, fontSize=10,
                             fontName="Helvetica-Bold", spaceBefore=6, spaceAfter=4)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0.6 * inch, leftMargin=0.6 * inch,
                            topMargin=0.5 * inch, bottomMargin=0.5 * inch,
                            title=f"Receipt {data.receipt_number}")
    width = A4[0] - 1.2 * inch
    grid = TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9), ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ])
    elements = []

    info = Paragraph(
        f"<b><font size=16>{escape(data.school_name.upper())}</font></b><br/>"
        + "<br/>".join(escape(x) for x in data.school_lines), centre)
    logo = _logo_image(data.logo)
    if logo is not None:
        header = Table([[logo, info]], colWidths=[1.1 * inch, width - 1.1 * inch])
        header.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
        elements.append(header)
    else:
        elements.append(info)
    rule = Table([[""]], colWidths=[width])
    rule.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, 0), 1, colors.black)]))
    elements += [rule, Spacer(1, 0.1 * inch), Paragraph("<b><font size=13>FEE RECEIPT</font></b>", centre),
                 Spacer(1, 0.1 * inch)]

    top = Table([
        ["Receipt No:", data.receipt_number, "Date:", data.payment_date.strftime("%d %b %Y")],
        ["Amount:", _rs(data.amount), "Paid by:", data.method + (f" ({data.transaction_id})" if data.transaction_id else "")],
        ["Student:", data.student_name, "Father:", data.father_name],
        ["Class:", data.class_name, "Adm. No:", data.admission_number],
    ], colWidths=[0.95 * inch, width / 2 - 0.95 * inch, 0.95 * inch, width / 2 - 0.95 * inch])
    top.setStyle(grid)
    top.setStyle(TableStyle([("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                             ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold")]))
    elements.append(top)

    elements.append(Paragraph("PAID AGAINST", section))
    rows = [["Fee", "Month", "Due", "Paid before", "Paid now", "Balance"]]
    for line in data.lines:
        rows.append([line.head, line.period.strftime("%b %Y"), _rs(line.net_amount), _rs(line.paid_before),
                     _rs(line.paid_now), _rs(line.balance_after)])
    if data.credit_added > 0:
        rows.append(["Advance (credit)", "", "", "", _rs(data.credit_added), ""])
    rows.append(["Total", "", "", "", _rs(data.amount), ""])
    table = Table(rows, colWidths=[1.6 * inch, 0.9 * inch] + [(width - 2.5 * inch) / 4] * 4, repeatRows=1)
    table.setStyle(grid)
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey), ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
    ]))
    elements.append(table)

    summary = Table([["Balance due after this payment:", _rs(data.balance)],
                     ["Credit held for future dues:", _rs(data.credit)]],
                    colWidths=[width - 1.6 * inch, 1.6 * inch])
    summary.setStyle(grid)
    summary.setStyle(TableStyle([("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"), ("ALIGN", (1, 0), (1, -1), "RIGHT")]))
    elements += [Spacer(1, 0.15 * inch), summary, Spacer(1, 0.2 * inch),
                 Paragraph("<font color='grey' size=8>System generated receipt. Contact the school office for queries.</font>", centre)]
    doc.build(elements)
    buffer.seek(0)
    return buffer


async def issue_receipt(
    db: AsyncSession, payment_id: int, *, upload: bool = True, whatsapp: bool = True,
    phone: Optional[str] = None, user_id: Optional[int] = None,
) -> dict:
    """
    Render the receipt, upload it to the school's Cloudinary folder (storing the
    URL on the payment) and send it on WhatsApp with the school's template.
    Returns what happened; failures are reported, not raised. Does not commit.
    """
    data = await receipt_data(db, payment_id)
    payment = await load_payment(db, payment_id)
    result = {"payment_id": payment_id, "receipt_number": data.receipt_number,
              "receipt_url": payment.receipt_url, "uploaded": False, "whatsapp": None}
    pdf = render_pdf(data)

    if upload:
        school = await db.get(School, get_session_school(db))
        folder = await repo.setting(db, SETTING_CLOUDINARY_FOLDER) or f"{school.code}/receipts"
        try:
            from app.services.cloudinary_receipt_service import CloudinaryReceiptService
            url, public_id = await run_in_threadpool(
                CloudinaryReceiptService().upload_receipt, pdf, payment.id, data.receipt_number, folder)
            payment.receipt_url, payment.receipt_cloudinary_id = url, public_id
            await db.flush()
            result.update(uploaded=True, receipt_url=url)
        except Exception as error:
            logger.error("Receipt upload failed for payment %s: %s", payment_id, error)
            result["upload_error"] = str(getattr(error, "detail", error))

    if whatsapp:
        enabled = (await repo.setting(db, SETTING_WHATSAPP_ENABLED, "true")).lower() != "false"
        to = phone or data.phone
        if not enabled:
            result["whatsapp"] = {"status": "DISABLED"}
        elif not result["receipt_url"]:
            result["whatsapp"] = {"status": "NO_RECEIPT_URL"}
        elif not to:
            result["whatsapp"] = {"status": "NO_PHONE"}
        else:
            from app.services.whatsapp_service import WhatsAppService
            result["whatsapp"] = await WhatsAppService().send_fee_media_receipt(
                phone_number=to, student_name=data.student_name, amount=float(data.amount),
                receipt_url=result["receipt_url"], payment_id=payment.id,
                template_sid=await repo.setting(db, SETTING_WHATSAPP_TEMPLATE),
            )

    await audit.record(db, entity_type="payment", entity_id=payment.id, action=AuditAction.RECEIPT.value, performed_by=user_id,
                       new={k: v for k, v in result.items() if k != "whatsapp"} | {
                           "whatsapp_status": (result["whatsapp"] or {}).get("status")})
    return result

