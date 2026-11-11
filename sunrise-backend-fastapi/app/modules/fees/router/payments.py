"""Routes: payments, reversals, receipts, student balance."""
import logging
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, get_db
from app.core.tenant import get_session_school, set_session_school
from app.models.user import User
from app.modules.fees import receipts
from app.modules.fees.audit import to_json
from app.modules.fees.deps import can_collect, can_view
from app.modules.fees.schemas import (
    PaymentCreate, PaymentDetail, PaymentOut, ReceiptSend, ReversalCreate, StudentBalance,
)
from app.modules.fees.service import payments as payment_service

router = APIRouter()
logger = logging.getLogger(__name__)


async def _send_receipt_in_background(school_id: int, payment_id: int, user_id: int) -> None:
    """Upload and send a receipt after the payment's request has finished (own session)."""
    async with AsyncSessionLocal() as db:
        set_session_school(db, school_id)
        try:
            await receipts.issue_receipt(db, payment_id, user_id=user_id)
            await db.commit()
        except Exception:
            logger.exception("Sending the receipt of payment %s failed", payment_id)
            await db.rollback()


@router.post("/payments", response_model=PaymentDetail, status_code=status.HTTP_201_CREATED)
async def collect_payment(body: PaymentCreate, background: BackgroundTasks, user: User = Depends(can_collect),
                          db: AsyncSession = Depends(get_db)):
    """Take a payment against any mix of the student's dues. One receipt number; leftover money is credit."""
    payment = await payment_service.collect_payment(db, body, user_id=user.id)
    await db.commit()
    if body.send_receipt:
        background.add_task(_send_receipt_in_background, get_session_school(db), payment.id, user.id)
    return await payment_service.payment_detail(db, payment.id)


@router.get("/payments/{payment_id}", response_model=PaymentDetail)
async def get_payment(payment_id: int, user: User = Depends(can_view), db: AsyncSession = Depends(get_db)):
    return await payment_service.payment_detail(db, payment_id)


@router.post("/payments/{payment_id}/reverse", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
async def reverse_payment(payment_id: int, body: ReversalCreate, user: User = Depends(can_collect),
                          db: AsyncSession = Depends(get_db)):
    """Reverse a payment fully (no amount) or partly. Returns the REVERSAL entry."""
    reversal = await payment_service.reverse_payment(db, payment_id, body, user_id=user.id)
    await db.commit()
    return await payment_service.load_payment(db, reversal.id)


@router.get("/payments/{payment_id}/receipt.pdf")
async def receipt_pdf(payment_id: int, user: User = Depends(can_view), db: AsyncSession = Depends(get_db)):
    """The receipt as a PDF, generated on the fly with the school's branding."""
    data = await receipts.receipt_data(db, payment_id)
    pdf = receipts.render_pdf(data)
    filename = data.receipt_number.replace("/", "-") + ".pdf"
    return StreamingResponse(pdf, media_type="application/pdf",
                             headers={"Content-Disposition": f"inline; filename=\"{filename}\""})


@router.post("/payments/{payment_id}/receipt/send")
async def send_receipt(payment_id: int, body: ReceiptSend, user: User = Depends(can_collect),
                       db: AsyncSession = Depends(get_db)):
    """Upload the receipt to the school's Cloudinary folder and send it on WhatsApp. Reports each step."""
    result = await receipts.issue_receipt(db, payment_id, upload=body.upload, whatsapp=body.whatsapp,
                                          phone=body.phone, user_id=user.id)
    await db.commit()
    return JSONResponse(to_json(result))


@router.get("/students/{student_id}/payments", response_model=List[PaymentOut])
async def student_payments(student_id: int, session_year_id: Optional[int] = None, user: User = Depends(can_view),
                           db: AsyncSession = Depends(get_db)):
    return await payment_service.list_payments(db, student_id, session_year_id=session_year_id)


@router.get("/students/{student_id}/balance", response_model=StudentBalance)
async def student_balance(student_id: int, as_of: Optional[date] = None, user: User = Depends(can_view),
                          db: AsyncSession = Depends(get_db)):
    """One balance across every fee head: dues billed minus paid. Unallocated credit is shown separately."""
    return await payment_service.student_balance(db, student_id, as_of=as_of)
