"""
Queries shared by the transport services. Every query runs on a school-bound
session, so app.core.tenant adds the school filter.
"""
from datetime import date
from typing import Dict, Iterable, List, Optional

from sqlalchemy import exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.metadata import Class
from app.models.student import Student
from app.modules.fees.repository import get_or_404  # noqa: F401  (re-exported)
from app.modules.transport.models import Route, TransportAssignment, TransportType, Vehicle


def active_on(on_date: date):
    """Assignments riding (not cancelled, started, not ended) on a date."""
    return (
        TransportAssignment.is_active,
        TransportAssignment.start_date <= on_date,
        or_(TransportAssignment.end_date.is_(None), TransportAssignment.end_date >= on_date),
    )


async def overlapping(
    db: AsyncSession, *, student_id: int, session_year_id: int, start: date, end: Optional[date],
    exclude_id: Optional[int] = None,
) -> Optional[TransportAssignment]:
    """An active assignment of the student in the session that overlaps [start, end]."""
    query = select(TransportAssignment).where(
        TransportAssignment.student_id == student_id,
        TransportAssignment.session_year_id == session_year_id,
        TransportAssignment.is_active,
        or_(TransportAssignment.end_date.is_(None), TransportAssignment.end_date >= start),
    )
    if end is not None:
        query = query.where(TransportAssignment.start_date <= end)
    if exclude_id is not None:
        query = query.where(TransportAssignment.id != exclude_id)
    return (await db.execute(query.limit(1))).scalar_one_or_none()


async def vehicle_seats(db: AsyncSession, vehicle: Vehicle) -> Optional[int]:
    if vehicle.capacity is not None:
        return vehicle.capacity
    type_ = await db.get(TransportType, vehicle.transport_type_id)
    return type_.capacity if type_ else None


async def riders_on_vehicle(
    db: AsyncSession, vehicle_id: int, on_date: date, *, exclude_id: Optional[int] = None
) -> int:
    query = (
        select(func.count(TransportAssignment.id))
        .join(Route, Route.id == TransportAssignment.route_id)
        .where(Route.vehicle_id == vehicle_id, *active_on(on_date))
    )
    if exclude_id is not None:
        query = query.where(TransportAssignment.id != exclude_id)
    return (await db.execute(query)).scalar_one()


async def in_use(db: AsyncSession, *conditions) -> bool:
    """True when any of the (model column == value) conditions matches a row."""
    for condition in conditions:
        if (await db.execute(select(exists().where(condition)))).scalar():
            return True
    return False


async def students_by_id(db: AsyncSession, ids: Iterable[int]) -> Dict[int, Student]:
    ids = set(ids)
    if not ids:
        return {}
    return {s.id: s for s in (await db.execute(select(Student).where(Student.id.in_(ids)))).scalars()}


async def class_names(db: AsyncSession, ids: Iterable[int]) -> Dict[int, str]:
    ids = set(i for i in ids if i is not None)
    if not ids:
        return {}
    return dict((await db.execute(select(Class.id, Class.name).where(Class.id.in_(ids)))).all())


def full_name(student: Student) -> str:
    return " ".join(p for p in (student.first_name, student.last_name) if p)


async def assignments(db: AsyncSession, query) -> List[TransportAssignment]:
    return list((await db.execute(query)).scalars())
