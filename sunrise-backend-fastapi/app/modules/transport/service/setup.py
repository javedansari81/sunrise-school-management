"""
Transport setup: vehicle types, vehicles, routes and their stops.

Rows in use are not deleted (the API answers 409); deactivate them instead.
A deactivated type, route or stop keeps its current riders but takes no new
assignments.
"""
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.fees.errors import Conflict, Invalid
from app.modules.transport import repository as repo
from app.modules.transport.models import (
    Route, RouteStop, TransportAssignment, TransportRate, TransportType, Vehicle,
)
from app.modules.transport.schemas import (
    RouteCreate, RouteUpdate, StopCreate, StopOrder, StopUpdate, TransportTypeCreate,
    TransportTypeUpdate, VehicleCreate, VehicleUpdate,
)


def _apply(obj, data) -> None:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)


# ---------------------------------------------------------------------------
# Transport types
# ---------------------------------------------------------------------------

async def _type_name_taken(db: AsyncSession, name: str, exclude_id: Optional[int] = None) -> bool:
    query = select(TransportType.id).where(func.lower(TransportType.name) == name.strip().lower())
    if exclude_id is not None:
        query = query.where(TransportType.id != exclude_id)
    return (await db.execute(query)).first() is not None


async def list_types(db: AsyncSession, *, include_inactive: bool = False) -> List[TransportType]:
    query = select(TransportType).order_by(TransportType.sort_order, TransportType.name)
    if not include_inactive:
        query = query.where(TransportType.is_active)
    return list((await db.execute(query)).scalars())


async def create_type(db: AsyncSession, data: TransportTypeCreate) -> TransportType:
    if await _type_name_taken(db, data.name):
        raise Conflict(f"Transport type '{data.name}' already exists")
    type_ = TransportType(**data.model_dump())
    db.add(type_)
    await db.flush()
    return type_


async def update_type(db: AsyncSession, type_id: int, data: TransportTypeUpdate) -> TransportType:
    type_ = await repo.get_or_404(db, TransportType, type_id, "Transport type")
    if data.name is not None and await _type_name_taken(db, data.name, exclude_id=type_id):
        raise Conflict(f"Transport type '{data.name}' already exists")
    _apply(type_, data)
    await db.flush()
    return type_


async def delete_type(db: AsyncSession, type_id: int) -> None:
    type_ = await repo.get_or_404(db, TransportType, type_id, "Transport type")
    if await repo.in_use(db, Vehicle.transport_type_id == type_id, TransportRate.transport_type_id == type_id,
                         TransportAssignment.transport_type_id == type_id):
        raise Conflict("The transport type is used by vehicles, rates or assignments; deactivate it instead")
    await db.delete(type_)
    await db.flush()


async def active_type_or_error(db: AsyncSession, type_id: int) -> TransportType:
    type_ = await repo.get_or_404(db, TransportType, type_id, "Transport type")
    if not type_.is_active:
        raise Invalid(f"Transport type '{type_.name}' is inactive")
    return type_


# ---------------------------------------------------------------------------
# Vehicles
# ---------------------------------------------------------------------------

async def _registration_taken(db: AsyncSession, number: str, exclude_id: Optional[int] = None) -> bool:
    query = select(Vehicle.id).where(func.upper(Vehicle.registration_number) == number.strip().upper())
    if exclude_id is not None:
        query = query.where(Vehicle.id != exclude_id)
    return (await db.execute(query)).first() is not None


async def list_vehicles(
    db: AsyncSession, *, include_inactive: bool = False, transport_type_id: Optional[int] = None
) -> List[Vehicle]:
    query = select(Vehicle).order_by(Vehicle.registration_number)
    if not include_inactive:
        query = query.where(Vehicle.is_active)
    if transport_type_id is not None:
        query = query.where(Vehicle.transport_type_id == transport_type_id)
    return list((await db.execute(query)).scalars())


async def create_vehicle(db: AsyncSession, data: VehicleCreate) -> Vehicle:
    await repo.get_or_404(db, TransportType, data.transport_type_id, "Transport type")
    if await _registration_taken(db, data.registration_number):
        raise Conflict(f"Vehicle {data.registration_number} already exists")
    vehicle = Vehicle(**data.model_dump())
    vehicle.registration_number = vehicle.registration_number.strip().upper()
    db.add(vehicle)
    await db.flush()
    return vehicle


async def update_vehicle(db: AsyncSession, vehicle_id: int, data: VehicleUpdate) -> Vehicle:
    vehicle = await repo.get_or_404(db, Vehicle, vehicle_id, "Vehicle")
    if data.transport_type_id is not None:
        await repo.get_or_404(db, TransportType, data.transport_type_id, "Transport type")
    if data.registration_number is not None:
        if await _registration_taken(db, data.registration_number, exclude_id=vehicle_id):
            raise Conflict(f"Vehicle {data.registration_number} already exists")
        data.registration_number = data.registration_number.strip().upper()
    _apply(vehicle, data)
    await db.flush()
    return vehicle


async def delete_vehicle(db: AsyncSession, vehicle_id: int) -> None:
    vehicle = await repo.get_or_404(db, Vehicle, vehicle_id, "Vehicle")
    if await repo.in_use(db, Route.vehicle_id == vehicle_id):
        raise Conflict("The vehicle serves a route; take it off the route or deactivate it instead")
    await db.delete(vehicle)
    await db.flush()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

async def _route_name_taken(db: AsyncSession, name: str, exclude_id: Optional[int] = None) -> bool:
    query = select(Route.id).where(func.lower(Route.name) == name.strip().lower())
    if exclude_id is not None:
        query = query.where(Route.id != exclude_id)
    return (await db.execute(query)).first() is not None


async def list_routes(db: AsyncSession, *, include_inactive: bool = False,
                      vehicle_id: Optional[int] = None) -> List[Route]:
    query = select(Route).order_by(Route.name)
    if not include_inactive:
        query = query.where(Route.is_active)
    if vehicle_id is not None:
        query = query.where(Route.vehicle_id == vehicle_id)
    return list((await db.execute(query)).scalars())


async def get_route(db: AsyncSession, route_id: int) -> Route:
    return await repo.get_or_404(db, Route, route_id, "Route")


def _check_stop_list(stops: List[StopCreate]) -> None:
    names = [s.name.strip().lower() for s in stops]
    if len(set(names)) != len(names):
        raise Invalid("Stop names on a route must be different")
    sequences = [s.sequence for s in stops if s.sequence is not None]
    if len(set(sequences)) != len(sequences):
        raise Invalid("Stop sequences on a route must be different")


async def create_route(db: AsyncSession, data: RouteCreate) -> Route:
    if await _route_name_taken(db, data.name):
        raise Conflict(f"Route '{data.name}' already exists")
    if data.vehicle_id is not None:
        await repo.get_or_404(db, Vehicle, data.vehicle_id, "Vehicle")
    _check_stop_list(data.stops)
    route = Route(name=data.name, description=data.description, vehicle_id=data.vehicle_id,
                  is_active=data.is_active, stops=[])
    next_sequence = max([s.sequence for s in data.stops if s.sequence] or [0]) + 1
    for stop in data.stops:
        values = stop.model_dump()
        if values["sequence"] is None:
            values["sequence"] = next_sequence
            next_sequence += 1
        route.stops.append(RouteStop(**values))
    db.add(route)
    await db.flush()
    route.stops.sort(key=lambda s: s.sequence)
    return route


async def update_route(db: AsyncSession, route_id: int, data: RouteUpdate) -> Route:
    route = await get_route(db, route_id)
    if data.name is not None and await _route_name_taken(db, data.name, exclude_id=route_id):
        raise Conflict(f"Route '{data.name}' already exists")
    if data.vehicle_id is not None:
        await repo.get_or_404(db, Vehicle, data.vehicle_id, "Vehicle")
    _apply(route, data)
    await db.flush()
    return route


async def delete_route(db: AsyncSession, route_id: int) -> None:
    route = await get_route(db, route_id)
    if await repo.in_use(db, TransportAssignment.route_id == route_id):
        raise Conflict("The route has assignments; deactivate it instead")
    await db.delete(route)
    await db.flush()


# ---------------------------------------------------------------------------
# Stops
# ---------------------------------------------------------------------------

async def add_stop(db: AsyncSession, route_id: int, data: StopCreate) -> RouteStop:
    route = await get_route(db, route_id)
    if any(s.name.strip().lower() == data.name.strip().lower() for s in route.stops):
        raise Conflict(f"Route '{route.name}' already has a stop '{data.name}'")
    values = data.model_dump()
    if values["sequence"] is None:
        values["sequence"] = max([s.sequence for s in route.stops] or [0]) + 1
    else:
        # Insert: move later stops down one place
        for s in route.stops:
            if s.sequence >= values["sequence"]:
                s.sequence += 1
    stop = RouteStop(**values)
    route.stops.append(stop)
    await db.flush()
    route.stops.sort(key=lambda s: s.sequence)
    return stop


async def update_stop(db: AsyncSession, stop_id: int, data: StopUpdate) -> RouteStop:
    stop = await repo.get_or_404(db, RouteStop, stop_id, "Stop")
    if data.name is not None:
        taken = (await db.execute(select(RouteStop.id).where(
            RouteStop.route_id == stop.route_id, RouteStop.id != stop_id,
            func.lower(RouteStop.name) == data.name.strip().lower(),
        ))).first()
        if taken:
            raise Conflict(f"The route already has a stop '{data.name}'")
    _apply(stop, data)
    await db.flush()
    return stop


async def delete_stop(db: AsyncSession, stop_id: int) -> None:
    stop = await repo.get_or_404(db, RouteStop, stop_id, "Stop")
    if await repo.in_use(db, TransportAssignment.route_stop_id == stop_id):
        raise Conflict("The stop has assignments; deactivate it instead")
    route = await get_route(db, stop.route_id)
    route.stops.remove(stop)
    await db.flush()
    for i, s in enumerate(sorted(route.stops, key=lambda s: s.sequence), start=1):
        s.sequence = i
    await db.flush()


async def reorder_stops(db: AsyncSession, route_id: int, data: StopOrder) -> Route:
    route = await get_route(db, route_id)
    current = {s.id for s in route.stops}
    if len(set(data.stop_ids)) != len(data.stop_ids) or set(data.stop_ids) != current:
        raise Invalid("stop_ids must list every stop of the route exactly once")
    by_id = {s.id: s for s in route.stops}
    for i, stop_id in enumerate(data.stop_ids, start=1):
        by_id[stop_id].sequence = i  # the unique key is checked at commit
    await db.flush()
    route.stops.sort(key=lambda s: s.sequence)
    return route


async def stop_or_error(db: AsyncSession, stop_id: int) -> RouteStop:
    return await repo.get_or_404(db, RouteStop, stop_id, "Stop")
