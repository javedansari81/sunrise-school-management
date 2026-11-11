"""Routes: transport types, vehicles, routes, stops and rates."""
from typing import List, Optional

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.modules.transport.constants import RateBasis
from app.modules.transport.deps import can_manage, can_view
from app.modules.transport.schemas import (
    RateCopy, RateCopyResult, RateCreate, RateOut, RateQuote, RateQuoteOut, RateUpdate, RouteCreate, RouteOut,
    RouteUpdate, StopCreate, StopOrder, StopOut, StopUpdate, TransportTypeCreate, TransportTypeOut,
    TransportTypeUpdate, VehicleCreate, VehicleOut, VehicleUpdate,
)
from app.modules.transport.service import rates as rate_service
from app.modules.transport.service import setup as setup_service

router = APIRouter()
NO_CONTENT = status.HTTP_204_NO_CONTENT


# ---------------------------------------------------------------------------
# Transport types
# ---------------------------------------------------------------------------

@router.get("/transport-types", response_model=List[TransportTypeOut])
async def list_transport_types(include_inactive: bool = False, user: User = Depends(can_view),
                               db: AsyncSession = Depends(get_db)):
    return await setup_service.list_types(db, include_inactive=include_inactive)


@router.post("/transport-types", response_model=TransportTypeOut, status_code=status.HTTP_201_CREATED)
async def create_transport_type(body: TransportTypeCreate, user: User = Depends(can_manage),
                                db: AsyncSession = Depends(get_db)):
    type_ = await setup_service.create_type(db, body)
    await db.commit()
    return type_


@router.patch("/transport-types/{type_id}", response_model=TransportTypeOut)
async def update_transport_type(type_id: int, body: TransportTypeUpdate, user: User = Depends(can_manage),
                                db: AsyncSession = Depends(get_db)):
    type_ = await setup_service.update_type(db, type_id, body)
    await db.commit()
    return type_


@router.delete("/transport-types/{type_id}", status_code=NO_CONTENT)
async def delete_transport_type(type_id: int, user: User = Depends(can_manage), db: AsyncSession = Depends(get_db)):
    await setup_service.delete_type(db, type_id)
    await db.commit()
    return Response(status_code=NO_CONTENT)


# ---------------------------------------------------------------------------
# Vehicles
# ---------------------------------------------------------------------------

@router.get("/vehicles", response_model=List[VehicleOut])
async def list_vehicles(include_inactive: bool = False, transport_type_id: Optional[int] = None,
                        user: User = Depends(can_view), db: AsyncSession = Depends(get_db)):
    return await setup_service.list_vehicles(db, include_inactive=include_inactive,
                                             transport_type_id=transport_type_id)


@router.post("/vehicles", response_model=VehicleOut, status_code=status.HTTP_201_CREATED)
async def create_vehicle(body: VehicleCreate, user: User = Depends(can_manage), db: AsyncSession = Depends(get_db)):
    vehicle = await setup_service.create_vehicle(db, body)
    await db.commit()
    return vehicle


@router.patch("/vehicles/{vehicle_id}", response_model=VehicleOut)
async def update_vehicle(vehicle_id: int, body: VehicleUpdate, user: User = Depends(can_manage),
                         db: AsyncSession = Depends(get_db)):
    vehicle = await setup_service.update_vehicle(db, vehicle_id, body)
    await db.commit()
    return vehicle


@router.delete("/vehicles/{vehicle_id}", status_code=NO_CONTENT)
async def delete_vehicle(vehicle_id: int, user: User = Depends(can_manage), db: AsyncSession = Depends(get_db)):
    await setup_service.delete_vehicle(db, vehicle_id)
    await db.commit()
    return Response(status_code=NO_CONTENT)


# ---------------------------------------------------------------------------
# Routes and stops
# ---------------------------------------------------------------------------

@router.get("/routes", response_model=List[RouteOut])
async def list_routes(include_inactive: bool = False, vehicle_id: Optional[int] = None,
                      user: User = Depends(can_view), db: AsyncSession = Depends(get_db)):
    return await setup_service.list_routes(db, include_inactive=include_inactive, vehicle_id=vehicle_id)


@router.post("/routes", response_model=RouteOut, status_code=status.HTTP_201_CREATED)
async def create_route(body: RouteCreate, user: User = Depends(can_manage), db: AsyncSession = Depends(get_db)):
    route = await setup_service.create_route(db, body)
    await db.commit()
    return route


@router.get("/routes/{route_id}", response_model=RouteOut)
async def get_route(route_id: int, user: User = Depends(can_view), db: AsyncSession = Depends(get_db)):
    return await setup_service.get_route(db, route_id)


@router.patch("/routes/{route_id}", response_model=RouteOut)
async def update_route(route_id: int, body: RouteUpdate, user: User = Depends(can_manage),
                       db: AsyncSession = Depends(get_db)):
    route = await setup_service.update_route(db, route_id, body)
    await db.commit()
    return route


@router.delete("/routes/{route_id}", status_code=NO_CONTENT)
async def delete_route(route_id: int, user: User = Depends(can_manage), db: AsyncSession = Depends(get_db)):
    await setup_service.delete_route(db, route_id)
    await db.commit()
    return Response(status_code=NO_CONTENT)


@router.post("/routes/{route_id}/stops", response_model=StopOut, status_code=status.HTTP_201_CREATED)
async def add_stop(route_id: int, body: StopCreate, user: User = Depends(can_manage),
                   db: AsyncSession = Depends(get_db)):
    stop = await setup_service.add_stop(db, route_id, body)
    await db.commit()
    return stop


@router.put("/routes/{route_id}/stops/order", response_model=RouteOut)
async def reorder_stops(route_id: int, body: StopOrder, user: User = Depends(can_manage),
                        db: AsyncSession = Depends(get_db)):
    route = await setup_service.reorder_stops(db, route_id, body)
    await db.commit()
    return route


@router.patch("/stops/{stop_id}", response_model=StopOut)
async def update_stop(stop_id: int, body: StopUpdate, user: User = Depends(can_manage),
                      db: AsyncSession = Depends(get_db)):
    stop = await setup_service.update_stop(db, stop_id, body)
    await db.commit()
    return stop


@router.delete("/stops/{stop_id}", status_code=NO_CONTENT)
async def delete_stop(stop_id: int, user: User = Depends(can_manage), db: AsyncSession = Depends(get_db)):
    await setup_service.delete_stop(db, stop_id)
    await db.commit()
    return Response(status_code=NO_CONTENT)


# ---------------------------------------------------------------------------
# Rates
# ---------------------------------------------------------------------------

@router.get("/rates", response_model=List[RateOut])
async def list_rates(session_year_id: Optional[int] = None, basis: Optional[RateBasis] = None,
                     transport_type_id: Optional[int] = None, route_stop_id: Optional[int] = None,
                     include_inactive: bool = False, user: User = Depends(can_view),
                     db: AsyncSession = Depends(get_db)):
    return await rate_service.list_rates(
        db, session_year_id=session_year_id, basis=basis.value if basis else None,
        transport_type_id=transport_type_id, route_stop_id=route_stop_id, include_inactive=include_inactive,
    )


@router.post("/rates", response_model=RateOut, status_code=status.HTTP_201_CREATED)
async def create_rate(body: RateCreate, user: User = Depends(can_manage), db: AsyncSession = Depends(get_db)):
    rate = await rate_service.create_rate(db, body)
    await db.commit()
    return rate


@router.post("/rates/quote", response_model=RateQuoteOut)
async def quote_rate(body: RateQuote, user: User = Depends(can_view), db: AsyncSession = Depends(get_db)):
    """The rate an assignment with this placement would get (nothing is saved)."""
    return await rate_service.quote(db, body)


@router.post("/rates/copy", response_model=RateCopyResult)
async def copy_rates(body: RateCopy, user: User = Depends(can_manage), db: AsyncSession = Depends(get_db)):
    copied = await rate_service.copy_rates(db, body)
    await db.commit()
    return {"copied": copied}


@router.patch("/rates/{rate_id}", response_model=RateOut)
async def update_rate(rate_id: int, body: RateUpdate, user: User = Depends(can_manage),
                      db: AsyncSession = Depends(get_db)):
    rate = await rate_service.update_rate(db, rate_id, body)
    await db.commit()
    return rate


@router.delete("/rates/{rate_id}", status_code=NO_CONTENT)
async def delete_rate(rate_id: int, user: User = Depends(can_manage), db: AsyncSession = Depends(get_db)):
    await rate_service.delete_rate(db, rate_id)
    await db.commit()
    return Response(status_code=NO_CONTENT)
