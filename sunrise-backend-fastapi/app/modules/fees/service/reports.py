"""
Fee reports.

* Collection: money received between two dates (by payment date), net of
  reversals, by day, by payment method and by fee head. Money not allocated to
  any due (advance credit) is shown on its own line.
* Pending dues by class: open balance and overdue balance per class.
* Student ledger: every due (debit) and payment or reversal (credit/debit) in
  date order with a running balance. A negative balance is credit.
* Consistency: checks the stored paid amounts against the allocations.
"""
from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.metadata import Class, PaymentMethod
from app.modules.fees import repository as repo
from app.modules.fees.constants import DueStatus, OPEN_DUE_STATUSES, PaymentKind
from app.modules.fees.errors import Invalid
from app.modules.fees.models import FeeHead, Payment, PaymentAllocation, StudentDue
from app.modules.fees.service.concessions import money

ZERO = Decimal("0.00")


async def collection(db: AsyncSession, *, date_from: date, date_to: date) -> dict:
    if date_to < date_from:
        raise Invalid("date_to must not be before date_from")
    in_range = and_(Payment.payment_date >= date_from, Payment.payment_date <= date_to)

    payments = (await db.execute(select(Payment).where(in_range))).scalars().all()
    received = sum((p.amount for p in payments if p.kind == PaymentKind.PAYMENT.value), ZERO)
    reversed_ = -sum((p.amount for p in payments if p.kind == PaymentKind.REVERSAL.value), ZERO)

    by_day: Dict[date, Decimal] = defaultdict(lambda: ZERO)
    by_method: Dict[Optional[int], Decimal] = defaultdict(lambda: ZERO)
    for p in payments:
        by_day[p.payment_date] += p.amount
        by_method[p.payment_method_id] += p.amount
    methods = {m.id: m.name for m in (await db.execute(select(PaymentMethod))).scalars()}

    # Head split: allocations of payments received in range, and reversal rows of reversals made in range
    head_rows = (await db.execute(
        select(FeeHead.id, FeeHead.code, FeeHead.name, func.sum(PaymentAllocation.amount))
        .join(StudentDue, StudentDue.fee_head_id == FeeHead.id)
        .join(PaymentAllocation, PaymentAllocation.student_due_id == StudentDue.id)
        .join(Payment, Payment.id == func.coalesce(PaymentAllocation.reversal_payment_id, PaymentAllocation.payment_id))
        .where(in_range)
        .group_by(FeeHead.id, FeeHead.code, FeeHead.name, FeeHead.sort_order)
        .order_by(FeeHead.sort_order)
    )).all()
    by_head = [{"fee_head_id": i, "code": c, "name": n, "amount": money(a)} for i, c, n, a in head_rows]
    allocated = sum((h["amount"] for h in by_head), ZERO)

    net = received - reversed_
    return {
        "date_from": date_from, "date_to": date_to,
        "received": received, "reversed": reversed_, "net": net,
        "payments": sum(1 for p in payments if p.kind == PaymentKind.PAYMENT.value),
        "by_day": [{"date": d, "amount": a} for d, a in sorted(by_day.items())],
        "by_method": [{"payment_method_id": m, "method": methods.get(m), "amount": a}
                      for m, a in sorted(by_method.items(), key=lambda x: x[0] or 0)],
        "by_head": by_head,
        "not_allocated": net - allocated,
    }


async def pending_by_class(db: AsyncSession, *, session_year_id: int, as_of: Optional[date] = None) -> dict:
    await repo.session_year_or_404(db, session_year_id)
    as_of = as_of or date.today()
    enrolled = await repo.enrolled_students(db, session_year_id)
    class_of = {s.id: c for s, c in enrolled}

    dues = (await db.execute(
        select(StudentDue).where(StudentDue.session_year_id == session_year_id,
                                 StudentDue.status.in_(OPEN_DUE_STATUSES))
    )).scalars().all()
    rows: Dict[Optional[int], dict] = {}
    for due in dues:
        class_id = class_of.get(due.student_id)
        row = rows.setdefault(class_id, {"class_id": class_id, "students": set(), "pending": ZERO, "overdue": ZERO})
        open_amount = due.net_amount - due.paid_amount
        row["students"].add(due.student_id)
        row["pending"] += open_amount
        if due.due_date < as_of:
            row["overdue"] += open_amount

    classes = {c.id: c for c in (await db.execute(select(Class))).scalars()}
    out = []
    for class_id, row in rows.items():
        klass = classes.get(class_id)
        out.append({
            "class_id": class_id, "class_name": klass.description if klass else "Not enrolled",
            "students_with_dues": len(row["students"]), "pending": row["pending"], "overdue": row["overdue"],
            "sort": klass.sort_order if klass and klass.sort_order is not None else 10_000,
        })
    out.sort(key=lambda r: (r["sort"], r["class_name"]))
    for r in out:
        r.pop("sort")
    return {
        "session_year_id": session_year_id, "as_of": as_of, "classes": out,
        "total_pending": sum((r["pending"] for r in out), ZERO),
        "total_overdue": sum((r["overdue"] for r in out), ZERO),
    }


async def student_ledger(db: AsyncSession, student_id: int, *, session_year_id: Optional[int] = None) -> dict:
    student = await repo.student_or_404(db, student_id)
    dues_q = select(StudentDue, FeeHead.name).join(FeeHead, FeeHead.id == StudentDue.fee_head_id).where(
        StudentDue.student_id == student_id, StudentDue.status != DueStatus.CANCELLED.value)
    pay_q = select(Payment).where(Payment.student_id == student_id)
    if session_year_id is not None:
        dues_q = dues_q.where(StudentDue.session_year_id == session_year_id)
        pay_q = pay_q.where(Payment.session_year_id == session_year_id)

    entries: List[dict] = []
    for due, head_name in (await db.execute(dues_q)).all():
        entries.append({"date": due.due_date, "order": 0, "type": "DUE", "reference": f"due:{due.id}",
                        "description": due.description or f"{head_name} {due.period:%b %Y}",
                        "debit": due.net_amount, "credit": ZERO, "status": due.status})
    for p in (await db.execute(pay_q)).scalars():
        if p.kind == PaymentKind.PAYMENT.value:
            entries.append({"date": p.payment_date, "order": 1, "type": "PAYMENT", "reference": p.receipt_number,
                            "description": f"Payment {p.receipt_number}", "debit": ZERO, "credit": p.amount,
                            "status": None})
        else:
            entries.append({"date": p.payment_date, "order": 2, "type": "REVERSAL",
                            "reference": f"reversal:{p.id}", "description": f"Reversal of payment {p.reverses_payment_id}",
                            "debit": -p.amount, "credit": ZERO, "status": None})
    entries.sort(key=lambda e: (e["date"], e["order"]))
    running = ZERO
    for e in entries:
        running += e["debit"] - e["credit"]
        e["balance"] = running
        e.pop("order")
    return {
        "student_id": student.id, "student_name": f"{student.first_name} {student.last_name}",
        "admission_number": student.admission_number, "session_year_id": session_year_id,
        "total_debit": sum((e["debit"] for e in entries), ZERO),
        "total_credit": sum((e["credit"] for e in entries), ZERO),
        "balance": running, "entries": entries,
    }


async def consistency(db: AsyncSession) -> dict:
    """Dues whose paid amount differs from their allocations, and payments allocated beyond what they hold."""
    alloc_by_due = dict((await db.execute(
        select(PaymentAllocation.student_due_id, func.sum(PaymentAllocation.amount))
        .group_by(PaymentAllocation.student_due_id)
    )).all())
    due_problems = []
    dues = (await db.execute(select(StudentDue))).scalars().all()
    for due in dues:
        allocated = alloc_by_due.get(due.id) or ZERO
        if allocated != due.paid_amount:
            due_problems.append({"due_id": due.id, "paid_amount": due.paid_amount, "allocated": allocated})
        elif due.status == DueStatus.PAID.value and due.paid_amount != due.net_amount:
            due_problems.append({"due_id": due.id, "status": due.status, "paid_amount": due.paid_amount,
                                 "net_amount": due.net_amount})

    payments = (await db.execute(select(Payment))).scalars().all()
    alloc_by_payment = dict((await db.execute(
        select(PaymentAllocation.payment_id, func.sum(PaymentAllocation.amount)).group_by(PaymentAllocation.payment_id)
    )).all())
    reversed_by = defaultdict(lambda: ZERO)
    for p in payments:
        if p.kind == PaymentKind.REVERSAL.value:
            reversed_by[p.reverses_payment_id] += -p.amount
    payment_problems = []
    for p in payments:
        if p.kind != PaymentKind.PAYMENT.value:
            continue
        held = p.amount - reversed_by[p.id]
        allocated = alloc_by_payment.get(p.id) or ZERO
        if allocated > held or held < 0:
            payment_problems.append({"payment_id": p.id, "receipt_number": p.receipt_number,
                                     "held": held, "allocated": allocated})
    return {"ok": not due_problems and not payment_problems,
            "dues_checked": len(dues), "payments_checked": len(payments),
            "due_problems": due_problems, "payment_problems": payment_problems}
