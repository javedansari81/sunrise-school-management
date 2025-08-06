from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import math

from app.core.database import get_db
from app.crud.crud_student import CRUDStudent
from app.crud import fee_record_crud

# Initialize CRUD instance
student_crud = CRUDStudent()
from app.schemas.student import (
    Student, StudentCreate, StudentUpdate, StudentProfileUpdate, StudentWithFees, StudentListResponse,
    ClassEnum, GenderEnum
)
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.user import UserTypeEnum

router = APIRouter()


@router.get("/", response_model=StudentListResponse)
@router.get("", response_model=StudentListResponse)  # Handle both with and without trailing slash
async def get_students(
    class_filter: Optional[str] = Query(None, description="Filter by class"),
    section_filter: Optional[str] = Query(None, description="Filter by section"),
    gender_filter: Optional[str] = Query(None, description="Filter by gender"),
    search: Optional[str] = Query(None, description="Search by name, admission number, or parent name"),
    is_active: Optional[bool] = Query(None, description="Filter by active status (None = all, True = active only, False = inactive only)"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all students with comprehensive filters and metadata
    """
    student_crud = CRUDStudent()
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

    # Convert to response schema with metadata
    result_students = []
    for student in students:
        student_with_metadata = await student_crud.get_with_metadata(db, id=student.id)
        result_students.append(Student.from_orm_with_metadata(student_with_metadata))

    total_pages = math.ceil(total / per_page)

    return StudentListResponse(
        students=result_students,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.post("/", response_model=Dict[str, Any])
@router.post("", response_model=Dict[str, Any])  # Handle both with and without trailing slash
async def create_student(
    student_data: StudentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new student record with metadata validation
    """
    try:
        from app.utils.soft_delete_helpers import validate_student_creation_with_soft_delete_check
        from sqlalchemy.exc import IntegrityError
        import logging

        # Validate creation considering soft-deleted records
        can_create, success_message, error_message = await validate_student_creation_with_soft_delete_check(
            db, student_data.admission_number, student_data.email
        )

        if not can_create:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )

        try:
            # Create student with metadata validation
            student = await student_crud.create_with_validation(db, obj_in=student_data)
            student_with_metadata = await student_crud.get_with_metadata(db, id=student.id)

            # Create response with student data and success message if replacing a soft-deleted record
            response_data = Student.from_orm_with_metadata(student_with_metadata).dict()
            if success_message:
                response_data["success_message"] = success_message

            return response_data

        except IntegrityError as e:
            # Handle database constraint errors gracefully
            await db.rollback()
            logging.error(f"Database constraint error creating student: {str(e)}")

            # Parse the error to provide user-friendly messages
            error_str = str(e).lower()

            if "admission_number" in error_str and "already exists" in error_str:
                # Check if it's a soft-deleted record that should be replaceable
                from app.utils.soft_delete_helpers import check_student_soft_deleted_by_admission_number
                soft_deleted = await check_student_soft_deleted_by_admission_number(db, student_data.admission_number)

                if soft_deleted:
                    detail = f"Student with admission number {student_data.admission_number} exists in archived records. Please contact system administrator to resolve this conflict."
                else:
                    detail = f"Student with admission number {student_data.admission_number} already exists"

            elif "email" in error_str and "already exists" in error_str:
                # Check if it's a soft-deleted record that should be replaceable
                from app.utils.soft_delete_helpers import check_student_soft_deleted_by_email
                soft_deleted = await check_student_soft_deleted_by_email(db, student_data.email)

                if soft_deleted:
                    detail = f"Student with email {student_data.email} exists in archived records. Please contact system administrator to resolve this conflict."
                else:
                    detail = f"Student with email {student_data.email} already exists"
            else:
                detail = "A student with this information already exists. Please check admission number and email."

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=detail
            )
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Handle any other unexpected errors
        await db.rollback()
        logging.error(f"Unexpected error creating student: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the student. Please try again."
        )


@router.get("/my-profile", response_model=Student)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current student's profile (for logged-in students)
    """
    # Verify user is a student using the enum comparison
    if current_user.user_type_enum != UserTypeEnum.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )

    # Find student record linked to this user
    student = await student_crud.get_by_user_id(db, user_id=current_user.id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found for this user"
        )

    # Get student with metadata
    student_with_metadata = await student_crud.get_with_metadata(db, id=student.id)
    if not student_with_metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )

    return Student.from_orm_with_metadata(student_with_metadata)


@router.put("/my-profile", response_model=Student)
async def update_my_profile(
    profile_data: StudentProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update current student's profile (for logged-in students)
    Only allows editing of non-restricted fields
    """
    # Verify user is a student using the enum comparison
    if current_user.user_type_enum != UserTypeEnum.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )

    # Find student record linked to this user
    student = await student_crud.get_by_user_id(db, user_id=current_user.id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found for this user"
        )

    # Update only the allowed fields
    update_data = profile_data.dict(exclude_unset=True)
    updated_student = await student_crud.update(db, db_obj=student, obj_in=update_data)

    # Return updated student with metadata
    student_with_metadata = await student_crud.get_with_metadata(db, id=updated_student.id)
    return Student.from_orm_with_metadata(student_with_metadata)


@router.get("/{student_id}", response_model=Student)
async def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get student details by ID with metadata
    """
    student_crud = CRUDStudent()
    student = await student_crud.get_with_metadata(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    return Student.from_orm_with_metadata(student)


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


# Student Profile Management Schemas
class StudentProfileUpdate(BaseModel):
    """Schema for student profile updates - excludes read-only fields"""
    # Personal Information (editable)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    blood_group: Optional[str] = Field(None, max_length=5)

    # Contact Information (editable)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)

    # Parent Information (editable)
    father_name: Optional[str] = Field(None, max_length=100)
    father_phone: Optional[str] = Field(None, max_length=15)
    father_email: Optional[str] = None
    father_occupation: Optional[str] = Field(None, max_length=100)

    mother_name: Optional[str] = Field(None, max_length=100)
    mother_phone: Optional[str] = Field(None, max_length=15)
    mother_email: Optional[str] = None
    mother_occupation: Optional[str] = Field(None, max_length=100)

    # Emergency Contact (editable)
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=15)
    emergency_contact_relation: Optional[str] = Field(None, max_length=50)

    # Academic Information (editable)
    previous_school: Optional[str] = Field(None, max_length=200)

    # Note: Read-only fields are excluded:
    # - admission_number, roll_number, class_id, session_year_id
    # - admission_date, gender_id (system/admin managed)



