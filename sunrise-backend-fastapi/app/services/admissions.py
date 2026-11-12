"""
What the public Admissions page shows: the session a family would be applying
for, its key dates, and what a new student pays per class.

* Admission session: the first session that starts after today. A school rarely
  creates next year's session record months ahead, so when there is none it is
  worked out from the current session (same start month, one year later).
* Key dates are counted back from the session's first month S:
      application forms out    15th of S-5
      last date to apply       last day of S-3
      entrance test            15th to 20th of S-2
      results                  25th of S-2
      admission confirmation   1st to 15th of S-1
      session begins           the session's start date
  For a session starting in April: 15 Nov, 31 Jan, 15-20 Feb, 25 Feb, 1-15 Mar, 1 Apr.
* Fees: the published fee structure of the admission session, else of the most
  recent session that has one, so a family always sees the latest known prices.
  New-student fees are included; fees only for existing students are left out.
"""
import calendar
from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.metadata import Class, SessionYear
from app.models.school import School
from app.modules.fees.constants import AppliesTo, Frequency, StructureStatus
from app.modules.fees.models import FeeHead, FeeStructure
from app.modules.fees.periods import add_months, month_start

# Times a year a fee of each frequency is billed, when it names no months
_TIMES_A_YEAR = {Frequency.MONTHLY.value: 12, Frequency.QUARTERLY.value: 4, Frequency.HALF_YEARLY.value: 2}


def _session_name(start: date) -> str:
    """2027-04-01 -> "2027-28"."""
    return f"{start.year}-{(start.year + 1) % 100:02d}"


def _last_day(month: date) -> date:
    return month.replace(day=calendar.monthrange(month.year, month.month)[1])


def key_dates(start: date) -> List[Dict[str, Any]]:
    """The admission calendar for a session starting on `start` (see the module docstring)."""
    first = month_start(start)

    def m(offset: int, day: int) -> date:
        return add_months(first, offset).replace(day=day)

    return [
        {"key": "forms", "label": "Application forms available", "date": m(-5, 15), "end_date": None},
        {"key": "last_date", "label": "Last date to apply", "date": _last_day(add_months(first, -3)), "end_date": None},
        {"key": "test", "label": "Entrance test / interaction", "date": m(-2, 15), "end_date": m(-2, 20)},
        {"key": "results", "label": "Results announced", "date": m(-2, 25), "end_date": None},
        {"key": "confirmation", "label": "Admission confirmation and fee payment", "date": m(-1, 1), "end_date": m(-1, 15)},
        {"key": "begins", "label": "Academic session begins", "date": start, "end_date": None},
    ]


async def _start_of(db: AsyncSession, year: SessionYear) -> date:
    if year.start_date is not None:
        return year.start_date
    school = await db.get(School, year.school_id)
    return date(int(year.name[:4]), (school.academic_year_start_month if school else None) or 4, 1)


async def admission_session(db: AsyncSession, today: Optional[date] = None) -> Optional[Dict[str, Any]]:
    """The session families apply for now: its name, start, and record id when it exists."""
    today = today or date.today()
    years = (await db.execute(select(SessionYear).where(SessionYear.is_active == True))).scalars().all()  # noqa: E712
    if not years:
        return None
    starts = [(await _start_of(db, y), y) for y in years]
    upcoming = sorted((s, y) for s, y in starts if s > today)
    if upcoming:
        start, year = upcoming[0]
        return {"session_year_id": year.id, "name": year.name, "start_date": start}

    # No record yet: the one after the latest session that has started
    latest_start, _ = max(starts, key=lambda pair: pair[0])
    start = add_months(month_start(latest_start), 12).replace(day=latest_start.day)
    return {"session_year_id": None, "name": _session_name(start), "start_date": start}


async def _structure_for(db: AsyncSession, session_year_id: Optional[int]) -> Optional[FeeStructure]:
    """Published structure of the session, else of the latest session that has one."""
    published = select(FeeStructure).where(FeeStructure.status == StructureStatus.PUBLISHED.value)
    if session_year_id is not None:
        own = (await db.execute(published.where(FeeStructure.session_year_id == session_year_id))).scalars().first()
        if own is not None:
            return own
    rows = (await db.execute(
        published.join(SessionYear, SessionYear.id == FeeStructure.session_year_id)
        .order_by(SessionYear.start_date.desc().nulls_last(), SessionYear.id.desc())
    )).scalars().first()
    return rows


async def fee_table(db: AsyncSession, structure: FeeStructure) -> List[Dict[str, Any]]:
    """Per class: monthly fees, one-time fees and the first-year total for a new student."""
    heads = {h.id: h for h in (await db.execute(select(FeeHead))).scalars()}
    # Per head: the price for a class, else the price for every class (as billing does)
    by_head: Dict[int, Dict[Optional[int], Any]] = {}
    for item in structure.items:
        if item.applies_to != AppliesTo.EXISTING_STUDENTS.value:
            by_head.setdefault(item.fee_head_id, {})[item.class_id] = item

    classes = (await db.execute(
        select(Class).where(Class.is_active == True).order_by(Class.sort_order, Class.id)  # noqa: E712
    )).scalars().all()
    rows = []
    for klass in classes:
        fees, monthly, one_time, first_year = [], Decimal("0"), Decimal("0"), Decimal("0")
        for head_id, prices in by_head.items():
            item, head = prices.get(klass.id) or prices.get(None), heads.get(head_id)
            if item is None or head is None:
                continue
            count = len(item.billing_months) if item.billing_months else _TIMES_A_YEAR.get(item.frequency, 1)
            if item.frequency == Frequency.MONTHLY.value:
                monthly += item.amount
            elif item.frequency == Frequency.ONE_TIME.value:
                one_time += item.amount
            first_year += item.amount * count
            fees.append({"name": head.name, "amount": item.amount, "frequency": item.frequency, "sort": head.sort_order})
        if fees:
            fees.sort(key=lambda f: f.pop("sort"))
            rows.append({"class_id": klass.id, "class_name": klass.description or klass.name, "monthly": monthly,
                         "one_time": one_time, "first_year_total": first_year, "fees": fees})
    return rows


async def admissions_info(db: AsyncSession, today: Optional[date] = None) -> Dict[str, Any]:
    session = await admission_session(db, today)
    if session is None:
        return {"session": None, "dates": [], "fees": {"session_year": None, "classes": []}}
    structure = await _structure_for(db, session["session_year_id"])
    fees_year = await db.get(SessionYear, structure.session_year_id) if structure else None
    return {
        "session": {"name": session["name"], "start_date": session["start_date"]},
        "dates": key_dates(session["start_date"]),
        "fees": {
            # The session the prices belong to; can be earlier than the admission session
            "session_year": fees_year.name if fees_year else None,
            "classes": await fee_table(db, structure) if structure else [],
        },
    }
