"""
Read-only fee figures for other modules (dashboard, student pages, student list).

Every query is ORM, so app.core.tenant scopes it to the request's school.
Amounts are Decimal; callers convert for JSON.

* Billed: net amount of every due that is not cancelled.
* Paid: paid amount of those dues.
* Pending: open (pending or partial) balance; overdue is the part already past its due date.
* Collected: money received by payment date, net of reversals (reversal rows carry negative amounts).
"""
from datetime import date
from decimal import Decimal
from typing import Dict, Iterable, List, Optional

from sqlalchemy import and_, case, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.fees.constants import DueStatus, OPEN_DUE_STATUSES, PaymentKind
from app.modules.fees.models import FeeHead, Payment, StudentDue

ZERO = Decimal("0.00")


def _due_filters(session_year_id: Optional[int], head_category: Optional[str]) -> list:
    filters = [StudentDue.status != DueStatus.CANCELLED.value]
    if session_year_id is not None:
        filters.append(StudentDue.session_year_id == session_year_id)
    if head_category is not None:
        filters.append(StudentDue.fee_head_id.in_(select(FeeHead.id).where(FeeHead.category == head_category)))
    return filters


async def session_summary(
    db: AsyncSession, session_year_id: int, *, head_category: Optional[str] = None, as_of: Optional[date] = None,
) -> dict:
    """Billed, paid, pending and overdue totals for a session, with student counts."""
    as_of = as_of or date.today()
    open_amount = StudentDue.net_amount - StudentDue.paid_amount
    is_open = StudentDue.status.in_(OPEN_DUE_STATUSES)
    row = (await db.execute(
        select(
            func.coalesce(func.sum(StudentDue.net_amount), 0),
            func.coalesce(func.sum(StudentDue.paid_amount), 0),
            func.coalesce(func.sum(case((is_open, open_amount), else_=0)), 0),
            func.coalesce(func.sum(case((and_(is_open, StudentDue.due_date < as_of), open_amount), else_=0)), 0),
            func.count(distinct(StudentDue.student_id)),
            func.count(distinct(case((is_open, StudentDue.student_id)))),
        ).where(*_due_filters(session_year_id, head_category))
    )).one()
    billed, paid, pending, overdue, students, students_open = (Decimal(row[0]), Decimal(row[1]), Decimal(row[2]),
                                                               Decimal(row[3]), row[4], row[5])
    return {
        "billed": billed, "paid": paid, "pending": pending, "overdue": overdue,
        "students": students, "students_with_dues": students_open, "students_paid": students - students_open,
        "collection_rate": float(paid / billed * 100) if billed > 0 else 0.0,
    }


async def collected(
    db: AsyncSession, *, session_year_id: Optional[int] = None,
    date_from: Optional[date] = None, date_to: Optional[date] = None,
) -> Decimal:
    """Money received between two payment dates (both optional, inclusive), net of reversals."""
    query = select(func.coalesce(func.sum(Payment.amount), 0))
    if session_year_id is not None:
        query = query.where(Payment.session_year_id == session_year_id)
    if date_from is not None:
        query = query.where(Payment.payment_date >= date_from)
    if date_to is not None:
        query = query.where(Payment.payment_date <= date_to)
    return Decimal((await db.execute(query)).scalar_one())


async def monthly_collections(db: AsyncSession, session_year_id: int) -> List[dict]:
    """Collections of a session per calendar month of payment, oldest first, net of reversals."""
    month = func.date_trunc("month", Payment.payment_date)
    rows = (await db.execute(
        select(month, func.sum(Payment.amount),
               func.count(case((Payment.kind == PaymentKind.PAYMENT.value, Payment.id))))
        .where(Payment.session_year_id == session_year_id)
        .group_by(month).order_by(month)
    )).all()
    return [{"month": m.strftime("%b %Y"), "period": m.date(), "amount": Decimal(a), "count": c} for m, a, c in rows]


async def monthly_dues(db: AsyncSession, session_year_id: int, *, head_category: Optional[str] = None) -> List[dict]:
    """Billed and paid per billing period of a session, oldest first."""
    rows = (await db.execute(
        select(StudentDue.period, func.sum(StudentDue.net_amount), func.sum(StudentDue.paid_amount))
        .where(*_due_filters(session_year_id, head_category))
        .group_by(StudentDue.period).order_by(StudentDue.period)
    )).all()
    return [{"month": p.strftime("%B"), "period": p, "total": Decimal(t), "collected": Decimal(c)} for p, t, c in rows]


async def student_balances(
    db: AsyncSession, student_ids: Iterable[int], *, session_year_id: Optional[int] = None,
    as_of: Optional[date] = None,
) -> Dict[int, dict]:
    """
    Per student: billed, paid, pending and overdue amounts, the number of dues and
    of overdue dues, and the last payment date. Students without dues are left out.
    """
    ids = list(student_ids)
    if not ids:
        return {}
    as_of = as_of or date.today()
    open_amount = StudentDue.net_amount - StudentDue.paid_amount
    is_open = StudentDue.status.in_(OPEN_DUE_STATUSES)
    is_overdue = and_(is_open, StudentDue.due_date < as_of)
    rows = (await db.execute(
        select(
            StudentDue.student_id,
            func.sum(StudentDue.net_amount), func.sum(StudentDue.paid_amount),
            func.coalesce(func.sum(case((is_open, open_amount), else_=0)), 0),
            func.coalesce(func.sum(case((is_overdue, open_amount), else_=0)), 0),
            func.count(StudentDue.id),
            func.count(case((is_overdue, StudentDue.id))),
        )
        .where(StudentDue.student_id.in_(ids), *_due_filters(session_year_id, None))
        .group_by(StudentDue.student_id)
    )).all()

    last_paid_query = (
        select(Payment.student_id, func.max(Payment.payment_date))
        .where(Payment.student_id.in_(ids), Payment.kind == PaymentKind.PAYMENT.value)
        .group_by(Payment.student_id)
    )
    if session_year_id is not None:
        last_paid_query = last_paid_query.where(Payment.session_year_id == session_year_id)
    last_paid = dict((await db.execute(last_paid_query)).all())

    return {
        sid: {"billed": Decimal(b), "paid": Decimal(p), "pending": Decimal(o), "overdue": Decimal(od),
              "dues": n, "overdue_dues": n_over, "last_payment_date": last_paid.get(sid)}
        for sid, b, p, o, od, n, n_over in rows
    }
