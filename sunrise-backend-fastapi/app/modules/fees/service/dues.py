"""
Dues: one billable line per student, fee head and month, generated from plans.

Generation is safe to run again: a month that already has a regular due for
the student and head is skipped (unique index). Unpaid dues are re-priced, so
a concession or sibling change reaches them on the next run; dues with any
payment are never changed (decision: paid dues are never edited).

After generating, late fees are applied and the students' credit (advance
payments, decision 10) is allocated to the new dues.
"""
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional, Set, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.fees import audit, repository as repo
from app.modules.fees.constants import (
    AuditAction, DueLineType, DueStatus, HEAD_LATE_FEE, OPEN_DUE_STATUSES,
    SETTING_LATE_FEE_ENABLED, SETTING_LATE_FEE_GRACE_DAYS, SETTING_LATE_FEE_MODE, SETTING_LATE_FEE_VALUE,
)
from app.modules.fees.errors import Conflict, Invalid
from app.modules.fees.models import StudentDue, StudentFeePlan
from app.modules.fees.periods import billed_periods, due_date_for, session_months
from app.modules.fees.schemas import DuesGenerateRequest
from app.modules.fees.service.concessions import ConcessionCalculator, money
from app.modules.fees.service.plans import clamp_period, today

ENTITY = "student_due"
ZERO = Decimal("0.00")


def _status_for(net: Decimal, concession: Decimal) -> str:
    return DueStatus.WAIVED.value if net == 0 and concession > 0 else DueStatus.PENDING.value


async def generate_dues(db: AsyncSession, data: DuesGenerateRequest, *, user_id: int) -> dict:
    session_year = await repo.session_year_or_404(db, data.session_year_id)
    months = session_months(await repo.session_start(db, session_year))
    first, last = months[0], months[-1]
    through = clamp_period(data.through_period or today(), first, last)

    students = await repo.enrolled_students(
        db, data.session_year_id, class_id=data.class_id,
        student_ids=[data.student_id] if data.student_id is not None else None,
    )
    if data.student_id is not None and not students:
        await repo.student_or_404(db, data.student_id)
        raise Invalid(f"Student {data.student_id} is not enrolled in session {data.session_year_id}")
    student_ids = [s.id for s, _ in students]
    result = dict(session_year_id=data.session_year_id, through_period=through, students=len(students),
                  created=0, repriced=0, total_amount=ZERO, late_fees=0, credit_applied=ZERO)
    if not student_ids:
        return result

    lines = (await db.execute(
        select(StudentFeePlan).where(
            StudentFeePlan.session_year_id == data.session_year_id,
            StudentFeePlan.student_id.in_(student_ids),
            StudentFeePlan.is_active,
            StudentFeePlan.amount > 0,
        ).order_by(StudentFeePlan.student_id, StudentFeePlan.id)
    )).scalars().all()
    heads = await repo.heads_by_id(db, {line.fee_head_id for line in lines})

    existing = (await db.execute(
        select(StudentDue).where(
            StudentDue.session_year_id == data.session_year_id,
            StudentDue.student_id.in_(student_ids),
            StudentDue.line_type == DueLineType.REGULAR.value,
            StudentDue.status != DueStatus.CANCELLED.value,
        )
    )).scalars().all()
    taken: Set[Tuple[int, int, date]] = {(d.student_id, d.fee_head_id, d.period) for d in existing}

    calc = ConcessionCalculator(db, data.session_year_id)

    for line in lines:
        head = heads[line.fee_head_id]
        end = min(line.end_period, through) if line.end_period else through
        if end < line.start_period:
            continue
        for period in billed_periods(frequency=line.frequency, billing_months=line.billing_months,
                                     session_start=first, start_period=line.start_period, end_period=end):
            key = (line.student_id, line.fee_head_id, period)
            if key in taken or period > through:
                continue
            gross = money(line.amount)
            concession = await calc.amount(line.student_id, line.fee_head_id, period, gross)
            net = gross - concession
            db.add(StudentDue(
                student_id=line.student_id, session_year_id=data.session_year_id, fee_head_id=line.fee_head_id,
                student_fee_plan_id=line.id, line_type=DueLineType.REGULAR.value, period=period,
                due_date=due_date_for(period, line.due_day), description=f"{head.name} {period:%b %Y}",
                gross_amount=gross, concession_amount=concession, net_amount=net,
                status=_status_for(net, concession), created_by=user_id,
            ))
            taken.add(key)
            result["created"] += 1
            result["total_amount"] += net

    # Re-price unpaid dues (concessions or siblings may have changed)
    for due in existing:
        if due.paid_amount != 0 or due.status not in (DueStatus.PENDING.value, DueStatus.WAIVED.value):
            continue
        concession = await calc.amount(due.student_id, due.fee_head_id, due.period, due.gross_amount)
        if concession != due.concession_amount:
            old = audit.snapshot(due, ("concession_amount", "net_amount", "status"))
            due.concession_amount = concession
            due.net_amount = due.gross_amount - concession
            due.status = _status_for(due.net_amount, concession)
            await db.flush()
            await audit.record(db, entity_type=ENTITY, entity_id=due.id, action=AuditAction.UPDATE.value,
                               performed_by=user_id, old=old,
                               new=audit.snapshot(due, ("concession_amount", "net_amount", "status")),
                               remarks="Re-priced on dues generation")
            result["repriced"] += 1
    await db.flush()

    late = await apply_late_fees(db, as_of=today(), session_year_id=data.session_year_id,
                                 student_ids=student_ids, user_id=user_id)
    result["late_fees"] = late["created"]

    # Advance payments (credit) settle the new dues
    from app.modules.fees.service.payments import apply_credit
    for student_id in student_ids:
        result["credit_applied"] += await apply_credit(db, student_id, user_id=user_id)

    await audit.record(db, entity_type="dues_generation", entity_id=data.session_year_id,
                       action=AuditAction.GENERATE.value, performed_by=user_id,
                       new={k: v for k, v in result.items()} | {"class_id": data.class_id, "student_id": data.student_id})
    return result


async def list_dues(
    db: AsyncSession, student_id: int, *, session_year_id: Optional[int] = None,
    status: Optional[List[str]] = None, open_only: bool = False,
) -> List[StudentDue]:
    await repo.student_or_404(db, student_id)
    query = select(StudentDue).where(StudentDue.student_id == student_id).order_by(
        StudentDue.due_date, StudentDue.fee_head_id, StudentDue.id
    )
    if session_year_id is not None:
        query = query.where(StudentDue.session_year_id == session_year_id)
    if open_only:
        query = query.where(StudentDue.status.in_(OPEN_DUE_STATUSES))
    elif status:
        query = query.where(StudentDue.status.in_(status))
    return list((await db.execute(query)).scalars())


async def cancel_due(db: AsyncSession, due_id: int, *, reason: str, user_id: int) -> StudentDue:
    due = await repo.get_or_404(db, StudentDue, due_id, "Due")
    if due.status == DueStatus.CANCELLED.value:
        raise Conflict(f"Due {due_id} is already cancelled")
    if due.paid_amount != 0:
        raise Conflict(f"Due {due_id} has payments against it; reverse the payment first")
    old = audit.snapshot(due, ("status",))
    due.status = DueStatus.CANCELLED.value
    due.cancelled_at = datetime.now(timezone.utc)
    due.cancelled_by = user_id
    due.cancel_reason = reason
    await db.flush()
    await audit.record(db, entity_type=ENTITY, entity_id=due.id, action=AuditAction.CANCEL.value,
                       performed_by=user_id, old=old, new={"status": due.status}, remarks=reason)
    return due


# ---------------------------------------------------------------------------
# Late fees (decision 7)
# ---------------------------------------------------------------------------

async def apply_late_fees(
    db: AsyncSession,
    *,
    as_of: Optional[date] = None,
    session_year_id: Optional[int] = None,
    student_ids: Optional[List[int]] = None,
    user_id: Optional[int],
) -> dict:
    """
    Add one Late fee due per student and overdue month when the school's late fee
    is enabled. A month is overdue when a regular or manual due of that month is
    still open more than `grace_days` after its due date. FIXED mode charges the
    setting's amount; PERCENT mode a percent of that month's open balance.
    """
    as_of = as_of or today()
    result = dict(enabled=False, as_of=as_of, created=0, total_amount=ZERO)
    if (await repo.setting(db, SETTING_LATE_FEE_ENABLED, "false")).lower() != "true":
        return result
    result["enabled"] = True
    mode = (await repo.setting(db, SETTING_LATE_FEE_MODE, "FIXED")).upper()
    value = Decimal(await repo.setting(db, SETTING_LATE_FEE_VALUE, "0") or "0")
    grace = int(await repo.setting(db, SETTING_LATE_FEE_GRACE_DAYS, "0") or "0")
    late_head = await repo.head_by_code(db, HEAD_LATE_FEE)
    if value <= 0 or late_head is None:
        return result

    query = select(StudentDue).where(
        StudentDue.status.in_(OPEN_DUE_STATUSES),
        StudentDue.line_type.in_((DueLineType.REGULAR.value, DueLineType.MANUAL.value)),
        StudentDue.due_date < as_of,
    )
    if session_year_id is not None:
        query = query.where(StudentDue.session_year_id == session_year_id)
    if student_ids is not None:
        query = query.where(StudentDue.student_id.in_(student_ids))
    overdue: Dict[Tuple[int, int, date], Decimal] = {}
    for due in (await db.execute(query)).scalars():
        if (as_of - due.due_date).days > grace:
            key = (due.student_id, due.session_year_id, due.period)
            overdue[key] = overdue.get(key, ZERO) + due.net_amount - due.paid_amount
    if not overdue:
        return result

    charged = {
        (d.student_id, d.session_year_id, d.period)
        for d in (await db.execute(
            select(StudentDue).where(
                StudentDue.fee_head_id == late_head.id,
                StudentDue.line_type == DueLineType.LATE_FEE.value,
                StudentDue.status != DueStatus.CANCELLED.value,
                StudentDue.student_id.in_({k[0] for k in overdue}),
            )
        )).scalars()
    }
    for (student_id, sy_id, period), balance in sorted(overdue.items()):
        if (student_id, sy_id, period) in charged or balance <= 0:
            continue
        amount = money(value if mode == "FIXED" else balance * value / 100)
        if amount <= 0:
            continue
        db.add(StudentDue(
            student_id=student_id, session_year_id=sy_id, fee_head_id=late_head.id,
            line_type=DueLineType.LATE_FEE.value, period=period, due_date=as_of,
            description=f"{late_head.name} for {period:%b %Y}", gross_amount=amount,
            concession_amount=ZERO, net_amount=amount, status=DueStatus.PENDING.value, created_by=user_id,
        ))
        result["created"] += 1
        result["total_amount"] += amount
    await db.flush()
    if result["created"]:
        await audit.record(db, entity_type="late_fees", entity_id=session_year_id or 0,
                           action=AuditAction.GENERATE.value, performed_by=user_id,
                           new={"as_of": as_of, "created": result["created"], "total_amount": result["total_amount"]})
    return result

