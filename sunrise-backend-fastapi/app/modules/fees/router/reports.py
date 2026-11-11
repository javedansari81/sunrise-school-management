"""Routes: fee reports and the student ledger."""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.modules.fees.audit import to_json
from app.modules.fees.deps import can_report, can_view
from app.modules.fees.service import reports as report_service

router = APIRouter()


def _json(data) -> JSONResponse:
    """Reports return money as exact strings ("1500.00"), like every other fee route."""
    return JSONResponse(to_json(data))


@router.get("/reports/collection")
async def collection_report(date_from: date, date_to: date, user: User = Depends(can_report),
                            db: AsyncSession = Depends(get_db)):
    """Money received between two dates, net of reversals, by day, method and fee head."""
    return _json(await report_service.collection(db, date_from=date_from, date_to=date_to))


@router.get("/reports/pending-by-class")
async def pending_by_class(session_year_id: int, as_of: Optional[date] = None, user: User = Depends(can_report),
                           db: AsyncSession = Depends(get_db)):
    """Open and overdue balance per class for a session."""
    return _json(await report_service.pending_by_class(db, session_year_id=session_year_id, as_of=as_of))


@router.get("/reports/consistency")
async def consistency_check(user: User = Depends(can_report), db: AsyncSession = Depends(get_db)):
    """Checks that stored paid amounts match the allocations, and no payment is over-allocated."""
    return _json(await report_service.consistency(db))


@router.get("/students/{student_id}/ledger")
async def student_ledger(student_id: int, session_year_id: Optional[int] = None, user: User = Depends(can_view),
                         db: AsyncSession = Depends(get_db)):
    """Every due, payment and reversal of a student in date order, with a running balance."""
    return _json(await report_service.student_ledger(db, student_id, session_year_id=session_year_id))
