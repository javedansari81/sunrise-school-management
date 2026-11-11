"""
The handoff to the fee module: which months an assignment is billed for, and
keeping its TRANSPORT plan lines in step.

Whole months only (decision 6), with the school's cut-off day
(fee.transport.cutoff_day, default 15):

* riding starts on or before the cut-off day: that month is billed, else
  billing starts the next month;
* the last day of riding is on or after the cut-off day: that month is billed,
  else billing stops the month before.

Both rules come from one function, so a change on day D bills the old terms up
to the month before the new terms start, with no gap and no double month.

Paused months are cut out, so one assignment can own several plan lines.
"""
from datetime import date, timedelta
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.fees import repository as fee_repo
from app.modules.fees.constants import (
    HEAD_TRANSPORT, PlanSource, SETTING_TRANSPORT_CUTOFF_DAY, SETTING_TRANSPORT_DUE_DAY,
)
from app.modules.fees.errors import Invalid
from app.modules.fees.models import StudentDue, StudentFeePlan
from app.modules.fees.periods import add_months, month_start, session_months
from app.modules.fees.schemas import DuesGenerateRequest
from app.modules.fees.service import dues as due_service
from app.modules.fees.service import plans as plan_service
from app.modules.transport.constants import DEFAULT_CUTOFF_DAY, DEFAULT_DUE_DAY
from app.modules.transport.models import TransportAssignment

Segment = Tuple[date, Optional[date]]


def first_billed_period(start_date: date, cutoff_day: int) -> date:
    """First billed month for riding that starts on `start_date`."""
    month = month_start(start_date)
    return month if start_date.day <= cutoff_day else add_months(month, 1)


def last_billed_period(end_date: date, cutoff_day: int) -> date:
    """Last billed month for riding whose last day is `end_date`."""
    return add_months(first_billed_period(end_date + timedelta(days=1), cutoff_day), -1)


async def _int_setting(db: AsyncSession, key: str, default: int, low: int, high: int) -> int:
    try:
        value = int(await fee_repo.setting(db, key, str(default)))
    except (TypeError, ValueError):
        return default
    return min(max(value, low), high)


async def cutoff_day(db: AsyncSession) -> int:
    return await _int_setting(db, SETTING_TRANSPORT_CUTOFF_DAY, DEFAULT_CUTOFF_DAY, 1, 31)


async def due_day(db: AsyncSession) -> int:
    return await _int_setting(db, SETTING_TRANSPORT_DUE_DAY, DEFAULT_DUE_DAY, 1, 28)


async def session_bounds(db: AsyncSession, session_year_id: int) -> Tuple[date, date]:
    session_year = await fee_repo.session_year_or_404(db, session_year_id)
    months = session_months(await fee_repo.session_start(db, session_year))
    return months[0], months[-1]


def billing_window(
    a: TransportAssignment, *, cutoff: int, first: date, last: date
) -> Optional[Tuple[date, date]]:
    """First and last billed month of an assignment, before pauses. None when it bills nothing."""
    if not a.is_active:
        return None
    start = max(first_billed_period(a.start_date, cutoff), first)
    end = min(last_billed_period(a.end_date, cutoff), last) if a.end_date else last
    return (start, end) if start <= end else None


def segments(a: TransportAssignment, *, cutoff: int, first: date, last: date) -> List[Segment]:
    """
    Billed month ranges of an assignment: its window minus paused months. The
    last range is open-ended (None) when the assignment has no end date and
    runs to the session end, so the plan line stays open like class lines.
    """
    window = billing_window(a, cutoff=cutoff, first=first, last=last)
    if window is None or a.monthly_amount <= 0:
        return []
    ranges: List[List[date]] = [[window[0], window[1]]]
    for pause in a.active_pauses():
        cut: List[List[date]] = []
        for start, end in ranges:
            if pause.to_period < start or pause.from_period > end:
                cut.append([start, end])
                continue
            if pause.from_period > start:
                cut.append([start, add_months(pause.from_period, -1)])
            if pause.to_period < end:
                cut.append([add_months(pause.to_period, 1), end])
        ranges = cut
    result: List[Segment] = [(s, e) for s, e in ranges]
    if result and a.end_date is None and result[-1][1] == last:
        result[-1] = (result[-1][0], None)
    return result


def billed_months(segs: List[Segment], last: date) -> List[date]:
    months: List[date] = []
    for start, end in segs:
        month, stop = start, end or last
        while month <= stop:
            months.append(month)
            month = add_months(month, 1)
    return months


async def transport_head_id(db: AsyncSession) -> int:
    head = await fee_repo.head_by_code(db, HEAD_TRANSPORT)
    if head is None or not head.is_active:
        raise Invalid("The school has no active TRANSPORT fee head")
    return head.id


async def sync(db: AsyncSession, a: TransportAssignment, *, user_id: Optional[int], reason: str) -> dict:
    """Bring the assignment's TRANSPORT plan lines in line with its dates, pauses and amount."""
    first, last = await session_bounds(db, a.session_year_id)
    segs = segments(a, cutoff=await cutoff_day(db), first=first, last=last)
    return await plan_service.sync_source_lines(
        db, student_id=a.student_id, session_year_id=a.session_year_id,
        fee_head_id=await transport_head_id(db), source=PlanSource.TRANSPORT, source_ref_id=a.id,
        amount=a.monthly_amount, due_day=await due_day(db), segments=segs, user_id=user_id, reason=reason,
    )


async def generate_dues(db: AsyncSession, student_id: int, session_year_id: int, *, user_id: Optional[int]):
    """Run the fee module's dues generation for one student (through this month). Skipped when not enrolled."""
    if not await fee_repo.enrolled_students(db, session_year_id, student_ids=[student_id]):
        return None
    return await due_service.generate_dues(
        db, DuesGenerateRequest(session_year_id=session_year_id, student_id=student_id), user_id=user_id
    )


async def paid_months(db: AsyncSession, a: TransportAssignment) -> List[date]:
    """Months with money paid against the assignment's transport dues (any of its lines, ended or not)."""
    rows = (await db.execute(
        select(StudentDue.period)
        .join(StudentFeePlan, StudentFeePlan.id == StudentDue.student_fee_plan_id)
        .where(
            StudentFeePlan.source == PlanSource.TRANSPORT.value,
            StudentFeePlan.source_ref_id == a.id,
            StudentDue.paid_amount != 0,
        )
        .distinct()
    )).scalars().all()
    return sorted(rows)
