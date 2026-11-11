"""Routes: concessions, student fee plans, dues and late fees."""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.modules.fees.constants import DueStatus
from app.modules.fees.deps import can_configure, can_view
from app.modules.fees.schemas import (
    ConcessionRuleCreate, ConcessionRuleOut, ConcessionRuleUpdate, DueCancel, DueOut, DuesGenerateRequest,
    DuesGenerateResult, LateFeeRequest, LateFeeResult, PlanBuildRequest, PlanBuildResult, PlanLineCreate,
    PlanLineEnd, PlanLineOut, RevokeRequest, SiblingConcessionPreview, StudentConcessionCreate,
    StudentConcessionOut,
)
from app.modules.fees.service import concessions as concession_service
from app.modules.fees.service import dues as dues_service
from app.modules.fees.service import plans as plan_service

router = APIRouter()


# ---------------------------------------------------------------------------
# Concession rules
# ---------------------------------------------------------------------------

@router.get("/concession-rules", response_model=List[ConcessionRuleOut])
async def list_concession_rules(include_inactive: bool = False, user: User = Depends(can_view),
                                db: AsyncSession = Depends(get_db)):
    return await concession_service.list_rules(db, include_inactive=include_inactive)


@router.post("/concession-rules", response_model=ConcessionRuleOut, status_code=status.HTTP_201_CREATED)
async def create_concession_rule(body: ConcessionRuleCreate, user: User = Depends(can_configure),
                                 db: AsyncSession = Depends(get_db)):
    rule = await concession_service.create_rule(db, body, user_id=user.id)
    await db.commit()
    return rule


@router.patch("/concession-rules/{rule_id}", response_model=ConcessionRuleOut)
async def update_concession_rule(rule_id: int, body: ConcessionRuleUpdate, user: User = Depends(can_configure),
                                 db: AsyncSession = Depends(get_db)):
    """Edit a rule, including the sibling tiers. Deactivate with is_active=false."""
    rule = await concession_service.update_rule(db, rule_id, body, user_id=user.id)
    await db.commit()
    return rule


# ---------------------------------------------------------------------------
# Student concessions and sibling concession
# ---------------------------------------------------------------------------

@router.get("/students/{student_id}/concessions", response_model=List[StudentConcessionOut])
async def list_student_concessions(student_id: int, session_year_id: Optional[int] = None,
                                   include_inactive: bool = False, user: User = Depends(can_view),
                                   db: AsyncSession = Depends(get_db)):
    return await concession_service.list_student_concessions(
        db, student_id, session_year_id=session_year_id, include_inactive=include_inactive)


@router.post("/students/{student_id}/concessions", response_model=StudentConcessionOut,
             status_code=status.HTTP_201_CREATED)
async def grant_student_concession(student_id: int, body: StudentConcessionCreate,
                                   user: User = Depends(can_configure), db: AsyncSession = Depends(get_db)):
    """Grant a staff, scholarship or custom concession. It reaches unpaid dues on the next dues generation."""
    concession = await concession_service.grant_concession(db, student_id, body, user_id=user.id)
    await db.commit()
    return concession


@router.post("/student-concessions/{concession_id}/revoke", response_model=StudentConcessionOut)
async def revoke_student_concession(concession_id: int, body: RevokeRequest, user: User = Depends(can_configure),
                                    db: AsyncSession = Depends(get_db)):
    concession = await concession_service.revoke_concession(db, concession_id, user_id=user.id, reason=body.reason)
    await db.commit()
    return concession


@router.get("/students/{student_id}/sibling-concession", response_model=SiblingConcessionPreview)
async def sibling_concession(student_id: int, session_year_id: int, user: User = Depends(can_view),
                             db: AsyncSession = Depends(get_db)):
    """The student's position among enrolled siblings (eldest first by date of birth) and the percent it gives."""
    return await concession_service.sibling_preview(db, student_id, session_year_id)


# ---------------------------------------------------------------------------
# Plans
# ---------------------------------------------------------------------------

@router.post("/plans/build", response_model=PlanBuildResult)
async def build_plans(body: PlanBuildRequest, user: User = Depends(can_configure), db: AsyncSession = Depends(get_db)):
    """
    Create or update class-based plan lines from the session's published fee
    structure, for the whole school, one class or some students. Safe to run
    again. Changes take effect from `effective_from` (default: a student's first
    build covers the whole session, later builds start this month).
    """
    result = await plan_service.build_class_plans(db, body, user_id=user.id)
    await db.commit()
    return result


@router.get("/students/{student_id}/plan", response_model=List[PlanLineOut])
async def student_plan(student_id: int, session_year_id: int, include_inactive: bool = False,
                       user: User = Depends(can_view), db: AsyncSession = Depends(get_db)):
    return await plan_service.list_plan(db, student_id, session_year_id, include_inactive=include_inactive)


@router.post("/students/{student_id}/plan-lines", response_model=PlanLineOut, status_code=status.HTTP_201_CREATED)
async def add_plan_line(student_id: int, body: PlanLineCreate, user: User = Depends(can_configure),
                        db: AsyncSession = Depends(get_db)):
    """Add a manual charge (one-off by default) for one student. Billed on the next dues generation."""
    line = await plan_service.add_manual_line(db, student_id, body, user_id=user.id)
    await db.commit()
    return line


@router.post("/plan-lines/{line_id}/end", response_model=PlanLineOut)
async def end_plan_line(line_id: int, body: PlanLineEnd, user: User = Depends(can_configure),
                        db: AsyncSession = Depends(get_db)):
    """Stop a plan line after `last_period` (or cancel it from its start). Unpaid later dues are cancelled."""
    line = await plan_service.end_plan_line(db, line_id, last_period=body.last_period, reason=body.reason,
                                            user_id=user.id)
    await db.commit()
    return line


# ---------------------------------------------------------------------------
# Dues
# ---------------------------------------------------------------------------

@router.post("/dues/generate", response_model=DuesGenerateResult)
async def generate_dues(body: DuesGenerateRequest, user: User = Depends(can_configure),
                        db: AsyncSession = Depends(get_db)):
    """
    Generate dues from plans up to `through_period` (default: this month) for the
    school, a class or one student. Safe to run again. Also re-prices unpaid dues,
    adds late fees and applies the students' credit.
    """
    result = await dues_service.generate_dues(db, body, user_id=user.id)
    await db.commit()
    return result


@router.get("/students/{student_id}/dues", response_model=List[DueOut])
async def student_dues(student_id: int, session_year_id: Optional[int] = None, open_only: bool = False,
                       status_filter: Optional[List[DueStatus]] = Query(default=None, alias="status"),
                       user: User = Depends(can_view), db: AsyncSession = Depends(get_db)):
    return await dues_service.list_dues(
        db, student_id, session_year_id=session_year_id, open_only=open_only,
        status=[s.value for s in status_filter] if status_filter else None)


@router.post("/dues/{due_id}/cancel", response_model=DueOut)
async def cancel_due(due_id: int, body: DueCancel, user: User = Depends(can_configure),
                     db: AsyncSession = Depends(get_db)):
    """Cancel a due nothing was paid against."""
    due = await dues_service.cancel_due(db, due_id, reason=body.reason, user_id=user.id)
    await db.commit()
    return due


@router.post("/late-fees/apply", response_model=LateFeeResult)
async def apply_late_fees(body: LateFeeRequest, user: User = Depends(can_configure),
                          db: AsyncSession = Depends(get_db)):
    """Add late fees for overdue months (per-school settings). A scheduled job will call this later."""
    result = await dues_service.apply_late_fees(db, as_of=body.as_of, session_year_id=body.session_year_id,
                                                user_id=user.id)
    await db.commit()
    return result
