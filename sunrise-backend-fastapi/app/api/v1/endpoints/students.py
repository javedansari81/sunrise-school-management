from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import math

from app.core.database import get_db
from app.crud import student_crud, fee_record_crud
from app.schemas.student import (
    Student, StudentCreate, StudentUpdate, StudentWithFees, StudentListResponse,
    ClassEnum, GenderEnum
)
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=StudentListResponse)
async def get_students(
    class_filter: Optional[str] = Query(None, description="Filter by class"),
    section_filter: Optional[str] = Query(None, description="Filter by section"),
    gender_filter: Optional[str] = Query(None, description="Filter by gender"),
    search: Optional[str] = Query(None, description="Search by name, admission number, or parent name"),
    is_active: bool = Query(True, description="Filter by active status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all students with comprehensive filters
    """
    skip = (page - 1) * per_page
    students, total = await student_crud.get_multi_with_filters(
        db,
        skip=skip,
        limit=per_page,
        class_filter=class_filter,
        section_filter=section_filter,
        gender_filter=gender_filter,
        search=search,
        is_active=is_active
    )

    total_pages = math.ceil(total / per_page)

    return StudentListResponse(
        students=students,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.post("/", response_model=Student)
async def create_student(
    student_data: StudentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new student record
    """
    # Check if admission number already exists
    existing_student = await student_crud.get_by_admission_number(
        db, admission_number=student_data.admission_number
    )
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student with this admission number already exists"
        )

    student = await student_crud.create(db, obj_in=student_data)
    return student


@router.get("/{student_id}", response_model=Student)
async def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get student details by ID
    """
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    return student


@router.put("/{student_id}", response_model=Student)
async def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update student information
    """
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Check if admission number is being changed and if it already exists
    if student_data.admission_number and student_data.admission_number != student.admission_number:
        existing_student = await student_crud.get_by_admission_number(
            db, admission_number=student_data.admission_number
        )
        if existing_student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student with this admission number already exists"
            )

    updated_student = await student_crud.update(
        db, db_obj=student, obj_in=student_data
    )
    return updated_student


@router.delete("/{student_id}")
async def delete_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Deactivate student record (soft delete)
    """
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Soft delete by setting is_active to False
    deactivated_student = await student_crud.remove(db, id=student_id)
    return {"message": "Student deactivated successfully", "student_id": student_id}


@router.get("/{student_id}/profile")
async def get_student_profile(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get complete student profile including academic records
    """
    # Get student with fee records
    student = await student_crud.get_with_fees(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Calculate fee summary
    total_fees_due = sum(fee.balance_amount for fee in student.fee_records)
    total_fees_paid = sum(fee.paid_amount for fee in student.fee_records)

    # Determine fee status
    fee_status = "Paid"
    if total_fees_due > 0:
        fee_status = "Pending"
        # Check if any fees are overdue
        from datetime import date
        overdue_fees = [fee for fee in student.fee_records if fee.due_date < date.today() and fee.balance_amount > 0]
        if overdue_fees:
            fee_status = "Overdue"

    return {
        "student_id": student_id,
        "profile": {
            "personal_info": {
                "id": student.id,
                "admission_number": student.admission_number,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "date_of_birth": student.date_of_birth,
                "gender": student.gender,
                "email": student.email,
                "phone": student.phone,
                "address": student.address,
                "admission_date": student.admission_date,
                "previous_school": student.previous_school
            },
            "academic_info": {
                "current_class": student.current_class,
                "section": student.section,
                "roll_number": student.roll_number,
                "is_active": student.is_active
            },
            "parent_info": {
                "father_name": student.father_name,
                "father_phone": student.father_phone,
                "father_email": student.father_email,
                "father_occupation": student.father_occupation,
                "mother_name": student.mother_name,
                "mother_phone": student.mother_phone,
                "mother_email": student.mother_email,
                "mother_occupation": student.mother_occupation,
                "emergency_contact_name": student.emergency_contact_name,
                "emergency_contact_phone": student.emergency_contact_phone,
                "emergency_contact_relation": student.emergency_contact_relation
            },
            "fee_status": {
                "total_fees_due": total_fees_due,
                "total_fees_paid": total_fees_paid,
                "status": fee_status,
                "fee_records_count": len(student.fee_records)
            }
        }
    }


@router.get("/class/{class_name}")
async def get_students_by_class(
    class_name: str,
    section: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all students in a specific class
    """
    students = await student_crud.get_by_class(
        db, class_name=class_name, section=section
    )

    return {
        "class": class_name,
        "section": section,
        "students": students,
        "total_students": len(students)
    }


@router.get("/search")
async def search_students(
    q: str = Query(..., description="Search term"),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Search students by name, admission number, or other criteria
    """
    students = await student_crud.search_students(
        db, search_term=q, limit=limit
    )

    return {
        "search_term": q,
        "students": students,
        "total_found": len(students)
    }


@router.get("/dashboard/stats")
async def get_student_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get student dashboard statistics
    """
    stats = await student_crud.get_dashboard_stats(db)

    # Get recent admissions
    recent_admissions = await student_crud.get_recent_admissions(db, limit=5)

    # Get class statistics
    class_stats = await student_crud.get_class_statistics(db)

    return {
        "total_students": stats['total_students'],
        "gender_distribution": stats['gender_distribution'],
        "class_distribution": stats['class_distribution'],
        "recent_admissions": recent_admissions,
        "class_statistics": class_stats
    }


@router.get("/with-pending-fees")
async def get_students_with_pending_fees(
    session_year: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get students with pending fees
    """
    students = await student_crud.get_students_with_pending_fees(
        db, session_year=session_year
    )

    return {
        "session_year": session_year or "All Sessions",
        "students_with_pending_fees": students,
        "total_students": len(students)
    }
