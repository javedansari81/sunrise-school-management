"""
Read-only transport figures for other modules (dashboard, student pages).

Assignments that were cancelled (is_active false) never count. An assignment
"rides" on a day when it has started and not ended by then.
"""
from datetime import date
from typing import Dict, Iterable, List, Optional

from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.metadata import SessionYear
from app.modules.transport import repository as repo
from app.modules.transport.models import Route, RouteStop, TransportAssignment, TransportType


async def _reference_day(db: AsyncSession, session_year_id: int) -> date:
    """Today, or the last day of the session if it has already ended (so past sessions still show riders)."""
    today = date.today()
    session = await db.get(SessionYear, session_year_id)
    if session is not None and session.end_date is not None and session.end_date < today:
        return session.end_date
    return today


async def session_summary(db: AsyncSession, session_year_id: int, *, on_date: Optional[date] = None) -> dict:
    """Assignment and rider counts for a session, with riders per transport type."""
    on_date = on_date or await _reference_day(db, session_year_id)
    in_session = (TransportAssignment.session_year_id == session_year_id, TransportAssignment.is_active)
    total, students = (await db.execute(
        select(func.count(TransportAssignment.id), func.count(distinct(TransportAssignment.student_id)))
        .where(*in_session)
    )).one()
    riding = (await db.execute(
        select(TransportType.id, TransportType.name, TransportType.description,
               func.count(distinct(TransportAssignment.student_id)))
        .join(TransportAssignment, TransportAssignment.transport_type_id == TransportType.id)
        .where(TransportAssignment.session_year_id == session_year_id, *repo.active_on(on_date))
        .group_by(TransportType.id, TransportType.name, TransportType.description, TransportType.sort_order)
        .order_by(TransportType.sort_order)
    )).all()
    return {
        "on_date": on_date,
        "total_assignments": total,
        "students_assigned": students,
        "students_riding": sum(r[3] for r in riding),
        "by_type": [{"transport_type_id": i, "name": n, "description": d or n, "riders": c} for i, n, d, c in riding],
    }


async def current_assignments(
    db: AsyncSession, student_ids: Iterable[int], *, session_year_id: Optional[int] = None,
    on_date: Optional[date] = None,
) -> Dict[int, dict]:
    """Per student, the assignment riding on a day (default today), with its type, route and stop names."""
    ids = list(student_ids)
    if not ids:
        return {}
    on_date = on_date or date.today()
    query = (
        select(TransportAssignment, TransportType.name, Route.name, RouteStop.name)
        .join(TransportType, TransportType.id == TransportAssignment.transport_type_id)
        .outerjoin(Route, Route.id == TransportAssignment.route_id)
        .outerjoin(RouteStop, RouteStop.id == TransportAssignment.route_stop_id)
        .where(TransportAssignment.student_id.in_(ids), *repo.active_on(on_date))
        .order_by(TransportAssignment.start_date)
    )
    if session_year_id is not None:
        query = query.where(TransportAssignment.session_year_id == session_year_id)
    out: Dict[int, dict] = {}
    for a, type_name, route_name, stop_name in (await db.execute(query)).all():
        out[a.student_id] = {
            "assignment_id": a.id, "session_year_id": a.session_year_id,
            "transport_type_id": a.transport_type_id, "transport_type": type_name,
            "route_id": a.route_id, "route": route_name, "route_stop_id": a.route_stop_id, "stop": stop_name,
            "distance_km": a.distance_km, "pickup_location": a.pickup_location, "drop_location": a.drop_location,
            "start_date": a.start_date, "end_date": a.end_date, "monthly_amount": a.monthly_amount,
        }
    return out


async def list_types(db: AsyncSession) -> List[TransportType]:
    """Active transport types of the school, in display order (for dropdowns)."""
    return list((await db.execute(
        select(TransportType).where(TransportType.is_active).order_by(TransportType.sort_order, TransportType.name)
    )).scalars())
