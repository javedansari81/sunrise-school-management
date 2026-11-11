"""
Transport rates and the lookup that prices an assignment.

An assignment takes the first rate that matches (constants.RATE_ORDER):

1. PER_STOP for its stop (a rate for its vehicle type before one for any type);
2. DISTANCE_SLAB covering its distance (type-specific before any type). A slab
   covers (from, to]; a slab from 0 also covers 0;
3. FLAT for its vehicle type.

The amount found is copied onto the assignment, so editing a rate later never
changes what is already billed; a change of the assignment picks up new rates.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.fees import repository as fee_repo
from app.modules.fees.errors import Conflict, Invalid
from app.modules.transport import repository as repo
from app.modules.transport.constants import RateBasis
from app.modules.transport.models import Route, RouteStop, TransportRate, TransportType, Vehicle
from app.modules.transport.schemas import Placement, RateCopy, RateCreate, RateQuote, RateUpdate
from app.modules.transport.service import setup


# ---------------------------------------------------------------------------
# Placement: route, stop, type and distance, checked against each other
# ---------------------------------------------------------------------------

@dataclass
class ResolvedPlacement:
    transport_type_id: int
    route: Optional[Route]
    stop: Optional[RouteStop]
    vehicle: Optional[Vehicle]
    distance_km: Optional[Decimal]

    @property
    def route_id(self):
        return self.route.id if self.route else None

    @property
    def route_stop_id(self):
        return self.stop.id if self.stop else None


async def resolve_placement(
    db: AsyncSession, p: Placement, *, for_new_rider: bool = True, default_type_id: Optional[int] = None
) -> ResolvedPlacement:
    """
    Fill in and check where a student rides: the stop's route, the route
    vehicle's type (else `default_type_id`), the stop's distance. Inactive routes, stops and types take
    no new riders.
    """
    stop = await setup.stop_or_error(db, p.route_stop_id) if p.route_stop_id is not None else None
    route = None
    if p.route_id is not None:
        route = await setup.get_route(db, p.route_id)
        if stop is not None and stop.route_id != route.id:
            raise Invalid(f"Stop {stop.id} is not on route '{route.name}'")
    elif stop is not None:
        route = await setup.get_route(db, stop.route_id)
    if for_new_rider:
        if route is not None and not route.is_active:
            raise Invalid(f"Route '{route.name}' is inactive")
        if stop is not None and not stop.is_active:
            raise Invalid(f"Stop '{stop.name}' is inactive")

    vehicle = await db.get(Vehicle, route.vehicle_id) if route is not None and route.vehicle_id else None
    type_id = p.transport_type_id
    if type_id is None and vehicle is None:
        type_id = default_type_id
    if type_id is None:
        if vehicle is None:
            raise Invalid("transport_type_id is needed when no route vehicle sets it")
        type_id = vehicle.transport_type_id
    elif vehicle is not None and vehicle.transport_type_id != type_id:
        raise Invalid(f"Route '{route.name}' is served by vehicle {vehicle.registration_number} of another type")
    if for_new_rider:
        await setup.active_type_or_error(db, type_id)
    else:
        await repo.get_or_404(db, TransportType, type_id, "Transport type")

    distance = p.distance_km
    if distance is None and stop is not None:
        distance = stop.distance_km
    return ResolvedPlacement(transport_type_id=type_id, route=route, stop=stop, vehicle=vehicle, distance_km=distance)


# ---------------------------------------------------------------------------
# Lookup
# ---------------------------------------------------------------------------

def slab_covers(rate: TransportRate, distance: Decimal) -> bool:
    above_from = distance > rate.distance_from_km or (rate.distance_from_km == 0 and distance >= 0)
    return above_from and distance <= rate.distance_to_km


def pick_rate(
    rates: List[TransportRate], *, transport_type_id: int, route_stop_id: Optional[int], distance_km: Optional[Decimal]
) -> Optional[TransportRate]:
    """The first matching rate (see module docstring). `rates` are one session's active rates."""
    def typed_first(candidates):
        typed = [r for r in candidates if r.transport_type_id == transport_type_id]
        untyped = [r for r in candidates if r.transport_type_id is None]
        return (typed or untyped or [None])[0]

    if route_stop_id is not None:
        hit = typed_first([r for r in rates if r.basis == RateBasis.PER_STOP.value and r.route_stop_id == route_stop_id])
        if hit:
            return hit
    if distance_km is not None:
        slabs = sorted((r for r in rates if r.basis == RateBasis.DISTANCE_SLAB.value and slab_covers(r, distance_km)),
                       key=lambda r: r.distance_from_km)
        hit = typed_first(slabs)
        if hit:
            return hit
    return typed_first([r for r in rates if r.basis == RateBasis.FLAT.value and r.transport_type_id == transport_type_id])


async def session_rates(db: AsyncSession, session_year_id: int) -> List[TransportRate]:
    return list((await db.execute(
        select(TransportRate).where(TransportRate.session_year_id == session_year_id, TransportRate.is_active)
        .order_by(TransportRate.id)
    )).scalars())


async def find_rate(db: AsyncSession, session_year_id: int, placement: ResolvedPlacement) -> Optional[TransportRate]:
    return pick_rate(await session_rates(db, session_year_id), transport_type_id=placement.transport_type_id,
                     route_stop_id=placement.route_stop_id, distance_km=placement.distance_km)


async def quote(db: AsyncSession, data: RateQuote) -> dict:
    await fee_repo.session_year_or_404(db, data.session_year_id)
    placement = await resolve_placement(db, data)
    rate = await find_rate(db, data.session_year_id, placement)
    return dict(
        transport_type_id=placement.transport_type_id, route_id=placement.route_id,
        route_stop_id=placement.route_stop_id, distance_km=placement.distance_km,
        transport_rate_id=rate.id if rate else None, basis=rate.basis if rate else None,
        monthly_amount=rate.monthly_amount if rate else None,
    )


# ---------------------------------------------------------------------------
# Rate list
# ---------------------------------------------------------------------------

async def list_rates(
    db: AsyncSession, *, session_year_id: Optional[int] = None, basis: Optional[str] = None,
    transport_type_id: Optional[int] = None, route_stop_id: Optional[int] = None, include_inactive: bool = False,
) -> List[TransportRate]:
    query = select(TransportRate).order_by(
        TransportRate.session_year_id, TransportRate.basis, TransportRate.transport_type_id,
        TransportRate.distance_from_km, TransportRate.id,
    )
    if session_year_id is not None:
        query = query.where(TransportRate.session_year_id == session_year_id)
    if basis is not None:
        query = query.where(TransportRate.basis == basis)
    if transport_type_id is not None:
        query = query.where(TransportRate.transport_type_id == transport_type_id)
    if route_stop_id is not None:
        query = query.where(TransportRate.route_stop_id == route_stop_id)
    if not include_inactive:
        query = query.where(TransportRate.is_active)
    return list((await db.execute(query)).scalars())


async def _check_clash(db: AsyncSession, rate: TransportRate) -> None:
    """Refuse a second active FLAT or PER_STOP rate for the same thing, or overlapping slabs."""
    if not rate.is_active:
        return
    query = select(TransportRate).where(
        TransportRate.session_year_id == rate.session_year_id,
        TransportRate.basis == rate.basis,
        TransportRate.is_active,
    )
    if rate.transport_type_id is None:
        query = query.where(TransportRate.transport_type_id.is_(None))
    else:
        query = query.where(TransportRate.transport_type_id == rate.transport_type_id)
    if rate.id is not None:
        query = query.where(TransportRate.id != rate.id)
    others = (await db.execute(query)).scalars().all()
    for other in others:
        if rate.basis == RateBasis.FLAT.value:
            raise Conflict("The session already has a FLAT rate for this transport type")
        if rate.basis == RateBasis.PER_STOP.value and other.route_stop_id == rate.route_stop_id:
            raise Conflict("The session already has a rate for this stop and transport type")
        if rate.basis == RateBasis.DISTANCE_SLAB.value and \
                rate.distance_from_km < other.distance_to_km and other.distance_from_km < rate.distance_to_km:
            raise Conflict(
                f"The slab overlaps {other.distance_from_km}-{other.distance_to_km} km (rate {other.id})"
            )


async def create_rate(db: AsyncSession, data: RateCreate) -> TransportRate:
    await fee_repo.session_year_or_404(db, data.session_year_id)
    if data.transport_type_id is not None:
        await repo.get_or_404(db, TransportType, data.transport_type_id, "Transport type")
    if data.route_stop_id is not None:
        await setup.stop_or_error(db, data.route_stop_id)
    rate = TransportRate(**{**data.model_dump(), "basis": data.basis.value})
    await _check_clash(db, rate)
    db.add(rate)
    await db.flush()
    return rate


async def update_rate(db: AsyncSession, rate_id: int, data: RateUpdate) -> TransportRate:
    rate = await repo.get_or_404(db, TransportRate, rate_id, "Rate")
    changes = data.model_dump(exclude_unset=True)
    if rate.basis != RateBasis.DISTANCE_SLAB.value and (
        changes.get("distance_from_km") is not None or changes.get("distance_to_km") is not None
    ):
        raise Invalid("Only DISTANCE_SLAB rates have distances")
    for field, value in changes.items():
        if value is None and field in ("distance_from_km", "distance_to_km", "monthly_amount", "is_active"):
            raise Invalid(f"{field} cannot be empty")
        setattr(rate, field, value)
    if rate.basis == RateBasis.DISTANCE_SLAB.value and rate.distance_to_km <= rate.distance_from_km:
        raise Invalid("distance_to_km must be more than distance_from_km")
    await _check_clash(db, rate)
    await db.flush()
    return rate


async def delete_rate(db: AsyncSession, rate_id: int) -> None:
    """Assignments keep the amount they were given; their link to the rate is cleared."""
    rate = await repo.get_or_404(db, TransportRate, rate_id, "Rate")
    await db.delete(rate)
    await db.flush()


async def copy_rates(db: AsyncSession, data: RateCopy) -> int:
    """Copy one session's active rates to another session that has none yet."""
    if data.from_session_year_id == data.to_session_year_id:
        raise Invalid("Choose two different sessions")
    await fee_repo.session_year_or_404(db, data.from_session_year_id)
    await fee_repo.session_year_or_404(db, data.to_session_year_id)
    if await session_rates(db, data.to_session_year_id):
        raise Conflict("The target session already has rates")
    copied = 0
    for r in await session_rates(db, data.from_session_year_id):
        db.add(TransportRate(
            session_year_id=data.to_session_year_id, basis=r.basis, transport_type_id=r.transport_type_id,
            route_stop_id=r.route_stop_id, distance_from_km=r.distance_from_km, distance_to_km=r.distance_to_km,
            monthly_amount=r.monthly_amount, description=r.description,
        ))
        copied += 1
    await db.flush()
    return copied
