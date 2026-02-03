"""
API endpoints for Session Progression feature.
SUPER_ADMIN only access for all write operations.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.session_progression import (
    ProgressionActionResponse,
    StudentProgressionPreviewRequest, StudentProgressionPreviewItem,
    StudentProgressionPreviewResponse, StudentProgressionItem,
    BulkProgressionRequest, BulkProgressionResultItem, BulkProgressionResponse,
    StudentProgressionHistoryItem, StudentProgressionHistoryResponse,
    RollbackRequest, RollbackResponse,
    ProgressionReportRequest, ProgressionReportResponse
)
from app.crud.crud_session_progression import (
    get_progression_actions, get_eligible_students_for_progression,
    get_next_class_id, bulk_progress_students, get_student_progression_history,
    rollback_progression_batch, get_progression_statistics,
    ProgressionActionIds, HIGHEST_CLASS_ID
)
from app.crud.metadata import session_year_crud, class_crud

router = APIRouter()


# SUPER_ADMIN user type ID
SUPER_ADMIN_TYPE_ID = 6


def require_super_admin(current_user: User) -> User:
    """Check if user is SUPER_ADMIN"""
    if current_user.user_type_id != SUPER_ADMIN_TYPE_ID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only SUPER_ADMIN can perform session progression operations"
        )
    return current_user


@router.get("/actions", response_model=List[ProgressionActionResponse])
async def get_progression_action_types(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all available progression action types.
    This is used to populate dropdowns in the UI.
    """
    actions = await get_progression_actions(db)
    return actions


@router.post("/preview", response_model=StudentProgressionPreviewResponse)
async def preview_eligible_students(
    request: StudentProgressionPreviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Preview students eligible for progression from one session to another.
    Shows suggested action as PROMOTED for all students. Admin can change to RETAINED or DEMOTED.
    """
    require_super_admin(current_user)
    
    # Validate session years
    from_session = await session_year_crud.get_by_id_async(db, request.from_session_year_id)
    to_session = await session_year_crud.get_by_id_async(db, request.to_session_year_id)
    
    if not from_session:
        raise HTTPException(status_code=404, detail="From session year not found")
    if not to_session:
        raise HTTPException(status_code=404, detail="To session year not found")
    
    # Get eligible students
    students = await get_eligible_students_for_progression(
        db, request.from_session_year_id, request.class_ids
    )
    
    preview_items = []
    for student in students:
        # Default action is PROMOTED for all students
        suggested_action_id = ProgressionActionIds.PROMOTED
        suggested_action_name = "PROMOTED"

        # Get target class (next class or same class for highest class)
        if student.class_id >= HIGHEST_CLASS_ID:
            # Highest class - keep in same class (user can choose RETAINED)
            target_class_id = student.class_id
            target_class_name = student.class_ref.description if student.class_ref else None
        else:
            # Normal class - suggest next class
            target_class_id = await get_next_class_id(db, student.class_id)
            target_class = await class_crud.get_by_id_async(db, target_class_id) if target_class_id else None
            target_class_name = target_class.description if target_class else None

        preview_items.append(StudentProgressionPreviewItem(
            student_id=student.id,
            admission_number=student.admission_number,
            first_name=student.first_name,
            last_name=student.last_name,
            current_class_id=student.class_id,
            current_class_name=student.class_ref.description if student.class_ref else "",
            current_section=student.section,
            current_roll_number=student.roll_number,
            suggested_action_id=suggested_action_id,
            suggested_action_name=suggested_action_name,
            target_class_id=target_class_id,
            target_class_name=target_class_name
        ))

    return StudentProgressionPreviewResponse(
        from_session_year_id=request.from_session_year_id,
        from_session_year_name=from_session.description,
        to_session_year_id=request.to_session_year_id,
        to_session_year_name=to_session.description,
        total_students=len(preview_items),
        students=preview_items
    )


@router.post("/bulk-progress", response_model=BulkProgressionResponse)
async def bulk_progress_students_endpoint(
    request: BulkProgressionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Bulk progress multiple students from one session year to another.
    Each student can have a different progression action (PROMOTED, RETAINED, etc.).
    Returns a batch ID that can be used for rollback if needed.
    """
    require_super_admin(current_user)

    # Validate session years
    from_session = await session_year_crud.get_by_id_async(db, request.from_session_year_id)
    to_session = await session_year_crud.get_by_id_async(db, request.to_session_year_id)

    if not from_session:
        raise HTTPException(status_code=404, detail="From session year not found")
    if not to_session:
        raise HTTPException(status_code=404, detail="To session year not found")

    # Prepare student data for CRUD
    students_data = [
        {
            "student_id": item.student_id,
            "progression_action_id": item.progression_action_id,
            "target_class_id": item.target_class_id,
            "target_section": item.target_section,
            "target_roll_number": item.target_roll_number,
            "remarks": item.remarks
        }
        for item in request.students
    ]

    result = await bulk_progress_students(
        db=db,
        from_session_year_id=request.from_session_year_id,
        to_session_year_id=request.to_session_year_id,
        students_data=students_data,
        progressed_by=current_user.id
    )

    # Convert results to response model
    result_items = [
        BulkProgressionResultItem(
            student_id=r["student_id"],
            success=r["success"],
            admission_number=r.get("admission_number"),
            student_name=r.get("student_name"),
            progression_action_name=r.get("progression_action_name"),
            error_message=r.get("error_message") or r.get("error")
        )
        for r in result["results"]
    ]

    return BulkProgressionResponse(
        batch_id=result["batch_id"],
        from_session_year_id=result["from_session_year_id"],
        to_session_year_id=result["to_session_year_id"],
        total_processed=result["total_processed"],
        successful_count=result["successful_count"],
        failed_count=result["failed_count"],
        results=result_items,
        processed_at=datetime.now()
    )


@router.get("/history/{student_id}", response_model=StudentProgressionHistoryResponse)
async def get_student_history(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the complete progression history for a specific student.
    Shows all session transitions with action taken, who performed it, and when.
    """
    history_records = await get_student_progression_history(db, student_id)

    history_items = [
        StudentProgressionHistoryItem(
            id=record.id,
            session_year_id=record.session_year_id,
            session_year_name=record.session_year.description if record.session_year else None,
            class_id=record.class_id,
            class_name=record.class_ref.description if record.class_ref else None,
            section=record.section,
            roll_number=record.roll_number,
            progression_action_id=record.progression_action_id,
            progression_action_name=record.progression_action.name if record.progression_action else None,
            from_session_year_id=record.from_session_year_id,
            from_session_year_name=record.from_session_year.description if record.from_session_year else None,
            from_class_id=record.from_class_id,
            from_class_name=record.from_class.description if record.from_class else None,
            progression_batch_id=record.progression_batch_id,
            progressed_by=record.progressed_by,
            progressed_by_name=f"{record.progressed_by_user.first_name} {record.progressed_by_user.last_name}" if record.progressed_by_user else None,
            progressed_at=record.progressed_at,
            remarks=record.remarks
        )
        for record in history_records
    ]

    return StudentProgressionHistoryResponse(
        student_id=student_id,
        total_records=len(history_items),
        history=history_items
    )


@router.post("/rollback", response_model=RollbackResponse)
async def rollback_batch(
    request: RollbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Rollback all progressions in a batch.
    Restores students to their previous session, class, section, and roll number.
    """
    require_super_admin(current_user)

    result = await rollback_progression_batch(
        db=db,
        batch_id=request.batch_id,
        rolled_back_by=current_user.id,
        reason=request.reason
    )

    return RollbackResponse(
        batch_id=result["batch_id"],
        students_affected=result["students_affected"],
        success=result["success"],
        message=result["message"],
        rolled_back_at=datetime.now() if result["success"] else None
    )


@router.get("/report", response_model=ProgressionReportResponse)
async def get_progression_report(
    session_year_id: int = Query(..., description="Session year to get report for"),
    class_ids: Optional[List[int]] = Query(None, description="Filter by class IDs"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a progression report for a session year.
    Shows statistics on how many students were promoted, retained, or demoted.
    """
    stats = await get_progression_statistics(db, session_year_id, class_ids)

    return ProgressionReportResponse(
        session_year_id=stats["session_year_id"],
        session_year_name=stats["session_year_name"],
        total_students_progressed=stats["total_students_progressed"],
        by_action=stats["by_action"],
        generated_at=stats["generated_at"]
    )

