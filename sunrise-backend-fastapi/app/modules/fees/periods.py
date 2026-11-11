"""
Billing periods. A period is the first day of a month. A session runs for 12
months from its start month (session_years.start_date, else the school's
academic_year_start_month).
"""
from datetime import date
from typing import List, Optional, Sequence

from app.modules.fees.constants import FREQUENCY_STEP, Frequency


def month_start(d: date) -> date:
    return d.replace(day=1)


def add_months(d: date, months: int) -> date:
    index = d.year * 12 + (d.month - 1) + months
    return date(index // 12, index % 12 + 1, 1)


def session_months(start: date) -> List[date]:
    """The 12 periods of a session starting at `start`."""
    first = month_start(start)
    return [add_months(first, i) for i in range(12)]


def default_billing_months(frequency: str, session_start: date) -> List[int]:
    """Calendar months billed for a frequency when no billing_months are given."""
    step = FREQUENCY_STEP[Frequency(frequency)]
    months = session_months(session_start)
    return [m.month for m in months[::step]]


def billed_periods(
    *,
    frequency: str,
    billing_months: Optional[Sequence[int]],
    session_start: date,
    start_period: date,
    end_period: Optional[date],
) -> List[date]:
    """Periods of the session a plan line is billed for, within its start and end."""
    months = set(billing_months) if billing_months else set(default_billing_months(frequency, session_start))
    periods = [p for p in session_months(session_start) if p.month in months]
    if frequency == Frequency.ONE_TIME.value:
        # Billed once: in its billing month if the line covers it, else in the line's first month
        inside = [p for p in periods if p >= start_period and (end_period is None or p <= end_period)]
        return inside[:1] or [start_period]
    return [p for p in periods if p >= start_period and (end_period is None or p <= end_period)]


def due_date_for(period: date, due_day: int) -> date:
    return period.replace(day=due_day)


def validate_billing_months(frequency: str, billing_months: Optional[Sequence[int]]) -> Optional[str]:
    """Error message, or None when the months fit the frequency."""
    if billing_months is None:
        return None
    if not billing_months:
        return "billing_months must not be empty; leave it out to use the default months"
    if any(m < 1 or m > 12 for m in billing_months):
        return "billing_months must be calendar months 1 to 12"
    if len(set(billing_months)) != len(billing_months):
        return "billing_months must not repeat a month"
    if frequency in (Frequency.ANNUAL.value, Frequency.ONE_TIME.value) and len(billing_months) != 1:
        return f"{frequency} lines are billed in exactly one month"
    return None
