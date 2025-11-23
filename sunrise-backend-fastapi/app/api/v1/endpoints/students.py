from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import math

from app.core.database import get_db
from app.crud.crud_student import student_crud
from app.crud import fee_record_crud
from app.crud.crud_teacher import teacher_crud
from app.schemas.student import (
    Student, StudentCreate, StudentUpdate, StudentProfileUpdate, StudentTeacherUpdate, StudentWithFees, StudentListResponse,
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
    class_filter: Optional[int] = Query(None, description="Filter by class ID"),
    section_filter: Optional[str] = Query(None, description="Filter by section"),
    gender_filter: Optional[int] = Query(None, description="Filter by gender ID"),
    search: Optional[str] = Query(None, description="Search by name, admission number, or parent name"),
    is_active: Optional[bool] = Query(None, description="Filter by active status (None = all, True = active only, False = inactive only)"),
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all students with comprehensive filters and metadata
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
    except HTTPException:
        # Re-raise HTTP exceptions (these are intentional errors with proper status codes)
        raise
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


@router.get("/my-dashboard-stats")
async def get_my_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current student's dashboard statistics including academic info, fee summary, and leave stats
    """
    # Verify user is a student
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
    student_query = text("""
        SELECT
            s.*,
            c.description as class_name,
            c.name as class_code,
            g.description as gender_name,
            sy.name as session_year_name
        FROM sunrise.students s
        LEFT JOIN sunrise.classes c ON s.class_id = c.id
        LEFT JOIN sunrise.genders g ON s.gender_id = g.id
        LEFT JOIN sunrise.session_years sy ON s.session_year_id = sy.id
        WHERE s.id = :student_id
    """)

    result = await db.execute(student_query, {"student_id": student.id})
    student_data = result.fetchone()

    if not student_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student data not found"
        )

    # Get leave statistics for this student
    leave_stats_query = text("""
        SELECT
            COUNT(*) as total,
            COUNT(CASE WHEN leave_status_id = 1 THEN 1 END) as pending,
            COUNT(CASE WHEN leave_status_id = 2 THEN 1 END) as approved,
            COUNT(CASE WHEN leave_status_id = 3 THEN 1 END) as rejected
        FROM sunrise.leave_requests
        WHERE applicant_type = 'student' AND applicant_id = :student_id
    """)

    leave_result = await db.execute(leave_stats_query, {"student_id": student.id})
    leave_stats = leave_result.fetchone()

    # Get fee summary for this student
    fee_summary_query = text("""
        SELECT
            fr.id,
            fr.total_amount,
            fr.balance_amount,
            COALESCE(SUM(fp.amount), 0) as total_paid,
            MAX(fp.payment_date) as last_payment_date
        FROM sunrise.fee_records fr
        LEFT JOIN sunrise.fee_payments fp ON fr.id = fp.fee_record_id
        WHERE fr.student_id = :student_id
        AND fr.session_year_id = :session_year_id
        GROUP BY fr.id, fr.total_amount, fr.balance_amount
    """)

    fee_result = await db.execute(fee_summary_query, {
        "student_id": student.id,
        "session_year_id": student_data.session_year_id
    })
    fee_data = fee_result.fetchone()

    # Calculate fee information
    has_fee_records = fee_data is not None
    if has_fee_records:
        total_fee = float(fee_data.total_amount) if fee_data.total_amount else 0.0
        total_paid = float(fee_data.total_paid) if fee_data.total_paid else 0.0
        remaining_balance = float(fee_data.balance_amount) if fee_data.balance_amount else 0.0
        last_payment_date = fee_data.last_payment_date.isoformat() if fee_data.last_payment_date else None
        payment_percentage = (total_paid / total_fee * 100) if total_fee > 0 else 0.0
    else:
        total_fee = 0.0
        total_paid = 0.0
        remaining_balance = 0.0
        last_payment_date = None
        payment_percentage = 0.0

    # Get transport information if enrolled
    transport_query = text("""
        SELECT
            ste.id,
            ste.transport_type_id,
            tt.description as transport_type_name,
            ste.pickup_location,
            ste.drop_location,
            ste.monthly_fee,
            ste.distance_km
        FROM sunrise.student_transport_enrollment ste
        LEFT JOIN sunrise.transport_types tt ON ste.transport_type_id = tt.id
        WHERE ste.student_id = :student_id
        AND ste.is_active = TRUE
        AND ste.discontinue_date IS NULL
        LIMIT 1
    """)

    transport_result = await db.execute(transport_query, {"student_id": student.id})
    transport_data = transport_result.fetchone()

    transport_info = None
    if transport_data:
        transport_info = {
            "transport_type_name": transport_data.transport_type_name or "N/A",
            "pickup_location": transport_data.pickup_location or "N/A",
            "drop_location": transport_data.drop_location or "N/A",
            "monthly_fee": float(transport_data.monthly_fee) if transport_data.monthly_fee else 0.0,
            "distance_km": float(transport_data.distance_km) if transport_data.distance_km else 0.0
        }

    return {
        "academic_info": {
            "admission_number": student_data.admission_number,
            "first_name": student_data.first_name,
            "last_name": student_data.last_name,
            "class_name": student_data.class_name,
            "class_code": student_data.class_code,
            "section": student_data.section,
            "roll_number": student_data.roll_number,
            "session_year": student_data.session_year_name,
            "gender": student_data.gender_name,
            "date_of_birth": student_data.date_of_birth.isoformat() if student_data.date_of_birth else None,
            "admission_date": student_data.admission_date.isoformat() if student_data.admission_date else None
        },
        "leave_stats": {
            "total": leave_stats.total if leave_stats else 0,
            "pending": leave_stats.pending if leave_stats else 0,
            "approved": leave_stats.approved if leave_stats else 0,
            "rejected": leave_stats.rejected if leave_stats else 0
        },
        "fee_summary": {
            "has_fee_records": has_fee_records,
            "total_fee": total_fee,
            "total_paid": total_paid,
            "remaining_balance": remaining_balance,
            "last_payment_date": last_payment_date,
            "payment_percentage": round(payment_percentage, 2)
        },
        "transport_info": transport_info
    }


@router.put("/{student_id}/teacher-update", response_model=Student)
async def teacher_update_student(
    student_id: int,
    profile_data: StudentTeacherUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update limited student fields by teacher
    Teachers can only edit: roll_number, section, blood_group
    """
    # Verify user is a teacher
    if current_user.user_type_enum != UserTypeEnum.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can access this endpoint"
        )

    # Find student record
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Update only the allowed fields
    update_data = profile_data.dict(exclude_unset=True)
    updated_student = await student_crud.update(db, db_obj=student, obj_in=update_data)

    # Return updated student with metadata
    student_with_metadata = await student_crud.get_with_metadata(db, id=updated_student.id)
    return Student.from_orm_with_metadata(student_with_metadata)


@router.get("/my-class-students", response_model=StudentListResponse)
async def get_my_class_students(
    section_filter: Optional[str] = Query(None, description="Filter by section"),
    gender_filter: Optional[int] = Query(None, description="Filter by gender ID"),
    search: Optional[str] = Query(None, description="Search by name, admission number, or parent name"),
    is_active: Optional[bool] = Query(None, description="Filter by active status (None = all, True = active only, False = inactive only)"),
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get students for the current teacher's assigned class
    Only accessible by teachers who are assigned as class teachers
    """
    # Verify user is a teacher
    if current_user.user_type_enum != UserTypeEnum.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can access this endpoint"
        )

    # Get teacher profile
    teacher = await teacher_crud.get_by_user_id(db, user_id=current_user.id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found"
        )

    # Check if teacher is a class teacher
    if not teacher.class_teacher_of_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only class teachers can access student profiles"
        )

    # Get students for this class teacher's assigned class
    skip = (page - 1) * per_page
    students, total = await student_crud.get_multi_with_filters(
        db,
        skip=skip,
        limit=per_page,
        class_filter=teacher.class_teacher_of_id,  # Filter by teacher's assigned class
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


@router.get("/{student_id}", response_model=Student)
async def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get student details by ID with metadata
    """
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
                "guardian_name": student.guardian_name,
                "guardian_phone": student.guardian_phone,
                "guardian_email": student.guardian_email,
                "guardian_relation": student.guardian_relation
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


# Search endpoint removed - not used in frontend, search functionality integrated into main GET endpoint


# Dashboard stats endpoint removed - not used in frontend


# Pending fees endpoint removed - functionality integrated into enhanced fee management system


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

    # Guardian/Emergency Contact (editable)
    guardian_name: Optional[str] = Field(None, max_length=200)
    guardian_phone: Optional[str] = Field(None, max_length=20)
    guardian_email: Optional[str] = None
    guardian_relation: Optional[str] = Field(None, max_length=50)

    # Note: Read-only fields are excluded:
    # - admission_number, roll_number, class_id, session_year_id
    # - admission_date, gender_id (system/admin managed)


# =====================================================
# Profile Picture Upload Endpoints
# =====================================================

@router.post("/my-profile/upload-picture", response_model=Dict[str, Any])
async def upload_my_profile_picture(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload profile picture for current student
    """
    from app.utils.profile_picture_helpers import (
        validate_profile_picture,
        upload_profile_picture_to_cloudinary,
        delete_profile_picture_from_cloudinary,
        update_student_profile_picture
    )

    # Verify user is a student
    if current_user.user_type_enum != UserTypeEnum.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )

    # Find student record
    student = await student_crud.get_by_user_id(db, user_id=current_user.id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found for this user"
        )

    # Validate file
    await validate_profile_picture(file)

    # Delete old profile picture if exists
    if student.profile_picture_cloudinary_id:
        await delete_profile_picture_from_cloudinary(student.profile_picture_cloudinary_id)

    # Upload new picture
    cloudinary_url, cloudinary_public_id = await upload_profile_picture_to_cloudinary(
        file=file,
        folder="profiles/students",
        identifier=str(student.id)
    )

    # Update database
    await update_student_profile_picture(
        db=db,
        student_id=student.id,
        profile_picture_url=cloudinary_url,
        profile_picture_cloudinary_id=cloudinary_public_id
    )

    # Return updated profile
    student_with_metadata = await student_crud.get_with_metadata(db, id=student.id)
    return {
        "message": "Profile picture uploaded successfully",
        "profile_picture_url": cloudinary_url,
        "student": Student.from_orm_with_metadata(student_with_metadata)
    }


@router.delete("/my-profile/delete-picture", response_model=Dict[str, Any])
async def delete_my_profile_picture(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete profile picture for current student
    """
    from app.utils.profile_picture_helpers import (
        delete_profile_picture_from_cloudinary,
        update_student_profile_picture
    )

    # Verify user is a student
    if current_user.user_type_enum != UserTypeEnum.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )

    # Find student record
    student = await student_crud.get_by_user_id(db, user_id=current_user.id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found for this user"
        )

    # Delete from Cloudinary if exists
    if student.profile_picture_cloudinary_id:
        await delete_profile_picture_from_cloudinary(student.profile_picture_cloudinary_id)

    # Update database
    await update_student_profile_picture(
        db=db,
        student_id=student.id,
        profile_picture_url=None,
        profile_picture_cloudinary_id=None
    )

    # Return updated profile
    student_with_metadata = await student_crud.get_with_metadata(db, id=student.id)
    return {
        "message": "Profile picture deleted successfully",
        "student": Student.from_orm_with_metadata(student_with_metadata)
    }


@router.post("/{student_id}/upload-picture", response_model=Dict[str, Any])
async def upload_student_profile_picture(
    student_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload profile picture for a specific student (Admin and Teacher)
    """
    from app.utils.profile_picture_helpers import (
        validate_profile_picture,
        upload_profile_picture_to_cloudinary,
        delete_profile_picture_from_cloudinary,
        update_student_profile_picture
    )

    # Verify user is admin or teacher
    if current_user.user_type_enum not in [UserTypeEnum.ADMIN, UserTypeEnum.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and teachers can upload profile pictures for students"
        )

    # Find student record
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Validate file
    await validate_profile_picture(file)

    # Delete old profile picture if exists
    if student.profile_picture_cloudinary_id:
        await delete_profile_picture_from_cloudinary(student.profile_picture_cloudinary_id)

    # Upload new picture
    cloudinary_url, cloudinary_public_id = await upload_profile_picture_to_cloudinary(
        file=file,
        folder="profiles/students",
        identifier=str(student.id)
    )

    # Update database
    await update_student_profile_picture(
        db=db,
        student_id=student.id,
        profile_picture_url=cloudinary_url,
        profile_picture_cloudinary_id=cloudinary_public_id
    )

    # Return updated profile
    student_with_metadata = await student_crud.get_with_metadata(db, id=student.id)
    return {
        "message": "Profile picture uploaded successfully",
        "profile_picture_url": cloudinary_url,
        "student": Student.from_orm_with_metadata(student_with_metadata)
    }


@router.delete("/{student_id}/delete-picture", response_model=Dict[str, Any])
async def delete_student_profile_picture(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete profile picture for a specific student (Admin only)
    """
    from app.utils.profile_picture_helpers import (
        delete_profile_picture_from_cloudinary,
        update_student_profile_picture
    )

    # Verify user is admin
    if current_user.user_type_enum != UserTypeEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete profile pictures for other students"
        )

    # Find student record
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Delete from Cloudinary if exists
    if student.profile_picture_cloudinary_id:
        await delete_profile_picture_from_cloudinary(student.profile_picture_cloudinary_id)

    # Update database
    await update_student_profile_picture(
        db=db,
        student_id=student.id,
        profile_picture_url=None,
        profile_picture_cloudinary_id=None
    )

    # Return updated profile
    student_with_metadata = await student_crud.get_with_metadata(db, id=student.id)
    return {
        "message": "Profile picture deleted successfully",
        "student": Student.from_orm_with_metadata(student_with_metadata)
    }



