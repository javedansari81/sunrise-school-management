"""
Student fee plans: which fee heads each student pays in a session.

Class lines (source CLASS) come from the session's published fee structure:
for each fee head, the line for the student's class, else the all-classes line.
The plan builder is safe to run again at any time:

* a line that already matches the structure is left alone;
* a line whose price or class changed is ended the month before
  `effective_from` and a new line starts at `effective_from`;
* a line whose fee head is gone from the structure is ended the same way.

Ending a line cancels its unpaid dues from `effective_from` on. Paid or part-paid
dues are never touched; the new line skips those months (one regular due per
student, head and month).

Manual lines (source MANUAL) are one-off or recurring charges added for one
student, e.g. a re-exam fee.

Transport lines (source TRANSPORT, source_ref_id = the transport assignment)
are owned by the transport operations module, which keeps them in step with
its assignments through sync_source_lines(). They cannot be added or ended by
hand here.
"""
from datetime import date, datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.fees import audit, repository as repo
from app.modules.fees.constants import AppliesTo, AuditAction, DueStatus, HEAD_TRANSPORT, Frequency, PlanSource
from app.modules.fees.errors import Conflict, Invalid
from app.modules.fees.models import FeeStructureItem, StudentDue, StudentFeePlan
from app.modules.fees.periods import add_months, month_start, session_months, validate_billing_months
from app.modules.fees.schemas import PlanBuildRequest, PlanLineCreate

ENTITY = "student_fee_plan"
LINE_FIELDS = ("student_id", "session_year_id", "fee_head_id", "amount", "frequency", "billing_months",
               "due_day", "start_period", "end_period", "source", "source_ref_id", "is_active")


def today() -> date:
    return date.today()


def clamp_period(period: date, first: date, last: date) -> date:
    return min(max(month_start(period), first), last)


async def _session_bounds(db: AsyncSession, session_year_id: int) -> Tuple[object, date, date]:
    session_year = await repo.session_year_or_404(db, session_year_id)
    months = session_months(await repo.session_start(db, session_year))
    return session_year, months[0], months[-1]


def _is_new_student(student, first: date, last: date) -> bool:
    return student.admission_date is not None and first <= month_start(student.admission_date) <= last


def _student_first_period(student, first: date, last: date) -> date:
    if _is_new_student(student, first, last):
        return month_start(student.admission_date)
    return first


def _item_applies(item: FeeStructureItem, is_new: bool) -> bool:
    if item.applies_to == AppliesTo.NEW_STUDENTS.value:
        return is_new
    if item.applies_to == AppliesTo.EXISTING_STUDENTS.value:
        return not is_new
    return True


def _matches(line: StudentFeePlan, item: FeeStructureItem) -> bool:
    return (
        line.source_ref_id == item.id
        or (
            line.amount == item.amount
            and line.frequency == item.frequency
            and (line.billing_months or None) == (item.billing_months or None)
            and line.due_day == item.due_day
        )
    )


async def cancel_unpaid_dues(db: AsyncSession, line: StudentFeePlan, from_period: Optional[date], *, user_id: int) -> int:
    """Cancel a line's dues that nothing was paid against, from a period on (all when None)."""
    query = update(StudentDue).where(
        StudentDue.student_fee_plan_id == line.id,
        StudentDue.status.in_((DueStatus.PENDING.value, DueStatus.WAIVED.value)),
        StudentDue.paid_amount == 0,
    )
    if from_period is not None:
        query = query.where(StudentDue.period >= from_period)
    result = await db.execute(
        query.values(status=DueStatus.CANCELLED.value, cancelled_by=user_id,
                     cancel_reason="Fee plan line ended", cancelled_at=datetime.now(timezone.utc))
        .execution_options(synchronize_session="fetch")
    )
    return result.rowcount or 0


async def end_line(db: AsyncSession, line: StudentFeePlan, *, from_period: date, user_id: int, reason: str) -> int:
    """
    Stop billing a line from `from_period`: its last month becomes the month before.
    A line that would bill nothing is cancelled (is_active False). Returns dues cancelled.
    """
    old = audit.snapshot(line, LINE_FIELDS)
    last = add_months(month_start(from_period), -1)
    if last < line.start_period:
        line.is_active = False
        line.end_period = line.start_period
    elif line.end_period is None or line.end_period > last:
        line.end_period = last
    cancelled = await cancel_unpaid_dues(db, line, month_start(from_period), user_id=user_id)
    await db.flush()
    await audit.record(db, entity_type=ENTITY, entity_id=line.id, action=AuditAction.UPDATE.value, performed_by=user_id,
                       old=old, new=audit.snapshot(line, LINE_FIELDS), remarks=f"{reason}; {cancelled} unpaid dues cancelled")
    return cancelled


async def build_class_plans(db: AsyncSession, data: PlanBuildRequest, *, user_id: int) -> dict:
    _, first, last = await _session_bounds(db, data.session_year_id)
    structure = await repo.published_structure(db, data.session_year_id)
    if structure is None:
        raise Invalid("The session has no published fee structure")

    items: Dict[int, Dict[Optional[int], FeeStructureItem]] = {}
    for item in structure.items:
        items.setdefault(item.fee_head_id, {})[item.class_id] = item

    students = await repo.enrolled_students(
        db, data.session_year_id, class_id=data.class_id, student_ids=data.student_ids
    )
    student_ids = [s.id for s, _ in students]
    open_lines: Dict[Tuple[int, int], StudentFeePlan] = {}
    if student_ids:
        rows = (await db.execute(
            select(StudentFeePlan).where(
                StudentFeePlan.session_year_id == data.session_year_id,
                StudentFeePlan.student_id.in_(student_ids),
                StudentFeePlan.source == PlanSource.CLASS.value,
                StudentFeePlan.is_active,
                StudentFeePlan.end_period.is_(None),
            )
        )).scalars().all()
        open_lines = {(r.student_id, r.fee_head_id): r for r in rows}

    default_from = clamp_period(today(), first, last)
    explicit_from = clamp_period(data.effective_from, first, last) if data.effective_from else None
    counts = dict(created=0, unchanged=0, replaced=0, ended=0, dues_cancelled=0)

    for student, class_id in students:
        is_new = _is_new_student(student, first, last)
        student_first = _student_first_period(student, first, last)
        has_lines = any(k[0] == student.id for k in open_lines)
        # First build for a student bills the whole session; later builds change from now on
        effective = explicit_from or (default_from if has_lines else first)

        wanted: Dict[int, FeeStructureItem] = {}
        for head_id, by_class in items.items():
            item = by_class.get(class_id) or by_class.get(None)
            if item is not None and _item_applies(item, is_new) and item.amount > 0:
                wanted[head_id] = item

        for head_id, item in wanted.items():
            line = open_lines.get((student.id, head_id))
            if line is not None and _matches(line, item):
                counts["unchanged"] += 1
                continue
            start = max(student_first, effective)
            if line is not None:
                counts["dues_cancelled"] += await end_line(
                    db, line, from_period=start, user_id=user_id, reason="Replaced by the fee structure"
                )
                counts["replaced"] += 1
            else:
                counts["created"] += 1
            new = StudentFeePlan(
                student_id=student.id, session_year_id=data.session_year_id, fee_head_id=head_id,
                amount=item.amount, frequency=item.frequency, billing_months=item.billing_months,
                due_day=item.due_day, start_period=start, source=PlanSource.CLASS.value,
                source_ref_id=item.id, created_by=user_id,
            )
            db.add(new)
            await db.flush()

        for (sid, head_id), line in open_lines.items():
            if sid == student.id and head_id not in wanted:
                counts["dues_cancelled"] += await end_line(
                    db, line, from_period=max(student_first, effective), user_id=user_id,
                    reason="Fee head no longer in the fee structure for this student",
                )
                counts["ended"] += 1

    await audit.record(db, entity_type="plan_build", entity_id=data.session_year_id, action=AuditAction.GENERATE.value,
                       performed_by=user_id, new={**counts, "fee_structure_id": structure.id,
                                                  "class_id": data.class_id, "student_ids": data.student_ids})
    return dict(session_year_id=data.session_year_id, fee_structure_id=structure.id, students=len(students),
                effective_from=explicit_from, **counts)


async def list_plan(db: AsyncSession, student_id: int, session_year_id: int, *, include_inactive: bool = False) -> List[StudentFeePlan]:
    await repo.student_or_404(db, student_id)
    query = select(StudentFeePlan).where(
        StudentFeePlan.student_id == student_id, StudentFeePlan.session_year_id == session_year_id
    ).order_by(StudentFeePlan.fee_head_id, StudentFeePlan.start_period)
    if not include_inactive:
        query = query.where(StudentFeePlan.is_active)
    return list((await db.execute(query)).scalars())


async def add_manual_line(db: AsyncSession, student_id: int, data: PlanLineCreate, *, user_id: int) -> StudentFeePlan:
    await repo.student_or_404(db, student_id)
    _, first, last = await _session_bounds(db, data.session_year_id)
    head = (await repo.heads_by_id(db, [data.fee_head_id])).get(data.fee_head_id)
    if head is None:
        raise Invalid(f"Fee head {data.fee_head_id} not found")
    if not head.is_active:
        raise Invalid(f"Fee head {head.code} is inactive")
    if head.code == HEAD_TRANSPORT:
        raise Invalid("Transport is billed from transport assignments; assign the student in the transport module")
    error = validate_billing_months(data.frequency.value, data.billing_months)
    if error:
        raise Invalid(error)
    start = clamp_period(data.start_period or today(), first, last)
    end = month_start(data.end_period) if data.end_period else None
    if end is not None and not (start <= end <= last):
        raise Invalid("end_period must be within the session and not before start_period")
    line = StudentFeePlan(
        student_id=student_id, session_year_id=data.session_year_id, fee_head_id=head.id, amount=data.amount,
        frequency=data.frequency.value, billing_months=data.billing_months, due_day=data.due_day,
        start_period=start, end_period=end, source=PlanSource.MANUAL.value, remarks=data.remarks, created_by=user_id,
    )
    db.add(line)
    await db.flush()
    await audit.record(db, entity_type=ENTITY, entity_id=line.id, action=AuditAction.CREATE.value,
                       performed_by=user_id, new=audit.snapshot(line, LINE_FIELDS))
    return line


async def end_plan_line(
    db: AsyncSession, line_id: int, *, last_period: Optional[date], reason: Optional[str], user_id: int
) -> StudentFeePlan:
    """
    End a plan line after `last_period` (its last billed month). Without
    `last_period` the line is cancelled from its start. Unpaid dues after the
    last month are cancelled; paid ones stay.
    """
    line = await repo.get_or_404(db, StudentFeePlan, line_id, "Plan line")
    if not line.is_active:
        raise Conflict(f"Plan line {line_id} is already cancelled")
    if line.source == PlanSource.TRANSPORT.value:
        raise Invalid("Transport lines follow their transport assignment; discontinue or change the assignment instead")
    from_period = add_months(month_start(last_period), 1) if last_period else line.start_period
    await end_line(db, line, from_period=from_period, user_id=user_id, reason=reason or "Ended by hand")
    return line


async def sync_source_lines(
    db: AsyncSession,
    *,
    student_id: int,
    session_year_id: int,
    fee_head_id: int,
    source: PlanSource,
    source_ref_id: int,
    amount,
    due_day: int,
    segments: Sequence[Tuple[date, Optional[date]]],
    user_id: Optional[int],
    reason: str,
) -> dict:
    """
    Make the active monthly lines of one source record (e.g. a transport
    assignment) bill exactly `segments`: (first period, last period or None for
    the session end), in order and not overlapping. Safe to call again.

    * a line whose start, amount and due day match a segment is kept; its end is
      moved to the segment's end (shortening cancels unpaid dues after it);
    * any other line is cancelled (unpaid dues cancelled, paid dues kept);
    * a segment without a line gets a new line.

    Dues are not generated here; the caller runs dues generation afterwards.
    Paid dues are never changed, and a new line skips months that already have
    a regular due for the student and head.
    """
    lines = (await db.execute(
        select(StudentFeePlan).where(
            StudentFeePlan.student_id == student_id,
            StudentFeePlan.session_year_id == session_year_id,
            StudentFeePlan.source == source.value,
            StudentFeePlan.source_ref_id == source_ref_id,
            StudentFeePlan.is_active,
        ).order_by(StudentFeePlan.start_period, StudentFeePlan.id)
    )).scalars().all()
    wanted: Dict[date, Optional[date]] = {start: end for start, end in segments}
    counts = dict(created=0, kept=0, changed=0, cancelled=0, dues_cancelled=0)

    for line in lines:
        if line.start_period not in wanted or line.amount != amount or line.due_day != due_day                 or line.fee_head_id != fee_head_id:
            counts["dues_cancelled"] += await end_line(db, line, from_period=line.start_period,
                                                       user_id=user_id, reason=reason)
            counts["cancelled"] += 1
            continue
        end = wanted.pop(line.start_period)
        if end == line.end_period:
            counts["kept"] += 1
        elif end is not None and (line.end_period is None or end < line.end_period):
            counts["dues_cancelled"] += await end_line(db, line, from_period=add_months(end, 1),
                                                       user_id=user_id, reason=reason)
            counts["changed"] += 1
        else:
            old = audit.snapshot(line, LINE_FIELDS)
            line.end_period = end
            await db.flush()
            await audit.record(db, entity_type=ENTITY, entity_id=line.id, action=AuditAction.UPDATE.value,
                               performed_by=user_id, old=old, new=audit.snapshot(line, LINE_FIELDS), remarks=reason)
            counts["changed"] += 1

    for start, end in sorted(wanted.items()):
        line = StudentFeePlan(
            student_id=student_id, session_year_id=session_year_id, fee_head_id=fee_head_id, amount=amount,
            frequency=Frequency.MONTHLY.value, due_day=due_day, start_period=start, end_period=end,
            source=source.value, source_ref_id=source_ref_id, created_by=user_id,
        )
        db.add(line)
        await db.flush()
        await audit.record(db, entity_type=ENTITY, entity_id=line.id, action=AuditAction.CREATE.value,
                           performed_by=user_id, new=audit.snapshot(line, LINE_FIELDS), remarks=reason)
        counts["created"] += 1
    return counts
