"""
Rosters: who rides a route or a vehicle on a given day, stop by stop.

A rider is an assignment riding on the day (started, not ended, not
cancelled). Riders in a paused month are listed with paused = true and do not
count towards the seats.
"""
from datetime import date
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.fees.periods import month_start
from app.modules.transport import repository as repo
from app.modules.transport.models import Route, TransportAssignment, Vehicle
from app.modules.transport.service import setup


def _paused(a: TransportAssignment, on_date: date) -> bool:
    month = month_start(on_date)
    return any(p.from_period <= month <= p.to_period for p in a.active_pauses())


async def _route_roster(db: AsyncSession, route: Route, on_date: date, *,
                        vehicle: Optional[Vehicle], seats: Optional[int]) -> dict:
    riders = await repo.assignments(db, select(TransportAssignment).where(
        TransportAssignment.route_id == route.id, *repo.active_on(on_date),
    ))
    students = await repo.students_by_id(db, {a.student_id for a in riders})
    classes = await repo.class_names(db, {s.class_id for s in students.values()})

    by_stop: Dict[Optional[int], list] = {}
    for a in riders:
        s = students.get(a.student_id)
        by_stop.setdefault(a.route_stop_id, []).append(dict(
            assignment_id=a.id, student_id=a.student_id,
            student_name=repo.full_name(s) if s else "", admission_number=s.admission_number if s else "",
            class_name=classes.get(s.class_id) if s else None, transport_type_id=a.transport_type_id,
            pickup_location=a.pickup_location, drop_location=a.drop_location, paused=_paused(a, on_date),
        ))
    for group in by_stop.values():
        group.sort(key=lambda r: (r["class_name"] or "", r["student_name"]))

    stops = [dict(stop=stop, riders=by_stop.pop(stop.id, [])) for stop in route.stops]
    if None in by_stop:
        stops.append(dict(stop=None, riders=by_stop.pop(None)))
    for stop_id, group in by_stop.items():  # stops removed from the route since
        stops.append(dict(stop=None, riders=group))

    paused = sum(1 for a in riders if _paused(a, on_date))
    riding = len(riders) - paused
    return dict(route_id=route.id, route_name=route.name, vehicle=vehicle, seats=seats, on_date=on_date,
                riding=riding, paused=paused, over_capacity=seats is not None and riding > seats, stops=stops)


async def route_roster(db: AsyncSession, route_id: int, on_date: date) -> dict:
    route = await setup.get_route(db, route_id)
    vehicle = await db.get(Vehicle, route.vehicle_id) if route.vehicle_id else None
    seats = await repo.vehicle_seats(db, vehicle) if vehicle else None
    return await _route_roster(db, route, on_date, vehicle=vehicle, seats=seats)


async def vehicle_roster(db: AsyncSession, vehicle_id: int, on_date: date) -> dict:
    vehicle = await repo.get_or_404(db, Vehicle, vehicle_id, "Vehicle")
    seats = await repo.vehicle_seats(db, vehicle)
    routes: List[dict] = []
    for route in await setup.list_routes(db, include_inactive=True, vehicle_id=vehicle_id):
        roster = await _route_roster(db, route, on_date, vehicle=vehicle, seats=seats)
        if route.is_active or roster["riding"] or roster["paused"]:
            routes.append(roster)
    riding = sum(r["riding"] for r in routes)
    for r in routes:
        r["over_capacity"] = seats is not None and riding > seats
    return dict(vehicle=vehicle, seats=seats, on_date=on_date, riding=riding,
                over_capacity=seats is not None and riding > seats, routes=routes)
