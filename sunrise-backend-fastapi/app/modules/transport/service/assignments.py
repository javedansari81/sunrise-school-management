"""
Transport assignments: who rides what, and the billing that follows.

Every write ends with billing.sync() (TRANSPORT plan lines follow the
assignment) and a dues run for the student, in the same transaction:

    assign        new assignment, plan line(s) from the first billed month
    change        old assignment ends the day before effective_date, a new one
                  starts on it; paid months stay as they are
    discontinue   sets the last riding day; unpaid later dues are cancelled
    cancel        an assignment entered by mistake; refused once money was paid
    pause/resume  paused months are cut out of the plan lines; refused for
                  months already paid
"""
from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.fees import audit
from app.modules.fees import repository as fee_repo
from app.modules.fees.constants import AuditAction
from app.modules.fees.errors import Conflict, Invalid
from app.modules.fees.periods import month_start
from app.modules.transport import billing, repository as repo
from app.modules.transport.constants import ENTITY_ASSIGNMENT, ENTITY_PAUSE
from app.modules.transport.models import Route, TransportAssignment, TransportPause
from app.modules.transport.schemas import (
    AssignmentCancel, AssignmentChange, AssignmentCreate, AssignmentDiscontinue, PauseCreate, Placement,
)
from app.modules.transport.service import rates as rate_service

FIELDS = ("student_id", "session_year_id", "transport_type_id", "route_id", "route_stop_id", "distance_km",
          "start_date", "end_date", "monthly_amount", "transport_rate_id", "amount_overridden",
          "previous_assignment_id", "is_active", "end_reason")


# ---------------------------------------------------------------------------
# Reads
# ---------------------------------------------------------------------------

async def decorate(db: AsyncSession, items: List[TransportAssignment]) -> List[TransportAssignment]:
    """Attach student name, admission number and the billed months for the response."""
    if not items:
        return items
    students = await repo.students_by_id(db, {a.student_id for a in items})
    cutoff = await billing.cutoff_day(db)
    bounds = {}
    for a in items:
        if a.session_year_id not in bounds:
            bounds[a.session_year_id] = await billing.session_bounds(db, a.session_year_id)
        first, last = bounds[a.session_year_id]
        segs = billing.segments(a, cutoff=cutoff, first=first, last=last)
        months = billing.billed_months(segs, last)
        a.billing = dict(billed_from=months[0] if months else None, billed_to=months[-1] if months else None,
                         billed_months=months)
        student = students.get(a.student_id)
        a.student_name = repo.full_name(student) if student else None
        a.admission_number = student.admission_number if student else None
    return items


async def get(db: AsyncSession, assignment_id: int) -> TransportAssignment:
    a = await repo.get_or_404(db, TransportAssignment, assignment_id, "Assignment")
    return (await decorate(db, [a]))[0]


async def list_assignments(
    db: AsyncSession, *, session_year_id: Optional[int] = None, student_id: Optional[int] = None,
    route_id: Optional[int] = None, route_stop_id: Optional[int] = None, transport_type_id: Optional[int] = None,
    vehicle_id: Optional[int] = None, active_on: Optional[date] = None, include_cancelled: bool = False,
) -> List[TransportAssignment]:
    query = select(TransportAssignment).order_by(TransportAssignment.student_id, TransportAssignment.start_date)
    if session_year_id is not None:
        query = query.where(TransportAssignment.session_year_id == session_year_id)
    if student_id is not None:
        query = query.where(TransportAssignment.student_id == student_id)
    if route_id is not None:
        query = query.where(TransportAssignment.route_id == route_id)
    if route_stop_id is not None:
        query = query.where(TransportAssignment.route_stop_id == route_stop_id)
    if transport_type_id is not None:
        query = query.where(TransportAssignment.transport_type_id == transport_type_id)
    if vehicle_id is not None:
        query = query.join(Route, Route.id == TransportAssignment.route_id).where(Route.vehicle_id == vehicle_id)
    if active_on is not None:
        query = query.where(*repo.active_on(active_on))
    elif not include_cancelled:
        query = query.where(TransportAssignment.is_active)
    return await decorate(db, await repo.assignments(db, query))


# ---------------------------------------------------------------------------
# Shared checks
# ---------------------------------------------------------------------------

async def _check_in_session(db: AsyncSession, session_year_id: int, day: date, what: str) -> None:
    first, last = await billing.session_bounds(db, session_year_id)
    if not first <= month_start(day) <= last:
        raise Invalid(f"{what} {day} is outside the session ({first:%b %Y} to {last:%b %Y})")


async def _check_enrolled(db: AsyncSession, student_id: int, session_year_id: int) -> None:
    await fee_repo.student_or_404(db, student_id)
    if not await fee_repo.enrolled_students(db, session_year_id, student_ids=[student_id]):
        raise Invalid(f"Student {student_id} is not enrolled in session {session_year_id}")


async def _check_no_overlap(db: AsyncSession, *, student_id: int, session_year_id: int, start: date,
                            end: Optional[date], exclude_id: Optional[int] = None) -> None:
    other = await repo.overlapping(db, student_id=student_id, session_year_id=session_year_id,
                                   start=start, end=end, exclude_id=exclude_id)
    if other is not None:
        raise Conflict(
            f"Student {student_id} already has transport assignment {other.id} from {other.start_date}"
            f"{f' to {other.end_date}' if other.end_date else ''}; change or discontinue it instead"
        )


async def _check_capacity(db: AsyncSession, placement: rate_service.ResolvedPlacement, on_date: date, *,
                          allow: bool, exclude_id: Optional[int] = None) -> List[str]:
    """Refuse a full vehicle unless allowed; then the overload comes back as a warning."""
    if placement.vehicle is None:
        return []
    seats = await repo.vehicle_seats(db, placement.vehicle)
    if seats is None:
        return []
    riding = await repo.riders_on_vehicle(db, placement.vehicle.id, on_date, exclude_id=exclude_id)
    if riding < seats:
        return []
    message = f"Vehicle {placement.vehicle.registration_number} has {riding} riders for {seats} seats on {on_date}"
    if not allow:
        raise Conflict(message + "; send allow_over_capacity to assign anyway")
    return [message]


async def _price(db: AsyncSession, session_year_id: int, placement, amount) -> tuple:
    """(monthly_amount, rate_id, overridden). An amount given by hand wins over the rate."""
    if amount is not None:
        return amount, None, True
    rate = await rate_service.find_rate(db, session_year_id, placement)
    if rate is None:
        raise Invalid("No transport rate matches; add a rate for the session or give monthly_amount")
    return rate.monthly_amount, rate.id, False


async def _bill(db: AsyncSession, assignments: List[TransportAssignment], *, user_id: int, reason: str) -> dict:
    """Sync plan lines of the assignments (in order), then run dues for the student once."""
    totals: dict = {}
    for a in assignments:
        for key, value in (await billing.sync(db, a, user_id=user_id, reason=reason)).items():
            totals[key] = totals.get(key, 0) + value
    first = assignments[0]
    dues = await billing.generate_dues(db, first.student_id, first.session_year_id, user_id=user_id)
    return {"plan_lines": totals, "dues": dues}


async def _audit(db: AsyncSession, a: TransportAssignment, action: AuditAction, *, user_id: int,
                 old: Optional[dict] = None, remarks: Optional[str] = None) -> None:
    await audit.record(db, entity_type=ENTITY_ASSIGNMENT, entity_id=a.id, action=action.value,
                       performed_by=user_id, old=old, new=audit.snapshot(a, FIELDS), remarks=remarks)


async def _result(db: AsyncSession, a: TransportAssignment, billed: dict, *,
                  previous: Optional[TransportAssignment] = None, warnings: Optional[List[str]] = None) -> dict:
    await decorate(db, [x for x in (a, previous) if x is not None])
    return dict(assignment=a, previous=previous, plan_lines=billed["plan_lines"], dues=billed["dues"],
                warnings=warnings or [])


# ---------------------------------------------------------------------------
# Writes
# ---------------------------------------------------------------------------

async def assign(db: AsyncSession, data: AssignmentCreate, *, user_id: int) -> dict:
    await fee_repo.session_year_or_404(db, data.session_year_id)
    await _check_enrolled(db, data.student_id, data.session_year_id)
    await _check_in_session(db, data.session_year_id, data.start_date, "start_date")
    await _check_no_overlap(db, student_id=data.student_id, session_year_id=data.session_year_id,
                            start=data.start_date, end=None)
    placement = await rate_service.resolve_placement(db, data)
    warnings = await _check_capacity(db, placement, data.start_date, allow=data.allow_over_capacity)
    amount, rate_id, overridden = await _price(db, data.session_year_id, placement, data.monthly_amount)

    a = TransportAssignment(
        student_id=data.student_id, session_year_id=data.session_year_id,
        transport_type_id=placement.transport_type_id, route_id=placement.route_id,
        route_stop_id=placement.route_stop_id, distance_km=placement.distance_km,
        pickup_location=data.pickup_location, drop_location=data.drop_location, start_date=data.start_date,
        monthly_amount=amount, transport_rate_id=rate_id, amount_overridden=overridden,
        remarks=data.remarks, created_by=user_id, pauses=[],
    )
    db.add(a)
    await db.flush()
    await _audit(db, a, AuditAction.CREATE, user_id=user_id)
    billed = await _bill(db, [a], user_id=user_id, reason=f"Transport assignment {a.id}")
    return await _result(db, a, billed, warnings=warnings)


async def change(db: AsyncSession, assignment_id: int, data: AssignmentChange, *, user_id: int) -> dict:
    old = await repo.get_or_404(db, TransportAssignment, assignment_id, "Assignment")
    if not old.is_active:
        raise Conflict(f"Assignment {assignment_id} is cancelled")
    eff = data.effective_date
    if eff <= old.start_date:
        raise Invalid("effective_date must be after the assignment's start date; cancel and assign again instead")
    if old.end_date is not None and eff > old.end_date:
        raise Invalid(f"The assignment ended on {old.end_date}; assign the student again instead")
    await _check_in_session(db, old.session_year_id, eff, "effective_date")

    given = data.model_fields_set
    route_id = data.route_id if "route_id" in given else old.route_id
    if "route_stop_id" in given:
        stop_id = data.route_stop_id
    elif "route_id" in given and data.route_id != old.route_id:
        stop_id = None  # the old stop is on the old route
    else:
        stop_id = old.route_stop_id
    if "route_stop_id" in given and "route_id" not in given and data.route_stop_id is not None:
        route_id = None  # taken from the new stop
    type_id = data.transport_type_id if "transport_type_id" in given else (
        None if "route_id" in given or "route_stop_id" in given else old.transport_type_id
    )
    if "distance_km" in given:
        distance = data.distance_km
    elif "route_stop_id" in given or "route_id" in given:
        distance = None  # taken from the new stop
    else:
        distance = old.distance_km
    placement = await rate_service.resolve_placement(db, Placement(
        transport_type_id=type_id, route_id=route_id, route_stop_id=stop_id, distance_km=distance,
    ), default_type_id=old.transport_type_id)
    warnings = []
    vehicle_changed = placement.vehicle is not None and (
        old.route_id is None or (await db.get(Route, old.route_id)).vehicle_id != placement.vehicle.id
    )
    if vehicle_changed:
        warnings = await _check_capacity(db, placement, eff, allow=data.allow_over_capacity, exclude_id=old.id)
    amount, rate_id, overridden = await _price(db, old.session_year_id, placement, data.monthly_amount)

    # End the old assignment the day before, then start the new one
    snapshot = audit.snapshot(old, FIELDS)
    original_end = old.end_date
    old.end_date = eff - timedelta(days=1)
    old.end_reason = data.reason or "Changed"
    old.ended_by = user_id
    await db.flush()
    await _audit(db, old, AuditAction.UPDATE, user_id=user_id, old=snapshot, remarks=old.end_reason)

    new = TransportAssignment(
        student_id=old.student_id, session_year_id=old.session_year_id,
        transport_type_id=placement.transport_type_id, route_id=placement.route_id,
        route_stop_id=placement.route_stop_id, distance_km=placement.distance_km,
        pickup_location=data.pickup_location if "pickup_location" in given else old.pickup_location,
        drop_location=data.drop_location if "drop_location" in given else old.drop_location,
        start_date=eff, end_date=original_end, monthly_amount=amount, transport_rate_id=rate_id,
        amount_overridden=overridden, previous_assignment_id=old.id,
        remarks=data.remarks if "remarks" in given else old.remarks, created_by=user_id, pauses=[],
    )
    db.add(new)
    await db.flush()
    # Pauses still ahead move to the new assignment
    first_new = billing.first_billed_period(eff, await billing.cutoff_day(db))
    for pause in old.active_pauses():
        if pause.to_period >= first_new:
            new.pauses.append(TransportPause(
                from_period=max(pause.from_period, first_new), to_period=pause.to_period,
                reason=pause.reason, created_by=user_id,
            ))
    await db.flush()
    await _audit(db, new, AuditAction.CREATE, user_id=user_id, remarks=f"Replaces assignment {old.id}")
    billed = await _bill(db, [old, new], user_id=user_id, reason=f"Transport assignment {old.id} changed")
    return await _result(db, new, billed, previous=old, warnings=warnings)


async def discontinue(db: AsyncSession, assignment_id: int, data: AssignmentDiscontinue, *, user_id: int) -> dict:
    a = await repo.get_or_404(db, TransportAssignment, assignment_id, "Assignment")
    if not a.is_active:
        raise Conflict(f"Assignment {assignment_id} is cancelled")
    if data.end_date < a.start_date:
        raise Invalid("end_date must not be before the start date; cancel the assignment instead")
    await _check_no_overlap(db, student_id=a.student_id, session_year_id=a.session_year_id,
                            start=a.start_date, end=data.end_date, exclude_id=a.id)
    snapshot = audit.snapshot(a, FIELDS)
    a.end_date = data.end_date
    a.end_reason = data.reason or "Discontinued"
    a.ended_by = user_id
    await db.flush()
    await _audit(db, a, AuditAction.UPDATE, user_id=user_id, old=snapshot, remarks=a.end_reason)
    billed = await _bill(db, [a], user_id=user_id, reason=f"Transport assignment {a.id} discontinued")

    warnings = []
    first, last = await billing.session_bounds(db, a.session_year_id)
    window = billing.billing_window(a, cutoff=await billing.cutoff_day(db), first=first, last=last)
    after = [m for m in await billing.paid_months(db, a) if window is None or m > window[1]]
    if after:
        warnings.append("Months already paid after the end stay paid: "
                        + ", ".join(f"{m:%b %Y}" for m in after) + ". Reverse the payment to refund them.")
    return await _result(db, a, billed, warnings=warnings)


async def cancel(db: AsyncSession, assignment_id: int, data: AssignmentCancel, *, user_id: int) -> dict:
    a = await repo.get_or_404(db, TransportAssignment, assignment_id, "Assignment")
    if not a.is_active:
        raise Conflict(f"Assignment {assignment_id} is already cancelled")
    paid = await billing.paid_months(db, a)
    if paid:
        raise Conflict("Money was paid against this assignment (" + ", ".join(f"{m:%b %Y}" for m in paid)
                       + "); reverse the payment first or discontinue instead")
    snapshot = audit.snapshot(a, FIELDS)
    a.is_active = False
    a.end_reason = data.reason
    a.ended_by = user_id
    await db.flush()
    await _audit(db, a, AuditAction.CANCEL, user_id=user_id, old=snapshot, remarks=data.reason)
    billed = await _bill(db, [a], user_id=user_id, reason=f"Transport assignment {a.id} cancelled")
    return await _result(db, a, billed)


async def pause(db: AsyncSession, assignment_id: int, data: PauseCreate, *, user_id: int) -> dict:
    a = await repo.get_or_404(db, TransportAssignment, assignment_id, "Assignment")
    if not a.is_active:
        raise Conflict(f"Assignment {assignment_id} is cancelled")
    start, end = month_start(data.from_period), month_start(data.to_period)
    first, last = await billing.session_bounds(db, a.session_year_id)
    window = billing.billing_window(a, cutoff=await billing.cutoff_day(db), first=first, last=last)
    if window is None or start < window[0] or end > window[1]:
        raise Invalid("Paused months must be within the months the assignment is billed for"
                      + (f" ({window[0]:%b %Y} to {window[1]:%b %Y})" if window else ""))
    for p in a.active_pauses():
        if start <= p.to_period and p.from_period <= end:
            raise Conflict(f"Overlaps pause {p.id} ({p.from_period:%b %Y} to {p.to_period:%b %Y})")
    paid = [m for m in await billing.paid_months(db, a) if start <= m <= end]
    if paid:
        raise Conflict("Months already paid cannot be paused: " + ", ".join(f"{m:%b %Y}" for m in paid)
                       + "; reverse the payment first")
    p = TransportPause(from_period=start, to_period=end, reason=data.reason, created_by=user_id)
    a.pauses.append(p)
    await db.flush()
    await audit.record(db, entity_type=ENTITY_PAUSE, entity_id=p.id, action=AuditAction.CREATE.value,
                       performed_by=user_id, new={"assignment_id": a.id, "from_period": start, "to_period": end},
                       remarks=data.reason)
    billed = await _bill(db, [a], user_id=user_id, reason=f"Transport assignment {a.id} paused")
    return await _result(db, a, billed)


async def resume(db: AsyncSession, pause_id: int, *, user_id: int) -> dict:
    """Remove a pause: its months are billed again."""
    p = await repo.get_or_404(db, TransportPause, pause_id, "Pause")
    if not p.is_active:
        raise Conflict(f"Pause {pause_id} was already removed")
    a = await repo.get_or_404(db, TransportAssignment, p.assignment_id, "Assignment")
    p.is_active = False
    await db.flush()
    await audit.record(db, entity_type=ENTITY_PAUSE, entity_id=p.id, action=AuditAction.DELETE.value,
                       performed_by=user_id, old={"assignment_id": a.id, "from_period": p.from_period,
                                                  "to_period": p.to_period})
    billed = await _bill(db, [a], user_id=user_id, reason=f"Transport assignment {a.id} pause removed")
    return await _result(db, a, billed)
