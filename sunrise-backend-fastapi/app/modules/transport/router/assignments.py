"""Routes: student transport assignments, pauses and rosters."""
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.modules.transport.deps import can_manage, can_view
from app.modules.transport.schemas import (
    AssignmentCancel, AssignmentChange, AssignmentCreate, AssignmentDiscontinue, AssignmentOut, AssignmentResult,
    PauseCreate, RouteRoster, VehicleRoster,
)
from app.modules.transport.service import assignments as assignment_service
from app.modules.transport.service import rosters as roster_service

router = APIRouter()


@router.get("/assignments", response_model=List[AssignmentOut])
async def list_assignments(
    session_year_id: Optional[int] = None, student_id: Optional[int] = None, route_id: Optional[int] = None,
    route_stop_id: Optional[int] = None, transport_type_id: Optional[int] = None, vehicle_id: Optional[int] = None,
    active_on: Optional[date] = None, include_cancelled: bool = False,
    user: User = Depends(can_view), db: AsyncSession = Depends(get_db),
):
    """Assignments, filtered. `active_on` lists those riding on that day."""
    return await assignment_service.list_assignments(
        db, session_year_id=session_year_id, student_id=student_id, route_id=route_id, route_stop_id=route_stop_id,
        transport_type_id=transport_type_id, vehicle_id=vehicle_id, active_on=active_on,
        include_cancelled=include_cancelled,
    )


@router.post("/assignments", response_model=AssignmentResult, status_code=status.HTTP_201_CREATED)
async def assign(body: AssignmentCreate, user: User = Depends(can_manage), db: AsyncSession = Depends(get_db)):
    """Assign a student to transport. Adds the Transport plan line and generates its dues up to this month."""
    result = await assignment_service.assign(db, body, user_id=user.id)
    await db.commit()
    return result


@router.get("/assignments/{assignment_id}", response_model=AssignmentOut)
async def get_assignment(assignment_id: int, user: User = Depends(can_view), db: AsyncSession = Depends(get_db)):
    return await assignment_service.get(db, assignment_id)


@router.post("/assignments/{assignment_id}/change", response_model=AssignmentResult)
async def change_assignment(assignment_id: int, body: AssignmentChange, user: User = Depends(can_manage),
                            db: AsyncSession = Depends(get_db)):
    """End this assignment the day before `effective_date` and start a new one on the new terms."""
    result = await assignment_service.change(db, assignment_id, body, user_id=user.id)
    await db.commit()
    return result


@router.post("/assignments/{assignment_id}/discontinue", response_model=AssignmentResult)
async def discontinue_assignment(assignment_id: int, body: AssignmentDiscontinue, user: User = Depends(can_manage),
                                 db: AsyncSession = Depends(get_db)):
    result = await assignment_service.discontinue(db, assignment_id, body, user_id=user.id)
    await db.commit()
    return result


@router.post("/assignments/{assignment_id}/cancel", response_model=AssignmentResult)
async def cancel_assignment(assignment_id: int, body: AssignmentCancel, user: User = Depends(can_manage),
                            db: AsyncSession = Depends(get_db)):
    """Cancel an assignment entered by mistake. Refused once money was paid against it."""
    result = await assignment_service.cancel(db, assignment_id, body, user_id=user.id)
    await db.commit()
    return result


@router.post("/assignments/{assignment_id}/pauses", response_model=AssignmentResult,
             status_code=status.HTTP_201_CREATED)
async def pause_assignment(assignment_id: int, body: PauseCreate, user: User = Depends(can_manage),
                           db: AsyncSession = Depends(get_db)):
    """Pause service for whole months; those months are not billed."""
    result = await assignment_service.pause(db, assignment_id, body, user_id=user.id)
    await db.commit()
    return result


@router.delete("/pauses/{pause_id}", response_model=AssignmentResult)
async def remove_pause(pause_id: int, user: User = Depends(can_manage), db: AsyncSession = Depends(get_db)):
    """Remove a pause; its months are billed again."""
    result = await assignment_service.resume(db, pause_id, user_id=user.id)
    await db.commit()
    return result


@router.get("/routes/{route_id}/roster", response_model=RouteRoster)
async def route_roster(route_id: int, on_date: Optional[date] = None, user: User = Depends(can_view),
                       db: AsyncSession = Depends(get_db)):
    """Riders of a route on a day (default today), stop by stop."""
    return await roster_service.route_roster(db, route_id, on_date or date.today())


@router.get("/vehicles/{vehicle_id}/roster", response_model=VehicleRoster)
async def vehicle_roster(vehicle_id: int, on_date: Optional[date] = None, user: User = Depends(can_view),
                         db: AsyncSession = Depends(get_db)):
    """Riders of every route a vehicle serves on a day (default today)."""
    return await roster_service.vehicle_roster(db, vehicle_id, on_date or date.today())
