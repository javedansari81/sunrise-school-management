"""Routes: a student's own fees. Students have no fee permission; they only ever see themselves."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.student import Student
from app.models.user import User
from app.modules.fees import receipts
from app.modules.fees.audit import to_json
from app.modules.fees.constants import DueStatus, PaymentKind
from app.modules.fees.models import FeeHead
from app.modules.fees.schemas import DueOut, PaymentOut
from app.modules.fees.service import dues as dues_service
from app.modules.fees.service import payments as payment_service

router = APIRouter()


async def current_student(user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)) -> Student:
    student = (await db.execute(select(Student).where(Student.user_id == user.id))).scalar_one_or_none()
    if student is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students have a fee statement")
    return student


@router.get("/my/statement")
async def my_statement(session_year_id: Optional[int] = None, student: Student = Depends(current_student),
                       db: AsyncSession = Depends(get_db)):
    """The logged-in student's balance, dues and payments. The balance covers every session."""
    dues = [d for d in await dues_service.list_dues(db, student.id, session_year_id=session_year_id)
            if d.status != DueStatus.CANCELLED.value]
    payments = await payment_service.list_payments(db, student.id, session_year_id=session_year_id)
    heads = {h.id: h.name for h in (await db.execute(select(FeeHead))).scalars()}
    return JSONResponse(to_json({
        "student_id": student.id,
        "student_name": f"{student.first_name} {student.last_name}",
        "admission_number": student.admission_number,
        "session_year_id": session_year_id,
        "balance": await payment_service.student_balance(db, student.id),
        "dues": [{**DueOut.model_validate(d).model_dump(), "fee_head_name": heads.get(d.fee_head_id)} for d in dues],
        "payments": [PaymentOut.model_validate(p).model_dump(exclude={"allocations", "reversal_allocations"})
                     for p in payments],
    }))


@router.get("/my/payments/{payment_id}/receipt.pdf")
async def my_receipt_pdf(payment_id: int, student: Student = Depends(current_student),
                         db: AsyncSession = Depends(get_db)):
    """Receipt of one of the student's own payments."""
    payment = await payment_service.load_payment(db, payment_id)
    if payment.student_id != student.id or payment.kind != PaymentKind.PAYMENT.value:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Payment {payment_id} not found")
    data = await receipts.receipt_data(db, payment_id)
    filename = data.receipt_number.replace("/", "-") + ".pdf"
    return StreamingResponse(receipts.render_pdf(data), media_type="application/pdf",
                             headers={"Content-Disposition": f"inline; filename=\"{filename}\""})
