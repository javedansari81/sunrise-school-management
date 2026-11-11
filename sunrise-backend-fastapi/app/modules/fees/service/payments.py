"""
Payments, allocations, credit and reversals.

* A payment settles any mix of the student's open dues and gets one receipt
  number from the school's series for the session (SUN/2026-27/000123). The
  number is taken under a row lock, so two cashiers never get the same one.
* Money not allocated to a due is the student's credit (decision 10). It is
  allocated automatically when new dues are generated, oldest due first.
* A reversal is a REVERSAL payment with a negative amount. It takes the money
  back from the payment's unallocated credit first, then from its allocations,
  latest due first, by adding negative allocation rows. Nothing is edited or
  deleted, so the ledger stays auditable.

Payments of one student are serialised by locking the student row.
"""
from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tenant import get_session_school
from app.models.metadata import PaymentMethod, ReversalReason
from app.models.school import School
from app.models.student import Student
from app.modules.fees import audit, repository as repo
from app.modules.fees.constants import (
    AuditAction, DueStatus, OPEN_DUE_STATUSES, PaymentKind, SETTING_RECEIPT_PREFIX,
)
from app.modules.fees.errors import Conflict, Invalid, NotFound
from app.modules.fees.models import FeeHead, Payment, PaymentAllocation, ReceiptSequence, StudentDue
from app.modules.fees.provisioning import default_receipt_prefix
from app.modules.fees.schemas import PaymentCreate, ReversalCreate

ENTITY = "payment"
ZERO = Decimal("0.00")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def set_due_status(due: StudentDue) -> None:
    if due.status == DueStatus.CANCELLED.value:
        return
    if due.paid_amount <= 0:
        due.status = DueStatus.WAIVED.value if due.net_amount == 0 and due.concession_amount > 0 else DueStatus.PENDING.value
    elif due.paid_amount < due.net_amount:
        due.status = DueStatus.PARTIAL.value
    else:
        due.status = DueStatus.PAID.value


async def _lock_student(db: AsyncSession, student_id: int) -> Student:
    student = (await db.execute(
        select(Student).where(Student.id == student_id).with_for_update()
    )).scalar_one_or_none()
    if student is None:
        raise NotFound(f"Student {student_id} not found")
    return student


async def _open_dues(db: AsyncSession, student_id: int) -> List[StudentDue]:
    """Open dues of a student, oldest due date first, locked for update."""
    return list((await db.execute(
        select(StudentDue)
        .join(FeeHead, FeeHead.id == StudentDue.fee_head_id)
        .where(StudentDue.student_id == student_id, StudentDue.status.in_(OPEN_DUE_STATUSES))
        .order_by(StudentDue.due_date, StudentDue.period, FeeHead.sort_order, StudentDue.id)
        .with_for_update(of=StudentDue)
    )).scalars())


async def next_receipt_number(db: AsyncSession, session_year_id: int) -> str:
    """Take the next receipt number of the school and session (row-locked until commit)."""
    session_year = await repo.session_year_or_404(db, session_year_id)
    school_id = get_session_school(db)
    prefix = await repo.setting(db, SETTING_RECEIPT_PREFIX)
    if not prefix:
        school = await db.get(School, school_id)
        prefix = default_receipt_prefix(school.code if school else "")
    await db.execute(
        insert(ReceiptSequence)
        .values(school_id=school_id, session_year_id=session_year_id, prefix=prefix, next_number=1)
        .on_conflict_do_nothing(constraint="receipt_sequences_school_session_unique")
    )
    sequence = (await db.execute(
        select(ReceiptSequence).where(ReceiptSequence.session_year_id == session_year_id)
        .with_for_update().execution_options(populate_existing=True)
    )).scalar_one()
    number = sequence.next_number
    sequence.next_number = number + 1
    await db.flush()
    return f"{sequence.prefix}/{session_year.name}/{number:0{sequence.padding}d}"


async def _allocated_by_payment(db: AsyncSession, payment_ids: Sequence[int]) -> Dict[int, Decimal]:
    if not payment_ids:
        return {}
    rows = await db.execute(
        select(PaymentAllocation.payment_id, func.sum(PaymentAllocation.amount))
        .where(PaymentAllocation.payment_id.in_(payment_ids))
        .group_by(PaymentAllocation.payment_id)
    )
    return {pid: total or ZERO for pid, total in rows.all()}


async def _reversed_by_payment(db: AsyncSession, payment_ids: Sequence[int]) -> Dict[int, Decimal]:
    """Amount taken back from each payment by reversals (positive numbers)."""
    if not payment_ids:
        return {}
    rows = await db.execute(
        select(Payment.reverses_payment_id, func.sum(Payment.amount))
        .where(Payment.reverses_payment_id.in_(payment_ids), Payment.kind == PaymentKind.REVERSAL.value)
        .group_by(Payment.reverses_payment_id)
    )
    return {pid: -(total or ZERO) for pid, total in rows.all()}


async def _payments_with_credit(db: AsyncSession, student_id: int) -> List[tuple]:
    """(payment, unallocated amount) for the student's payments with money left, oldest first."""
    payments = list((await db.execute(
        select(Payment).where(Payment.student_id == student_id, Payment.kind == PaymentKind.PAYMENT.value)
        .order_by(Payment.payment_date, Payment.id)
    )).scalars())
    ids = [p.id for p in payments]
    allocated = await _allocated_by_payment(db, ids)
    reversed_ = await _reversed_by_payment(db, ids)
    result = []
    for p in payments:
        left = p.amount - reversed_.get(p.id, ZERO) - allocated.get(p.id, ZERO)
        if left > 0:
            result.append((p, left))
    return result


async def student_credit(db: AsyncSession, student_id: int) -> Decimal:
    return sum((left for _, left in await _payments_with_credit(db, student_id)), ZERO)


def _allocate(payment: Payment, dues: List[StudentDue], available: Decimal, user_id: Optional[int],
              db: AsyncSession, limits: Optional[Dict[int, Decimal]] = None) -> Decimal:
    """Allocate up to `available` to the dues in order. Returns the amount allocated."""
    used = ZERO
    for due in dues:
        if available - used <= 0:
            break
        room = due.net_amount - due.paid_amount
        if limits is not None:
            room = min(room, limits.get(due.id, ZERO))
        take = min(room, available - used)
        if take <= 0:
            continue
        db.add(PaymentAllocation(payment_id=payment.id, student_due_id=due.id, amount=take, created_by=user_id))
        due.paid_amount += take
        set_due_status(due)
        used += take
    return used


# ---------------------------------------------------------------------------
# Collect
# ---------------------------------------------------------------------------

async def collect_payment(db: AsyncSession, data: PaymentCreate, *, user_id: int) -> Payment:
    student = await _lock_student(db, data.student_id)
    if await db.get(PaymentMethod, data.payment_method_id) is None:
        raise Invalid(f"Payment method {data.payment_method_id} not found")
    session_year_id = data.session_year_id or student.session_year_id
    await repo.session_year_or_404(db, session_year_id)

    open_dues = await _open_dues(db, student.id)
    by_id = {d.id: d for d in open_dues}
    limits = None
    if data.allocations:
        limits = {}
        for a in data.allocations:
            due = by_id.get(a.due_id)
            if due is None:
                raise Invalid(f"Due {a.due_id} is not an open due of student {student.id}")
            if a.due_id in limits:
                raise Invalid(f"Due {a.due_id} is listed twice")
            if a.amount > due.net_amount - due.paid_amount:
                raise Invalid(f"Due {a.due_id} has only {due.net_amount - due.paid_amount} left to pay")
            limits[a.due_id] = a.amount
        if sum(limits.values(), ZERO) > data.amount:
            raise Invalid("The allocations add up to more than the amount paid")
        targets = [by_id[a.due_id] for a in data.allocations]
    elif data.due_ids:
        missing = [i for i in data.due_ids if i not in by_id]
        if missing:
            raise Invalid(f"Not open dues of student {student.id}: {missing}")
        targets = [by_id[i] for i in dict.fromkeys(data.due_ids)]
    else:
        targets = open_dues

    payment = Payment(
        student_id=student.id, session_year_id=session_year_id, kind=PaymentKind.PAYMENT.value,
        receipt_number=await next_receipt_number(db, session_year_id), amount=data.amount,
        payment_method_id=data.payment_method_id, payment_date=data.payment_date or date.today(),
        transaction_id=data.transaction_id, remarks=data.remarks, created_by=user_id,
    )
    db.add(payment)
    await db.flush()
    allocated = _allocate(payment, targets, data.amount, user_id, db, limits)
    await db.flush()
    await audit.record(db, entity_type=ENTITY, entity_id=payment.id, action=AuditAction.PAY.value, performed_by=user_id,
                       new={"receipt_number": payment.receipt_number, "amount": payment.amount,
                            "allocated": allocated, "credit": data.amount - allocated,
                            "dues": [d.id for d in targets]})
    return payment


async def apply_credit(db: AsyncSession, student_id: int, *, user_id: Optional[int]) -> Decimal:
    """Allocate the student's unallocated payments to open dues, oldest first. Returns the amount applied."""
    credits = await _payments_with_credit(db, student_id)
    if not credits:
        return ZERO
    await _lock_student(db, student_id)
    dues = await _open_dues(db, student_id)
    applied = ZERO
    for payment, left in credits:
        used = _allocate(payment, dues, left, user_id, db)
        if used > 0:
            applied += used
            await db.flush()
            await audit.record(db, entity_type=ENTITY, entity_id=payment.id, action=AuditAction.APPLY_CREDIT.value,
                               performed_by=user_id, new={"applied": used})
    return applied


# ---------------------------------------------------------------------------
# Reverse
# ---------------------------------------------------------------------------

async def reverse_payment(db: AsyncSession, payment_id: int, data: ReversalCreate, *, user_id: int) -> Payment:
    original = await repo.get_or_404(db, Payment, payment_id, "Payment")
    if original.kind != PaymentKind.PAYMENT.value:
        raise Invalid("A reversal cannot be reversed")
    if await db.get(ReversalReason, data.reversal_reason_id) is None:
        raise Invalid(f"Reversal reason {data.reversal_reason_id} not found")
    await _lock_student(db, original.student_id)

    already = (await _reversed_by_payment(db, [original.id])).get(original.id, ZERO)
    reversible = original.amount - already
    if reversible <= 0:
        raise Conflict(f"Payment {original.receipt_number} is already fully reversed")
    amount = data.amount if data.amount is not None else reversible
    if amount > reversible:
        raise Invalid(f"Only {reversible} of payment {original.receipt_number} can still be reversed")

    reversal = Payment(
        student_id=original.student_id, session_year_id=original.session_year_id, kind=PaymentKind.REVERSAL.value,
        amount=-amount, payment_method_id=original.payment_method_id, payment_date=date.today(),
        reverses_payment_id=original.id, reversal_reason_id=data.reversal_reason_id, remarks=data.remarks,
        created_by=user_id,
    )
    db.add(reversal)
    await db.flush()

    # Credit first, then allocations from the latest due back
    allocated = (await _allocated_by_payment(db, [original.id])).get(original.id, ZERO)
    unallocated = original.amount - already - allocated
    to_take = amount - min(unallocated, amount)
    taken_from: List[dict] = []
    if to_take > 0:
        net_by_due: Dict[int, Decimal] = defaultdict(lambda: ZERO)
        for a in (await db.execute(
            select(PaymentAllocation).where(PaymentAllocation.payment_id == original.id)
        )).scalars():
            net_by_due[a.student_due_id] += a.amount
        due_ids = [i for i, v in net_by_due.items() if v > 0]
        dues = list((await db.execute(
            select(StudentDue).where(StudentDue.id.in_(due_ids))
            .order_by(StudentDue.due_date.desc(), StudentDue.period.desc(), StudentDue.id.desc())
            .with_for_update()
        )).scalars())
        for due in dues:
            if to_take <= 0:
                break
            take = min(net_by_due[due.id], to_take)
            db.add(PaymentAllocation(
                payment_id=original.id, student_due_id=due.id, amount=-take, is_reversal=True,
                reversal_payment_id=reversal.id, created_by=user_id,
            ))
            due.paid_amount -= take
            set_due_status(due)
            to_take -= take
            taken_from.append({"due_id": due.id, "amount": take})
    await db.flush()
    await audit.record(db, entity_type=ENTITY, entity_id=original.id, action=AuditAction.REVERSE.value,
                       performed_by=user_id, remarks=data.remarks,
                       new={"reversal_id": reversal.id, "amount": amount, "full": amount == reversible,
                            "reason_id": data.reversal_reason_id, "from_credit": amount - sum((t["amount"] for t in taken_from), ZERO),
                            "from_dues": taken_from})
    return reversal


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

async def load_payment(db: AsyncSession, payment_id: int) -> Payment:
    """A payment with both allocation lists freshly loaded (they change after a reversal)."""
    payment = (await db.execute(
        select(Payment).where(Payment.id == payment_id).execution_options(populate_existing=True)
    )).scalar_one_or_none()
    if payment is None:
        raise NotFound(f"Payment {payment_id} not found")
    return payment


async def payment_detail(db: AsyncSession, payment_id: int) -> dict:
    payment = await load_payment(db, payment_id)
    allocated = (await _allocated_by_payment(db, [payment.id])).get(payment.id, ZERO)
    reversed_ = (await _reversed_by_payment(db, [payment.id])).get(payment.id, ZERO)
    unallocated = payment.amount - reversed_ - allocated if payment.kind == PaymentKind.PAYMENT.value else ZERO
    data = {c: getattr(payment, c) for c in (
        "id", "student_id", "session_year_id", "kind", "receipt_number", "amount", "payment_method_id",
        "payment_date", "transaction_id", "remarks", "reverses_payment_id", "reversal_reason_id",
        "receipt_url", "created_by", "created_at", "allocations", "reversal_allocations")}
    return {**data, "allocated": allocated, "reversed": reversed_, "unallocated": unallocated}


async def list_payments(db: AsyncSession, student_id: int, *, session_year_id: Optional[int] = None) -> List[Payment]:
    await repo.student_or_404(db, student_id)
    query = select(Payment).where(Payment.student_id == student_id).order_by(Payment.payment_date, Payment.id)
    if session_year_id is not None:
        query = query.where(Payment.session_year_id == session_year_id)
    return list((await db.execute(query.execution_options(populate_existing=True))).scalars())


async def student_balance(db: AsyncSession, student_id: int, *, as_of: Optional[date] = None) -> dict:
    await repo.student_or_404(db, student_id)
    as_of = as_of or date.today()
    dues = (await db.execute(
        select(StudentDue).where(StudentDue.student_id == student_id, StudentDue.status != DueStatus.CANCELLED.value)
    )).scalars().all()
    total_due = sum((d.net_amount for d in dues), ZERO)
    total_paid = sum((d.paid_amount for d in dues), ZERO)
    open_dues = [d for d in dues if d.status in OPEN_DUE_STATUSES]
    overdue = sum((d.net_amount - d.paid_amount for d in open_dues if d.due_date < as_of), ZERO)
    return {
        "student_id": student_id, "total_due": total_due, "total_paid": total_paid,
        "balance": total_due - total_paid, "overdue": overdue,
        "credit": await student_credit(db, student_id), "open_dues": len(open_dues),
    }
