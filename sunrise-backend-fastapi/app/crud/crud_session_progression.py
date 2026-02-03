"""
CRUD operations for Session Progression feature
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_, func
from datetime import datetime
import uuid

from app.models.student import Student
from app.models.student_session_history import StudentSessionHistory
from app.models.progression_action import ProgressionAction
from app.models.metadata import SessionYear, Class
from app.models.user import User


# Constants for progression actions (matching database IDs)
# Only PROMOTED, RETAINED, DEMOTED are supported for session progression
class ProgressionActionIds:
    PROMOTED = 1
    RETAINED = 2
    DEMOTED = 3


# Highest class ID (Class 8 = ID 12)
HIGHEST_CLASS_ID = 12


async def get_progression_actions(
    db: AsyncSession,
    active_only: bool = True
) -> List[ProgressionAction]:
    """Get all progression actions from metadata table"""
    query = select(ProgressionAction)
    if active_only:
        query = query.where(ProgressionAction.is_active == True)
    query = query.order_by(ProgressionAction.display_order)
    result = await db.execute(query)
    return result.scalars().all()


async def get_progression_action_by_id(
    db: AsyncSession,
    action_id: int
) -> Optional[ProgressionAction]:
    """Get a progression action by ID"""
    query = select(ProgressionAction).where(ProgressionAction.id == action_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_eligible_students_for_progression(
    db: AsyncSession,
    from_session_year_id: int,
    class_ids: Optional[List[int]] = None
) -> List[Student]:
    """Get students eligible for progression from a given session year"""
    query = select(Student).options(
        joinedload(Student.class_ref),
        joinedload(Student.session_year)
    ).where(
        and_(
            Student.session_year_id == from_session_year_id,
            Student.is_active == True,
            Student.is_deleted != True
        )
    )
    
    if class_ids:
        query = query.where(Student.class_id.in_(class_ids))
    
    query = query.order_by(Student.class_id, Student.first_name, Student.last_name)
    result = await db.execute(query)
    return result.scalars().unique().all()


async def get_next_class_id(db: AsyncSession, current_class_id: int) -> Optional[int]:
    """Get the next class ID for promotion"""
    # Get class with sort_order greater than current
    current_class = await db.execute(
        select(Class).where(Class.id == current_class_id)
    )
    current = current_class.scalar_one_or_none()
    
    if not current:
        return None
    
    # Find next class by sort_order
    next_class = await db.execute(
        select(Class).where(
            and_(
                Class.sort_order > current.sort_order,
                Class.is_active == True
            )
        ).order_by(Class.sort_order).limit(1)
    )
    next_cls = next_class.scalar_one_or_none()
    return next_cls.id if next_cls else None


async def get_previous_class_id(db: AsyncSession, current_class_id: int) -> Optional[int]:
    """Get the previous class ID for demotion"""
    current_class = await db.execute(
        select(Class).where(Class.id == current_class_id)
    )
    current = current_class.scalar_one_or_none()

    if not current:
        return None

    # Find previous class by sort_order
    prev_class = await db.execute(
        select(Class).where(
            and_(
                Class.sort_order < current.sort_order,
                Class.is_active == True
            )
        ).order_by(Class.sort_order.desc()).limit(1)
    )
    prev_cls = prev_class.scalar_one_or_none()
    return prev_cls.id if prev_cls else None


async def create_session_history_record(
    db: AsyncSession,
    student_id: int,
    session_year_id: int,
    class_id: int,
    progression_action_id: int,
    progressed_by: int,
    section: Optional[str] = None,
    roll_number: Optional[str] = None,
    from_session_year_id: Optional[int] = None,
    from_class_id: Optional[int] = None,
    progression_batch_id: Optional[str] = None,
    remarks: Optional[str] = None,
    snapshot_data: Optional[Dict[str, Any]] = None
) -> StudentSessionHistory:
    """Create a session history record for a student"""
    history = StudentSessionHistory(
        student_id=student_id,
        session_year_id=session_year_id,
        class_id=class_id,
        section=section,
        roll_number=roll_number,
        progression_action_id=progression_action_id,
        from_session_year_id=from_session_year_id,
        from_class_id=from_class_id,
        progression_batch_id=progression_batch_id,
        progressed_by=progressed_by,
        remarks=remarks,
        snapshot_data=snapshot_data
    )
    db.add(history)
    return history


async def progress_student(
    db: AsyncSession,
    student_id: int,
    from_session_year_id: int,
    to_session_year_id: int,
    progression_action_id: int,
    target_class_id: int,
    progressed_by: int,
    batch_id: str,
    section: Optional[str] = None,
    roll_number: Optional[str] = None,
    remarks: Optional[str] = None
) -> Dict[str, Any]:
    """
    Progress a single student to a new session year.
    Updates the student record and creates a session history entry.
    """
    # Get the student
    student_query = await db.execute(
        select(Student).options(
            joinedload(Student.class_ref),
            joinedload(Student.session_year)
        ).where(Student.id == student_id)
    )
    student = student_query.scalar_one_or_none()

    if not student:
        return {"success": False, "error": "Student not found"}

    # Store current values for history
    from_class_id = student.class_id
    current_section = student.section
    current_roll_number = student.roll_number

    # Get progression action details
    action = await get_progression_action_by_id(db, progression_action_id)
    if not action:
        return {"success": False, "error": "Invalid progression action"}

    # Create snapshot of student data before progression
    snapshot = {
        "class_id": from_class_id,
        "class_name": student.class_ref.description if student.class_ref else None,
        "section": current_section,
        "roll_number": current_roll_number,
        "session_year_id": from_session_year_id,
        "session_year_name": student.session_year.description if student.session_year else None
    }

    # Check if action creates a new session entry
    if action.creates_new_session:
        # Update student's current session and class
        student.session_year_id = to_session_year_id
        student.class_id = target_class_id
        student.section = section
        student.roll_number = roll_number

        # Set original admission info if not already set
        if student.original_session_year_id is None:
            student.original_session_year_id = from_session_year_id
        if student.original_class_id is None:
            student.original_class_id = from_class_id

    # Handle non-session creating actions (GRADUATED, TRANSFERRED_OUT, WITHDRAWN)
    if not action.creates_new_session:
        student.is_active = False

    # Create session history record
    await create_session_history_record(
        db=db,
        student_id=student_id,
        session_year_id=to_session_year_id,
        class_id=target_class_id,
        section=section,
        roll_number=roll_number,
        progression_action_id=progression_action_id,
        from_session_year_id=from_session_year_id,
        from_class_id=from_class_id,
        progression_batch_id=batch_id,
        progressed_by=progressed_by,
        remarks=remarks,
        snapshot_data=snapshot
    )

    return {
        "success": True,
        "student_id": student_id,
        "admission_number": student.admission_number,
        "student_name": f"{student.first_name} {student.last_name}",
        "progression_action_id": progression_action_id,
        "progression_action_name": action.name,
        "from_class_id": from_class_id,
        "to_class_id": target_class_id
    }


async def bulk_progress_students(
    db: AsyncSession,
    from_session_year_id: int,
    to_session_year_id: int,
    students_data: List[Dict[str, Any]],
    progressed_by: int
) -> Dict[str, Any]:
    """
    Bulk progress multiple students.
    Returns summary of successful and failed progressions.
    """
    batch_id = f"PROG-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}"
    results = []
    successful_count = 0
    failed_count = 0

    for student_data in students_data:
        try:
            result = await progress_student(
                db=db,
                student_id=student_data["student_id"],
                from_session_year_id=from_session_year_id,
                to_session_year_id=to_session_year_id,
                progression_action_id=student_data["progression_action_id"],
                target_class_id=student_data.get("target_class_id"),
                progressed_by=progressed_by,
                batch_id=batch_id,
                section=student_data.get("target_section"),
                roll_number=student_data.get("target_roll_number"),
                remarks=student_data.get("remarks")
            )

            if result["success"]:
                successful_count += 1
            else:
                failed_count += 1

            results.append(result)

        except Exception as e:
            failed_count += 1
            results.append({
                "success": False,
                "student_id": student_data["student_id"],
                "error_message": str(e)
            })

    # Commit all changes
    await db.commit()

    return {
        "batch_id": batch_id,
        "from_session_year_id": from_session_year_id,
        "to_session_year_id": to_session_year_id,
        "total_processed": len(students_data),
        "successful_count": successful_count,
        "failed_count": failed_count,
        "results": results
    }


async def get_student_progression_history(
    db: AsyncSession,
    student_id: int
) -> List[StudentSessionHistory]:
    """Get progression history for a specific student"""
    query = select(StudentSessionHistory).options(
        joinedload(StudentSessionHistory.session_year),
        joinedload(StudentSessionHistory.class_ref),
        joinedload(StudentSessionHistory.progression_action),
        joinedload(StudentSessionHistory.from_session_year),
        joinedload(StudentSessionHistory.from_class),
        joinedload(StudentSessionHistory.progressed_by_user)
    ).where(
        StudentSessionHistory.student_id == student_id
    ).order_by(StudentSessionHistory.progressed_at.desc())

    result = await db.execute(query)
    return result.scalars().unique().all()


async def rollback_progression_batch(
    db: AsyncSession,
    batch_id: str,
    rolled_back_by: int,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Rollback all progressions in a batch.
    Restores students to their previous state.
    """
    # Get all history records for this batch
    query = select(StudentSessionHistory).options(
        joinedload(StudentSessionHistory.student)
    ).where(
        StudentSessionHistory.progression_batch_id == batch_id
    )

    result = await db.execute(query)
    history_records = result.scalars().unique().all()

    if not history_records:
        return {
            "batch_id": batch_id,
            "students_affected": 0,
            "success": False,
            "message": "No records found for this batch ID"
        }

    students_affected = 0

    for record in history_records:
        student = record.student
        if student and record.from_session_year_id and record.from_class_id:
            # Restore student to previous state
            student.session_year_id = record.from_session_year_id
            student.class_id = record.from_class_id

            # Restore section and roll number from snapshot if available
            if record.snapshot_data:
                student.section = record.snapshot_data.get("section")
                student.roll_number = record.snapshot_data.get("roll_number")

            # Reactivate if was deactivated
            student.is_active = True

            students_affected += 1

        # Delete the history record
        await db.delete(record)

    await db.commit()

    return {
        "batch_id": batch_id,
        "students_affected": students_affected,
        "success": True,
        "message": f"Successfully rolled back {students_affected} student(s)"
    }


async def get_progression_statistics(
    db: AsyncSession,
    session_year_id: int,
    class_ids: Optional[List[int]] = None
) -> Dict[str, Any]:
    """Get progression statistics for a session year"""
    # Base query for counting by action
    query = select(
        StudentSessionHistory.progression_action_id,
        func.count(StudentSessionHistory.id).label("count")
    ).where(
        StudentSessionHistory.session_year_id == session_year_id
    ).group_by(
        StudentSessionHistory.progression_action_id
    )

    if class_ids:
        query = query.where(StudentSessionHistory.class_id.in_(class_ids))

    result = await db.execute(query)
    by_action = result.all()

    # Get action details
    actions = await get_progression_actions(db)
    action_map = {a.id: a for a in actions}

    stats_by_action = []
    for action_id, count in by_action:
        action = action_map.get(action_id)
        if action:
            stats_by_action.append({
                "action_id": action_id,
                "action_name": action.name,
                "action_icon": action.icon,
                "action_color": action.color_code,
                "count": count
            })

    # Get session year name
    session_query = await db.execute(
        select(SessionYear).where(SessionYear.id == session_year_id)
    )
    session_year = session_query.scalar_one_or_none()

    return {
        "session_year_id": session_year_id,
        "session_year_name": session_year.description if session_year else None,
        "total_students_progressed": sum(count for _, count in by_action),
        "by_action": stats_by_action,
        "generated_at": datetime.now()
    }
