from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import math
import json
from datetime import datetime

from app.core.database import get_db
from app.crud import teacher_crud
from app.schemas.teacher import (
    Teacher, TeacherCreate, TeacherUpdate, TeacherProfile, TeacherListResponse, TeacherDashboard,
    GenderEnum, TeacherProfileUpdate
)
from app.api.deps import get_current_active_user
from app.models.user import User, UserTypeEnum

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
@router.get("", response_model=Dict[str, Any])  # Handle both with and without trailing slash
async def get_teachers(
    department_filter: Optional[int] = Query(None, description="Filter by department ID"),
    position_filter: Optional[int] = Query(None, description="Filter by position ID"),
    qualification_filter: Optional[int] = Query(None, description="Filter by qualification ID"),
    employment_status_filter: Optional[int] = Query(None, description="Filter by employment status ID"),
    search: Optional[str] = Query(None, description="Search by name, employee ID, or email"),
    is_active: bool = Query(True, description="Filter by active status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all teachers with comprehensive filters and metadata
    """
    skip = (page - 1) * per_page
    teachers, total = await teacher_crud.get_multi_with_filters(
        db,
        skip=skip,
        limit=per_page,
        department_filter=department_filter,
        position_filter=position_filter,
        qualification_filter=qualification_filter,
        employment_status_filter=employment_status_filter,
        search=search,
        is_active=is_active
    )

    total_pages = math.ceil(total / per_page)

    return {
        "teachers": teachers,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages
    }


@router.post("/", response_model=Dict[str, Any])
@router.post("", response_model=Dict[str, Any])  # Handle both with and without trailing slash
async def create_teacher(
    teacher_data: TeacherCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new teacher with user account
    """
    from app.utils.soft_delete_helpers import validate_teacher_creation_with_soft_delete_check
    from sqlalchemy.exc import IntegrityError
    import logging

    # Validate creation considering soft-deleted records
    can_create, success_message, error_message = await validate_teacher_creation_with_soft_delete_check(
        db, teacher_data.employee_id, teacher_data.email
    )

    if not can_create:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    try:
        # Create teacher with user account
        teacher = await teacher_crud.create_with_user_account(db, obj_in=teacher_data)

        # Return teacher with metadata and success message
        teacher_with_metadata = await teacher_crud.get_with_metadata(db, id=teacher.id)

        # Add success message if replacing a soft-deleted record
        if success_message:
            teacher_with_metadata["success_message"] = success_message

        return teacher_with_metadata

    except IntegrityError as e:
        # Handle database constraint errors gracefully
        await db.rollback()
        logging.error(f"Database constraint error creating teacher: {str(e)}")

        # Parse the error to provide user-friendly messages
        error_str = str(e).lower()

        if "employee_id" in error_str and "already exists" in error_str:
            # Check if it's a soft-deleted record that should be replaceable
            from app.utils.soft_delete_helpers import check_teacher_soft_deleted_by_employee_id
            soft_deleted = await check_teacher_soft_deleted_by_employee_id(db, teacher_data.employee_id)

            if soft_deleted:
                detail = f"Teacher with employee ID {teacher_data.employee_id} exists in archived records. Please contact system administrator to resolve this conflict."
            else:
                detail = f"Teacher with employee ID {teacher_data.employee_id} already exists"

        elif "email" in error_str and "already exists" in error_str:
            # Check if it's a soft-deleted record that should be replaceable
            from app.utils.soft_delete_helpers import check_teacher_soft_deleted_by_email
            soft_deleted = await check_teacher_soft_deleted_by_email(db, teacher_data.email)

            if soft_deleted:
                detail = f"Teacher with email {teacher_data.email} exists in archived records. Please contact system administrator to resolve this conflict."
            else:
                detail = f"Teacher with email {teacher_data.email} already exists"
        else:
            detail = "A teacher with this information already exists. Please check employee ID and email."

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

    except HTTPException:
        # Re-raise HTTP exceptions (these are intentional errors with proper status codes)
        raise

    except Exception as e:
        # Handle any other unexpected errors
        await db.rollback()
        logging.error(f"Unexpected error creating teacher: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the teacher. Please try again."
        )


@router.get("/my-profile", response_model=Dict[str, Any])
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current teacher's profile (for logged-in teachers)
    """
    # Verify user is a teacher using the enum comparison
    if current_user.user_type_enum != UserTypeEnum.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can access this endpoint"
        )

    # Find teacher record linked to this user
    teacher = await teacher_crud.get_by_user_id(db, user_id=current_user.id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found for this user"
        )

    # Get teacher with metadata
    teacher_with_metadata = await teacher_crud.get_with_metadata(db, id=teacher.id)
    if not teacher_with_metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found"
        )

    # Parse JSON fields
    if teacher_with_metadata.get('subjects'):
        try:
            teacher_with_metadata['subjects_list'] = json.loads(teacher_with_metadata['subjects'])
        except (json.JSONDecodeError, TypeError):
            teacher_with_metadata['subjects_list'] = []
    else:
        teacher_with_metadata['subjects_list'] = []

    return teacher_with_metadata


@router.get("/{teacher_id}", response_model=Dict[str, Any])
async def get_teacher(
    teacher_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get teacher by ID with complete profile and metadata
    """
    teacher_with_metadata = await teacher_crud.get_with_metadata(db, id=teacher_id)
    if not teacher_with_metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )

    # Parse JSON fields if they exist
    if teacher_with_metadata.get('subjects'):
        try:
            teacher_with_metadata['subjects_list'] = json.loads(teacher_with_metadata['subjects'])
        except (json.JSONDecodeError, TypeError):
            teacher_with_metadata['subjects_list'] = []
    else:
        teacher_with_metadata['subjects_list'] = []

    if teacher_with_metadata.get('classes_assigned'):
        try:
            teacher_with_metadata['classes_assigned_list'] = json.loads(teacher_with_metadata['classes_assigned'])
        except (json.JSONDecodeError, TypeError):
            teacher_with_metadata['classes_assigned_list'] = []
    else:
        teacher_with_metadata['classes_assigned_list'] = []

    return teacher_with_metadata


@router.put("/my-profile", response_model=Dict[str, Any])
async def update_my_profile(
    profile_data: TeacherProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update current teacher's profile (for logged-in teachers)
    Only allows editing of non-restricted fields
    """
    # Verify user is a teacher using the enum comparison
    if current_user.user_type_enum != UserTypeEnum.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can access this endpoint"
        )

    # Find teacher record linked to this user
    teacher = await teacher_crud.get_by_user_id(db, user_id=current_user.id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found for this user"
        )

    # Update only the allowed fields
    update_data = profile_data.dict(exclude_unset=True)
    updated_teacher = await teacher_crud.update(db, db_obj=teacher, obj_in=update_data)

    # Return updated teacher with metadata
    teacher_with_metadata = await teacher_crud.get_with_metadata(db, id=updated_teacher.id)
    return teacher_with_metadata


@router.put("/{teacher_id}", response_model=Dict[str, Any])
async def update_teacher(
    teacher_id: int,
    teacher_data: TeacherUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update teacher by ID and return complete profile with metadata
    """
    teacher = await teacher_crud.get(db, id=teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )

    # Check if employee ID is being changed and if it already exists
    if teacher_data.employee_id and teacher_data.employee_id != teacher.employee_id:
        existing_teacher = await teacher_crud.get_by_employee_id(
            db, employee_id=teacher_data.employee_id
        )
        if existing_teacher:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Teacher with this employee ID already exists"
            )

    # Check if email is being changed and if it already exists
    if teacher_data.email and teacher_data.email != teacher.email:
        existing_email = await teacher_crud.get_by_email(
            db, email=teacher_data.email
        )
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Teacher with this email already exists"
            )

    updated_teacher = await teacher_crud.update(
        db, db_obj=teacher, obj_in=teacher_data
    )

    # Return updated teacher with complete metadata
    teacher_with_metadata = await teacher_crud.get_with_metadata(db, id=updated_teacher.id)

    # Parse JSON fields if they exist
    if teacher_with_metadata.get('subjects'):
        try:
            teacher_with_metadata['subjects_list'] = json.loads(teacher_with_metadata['subjects'])
        except (json.JSONDecodeError, TypeError):
            teacher_with_metadata['subjects_list'] = []
    else:
        teacher_with_metadata['subjects_list'] = []

    if teacher_with_metadata.get('classes_assigned'):
        try:
            teacher_with_metadata['classes_assigned_list'] = json.loads(teacher_with_metadata['classes_assigned'])
        except (json.JSONDecodeError, TypeError):
            teacher_with_metadata['classes_assigned_list'] = []
    else:
        teacher_with_metadata['classes_assigned_list'] = []

    return teacher_with_metadata


@router.delete("/{teacher_id}")
async def delete_teacher(
    teacher_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Soft delete teacher by ID
    """
    teacher = await teacher_crud.get(db, id=teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )

    # Soft delete teacher
    deleted_teacher = await teacher_crud.soft_delete(db, id=teacher_id)
    return {"message": "Teacher deleted successfully", "teacher_id": teacher_id}


@router.get("/department/{department}")
async def get_teachers_by_department(
    department: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all teachers in a specific department
    """
    teachers = await teacher_crud.get_by_department(db, department=department)

    return {
        "department": department,
        "teachers": teachers,
        "total_teachers": len(teachers)
    }


@router.get("/subject/{subject}")
async def get_teachers_by_subject(
    subject: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all teachers who teach a specific subject
    """
    teachers = await teacher_crud.get_by_subjects(db, subject=subject)

    return {
        "subject": subject,
        "teachers": teachers,
        "total_teachers": len(teachers)
    }


# NOTE: Public faculty endpoint moved to /api/v1/public/faculty
# This removes the duplicate endpoint that was causing confusion
# The public faculty endpoint is now only available at /api/v1/public/faculty


@router.get("/search")
async def search_teachers(
    q: str = Query(..., description="Search term"),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Search teachers by name, employee ID, or email
    """
    teachers = await teacher_crud.search_teachers(
        db, search_term=q, limit=limit
    )

    return {
        "search_term": q,
        "teachers": teachers,
        "total_found": len(teachers)
    }


@router.get("/dashboard/stats", response_model=TeacherDashboard)
async def get_teacher_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get teacher dashboard statistics
    """
    stats = await teacher_crud.get_dashboard_stats(db)

    # Get recent joinings
    recent_joinings = await teacher_crud.get_recent_joinings(db, limit=5)

    return TeacherDashboard(
        total_teachers=stats['total_teachers'],
        active_teachers=stats['active_teachers'],
        departments=stats['departments'],
        qualification_breakdown=stats['qualification_breakdown'],
        experience_breakdown=stats['experience_breakdown'],
        recent_joinings=recent_joinings
    )


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
    Upload profile picture for current teacher
    """
    from app.utils.profile_picture_helpers import (
        validate_profile_picture,
        upload_profile_picture_to_cloudinary,
        delete_profile_picture_from_cloudinary,
        update_teacher_profile_picture
    )

    # Verify user is a teacher
    if current_user.user_type_enum != UserTypeEnum.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can access this endpoint"
        )

    # Find teacher record
    teacher = await teacher_crud.get_by_user_id(db, user_id=current_user.id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found for this user"
        )

    # Validate file
    await validate_profile_picture(file)

    # Delete old profile picture if exists
    if teacher.profile_picture_cloudinary_id:
        await delete_profile_picture_from_cloudinary(teacher.profile_picture_cloudinary_id)

    # Upload new picture
    cloudinary_url, cloudinary_public_id = await upload_profile_picture_to_cloudinary(
        file=file,
        folder="profiles/teachers",
        identifier=str(teacher.id)
    )

    # Update database
    await update_teacher_profile_picture(
        db=db,
        teacher_id=teacher.id,
        profile_picture_url=cloudinary_url,
        profile_picture_cloudinary_id=cloudinary_public_id
    )

    # Return updated profile
    teacher_with_metadata = await teacher_crud.get_with_metadata(db, id=teacher.id)
    return {
        "message": "Profile picture uploaded successfully",
        "profile_picture_url": cloudinary_url,
        "teacher": teacher_with_metadata
    }


@router.delete("/my-profile/delete-picture", response_model=Dict[str, Any])
async def delete_my_profile_picture(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete profile picture for current teacher
    """
    from app.utils.profile_picture_helpers import (
        delete_profile_picture_from_cloudinary,
        update_teacher_profile_picture
    )

    # Verify user is a teacher
    if current_user.user_type_enum != UserTypeEnum.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can access this endpoint"
        )

    # Find teacher record
    teacher = await teacher_crud.get_by_user_id(db, user_id=current_user.id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found for this user"
        )

    # Delete from Cloudinary if exists
    if teacher.profile_picture_cloudinary_id:
        await delete_profile_picture_from_cloudinary(teacher.profile_picture_cloudinary_id)

    # Update database
    await update_teacher_profile_picture(
        db=db,
        teacher_id=teacher.id,
        profile_picture_url=None,
        profile_picture_cloudinary_id=None
    )

    # Return updated profile
    teacher_with_metadata = await teacher_crud.get_with_metadata(db, id=teacher.id)
    return {
        "message": "Profile picture deleted successfully",
        "teacher": teacher_with_metadata
    }


@router.post("/{teacher_id}/upload-picture", response_model=Dict[str, Any])
async def upload_teacher_profile_picture(
    teacher_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload profile picture for a specific teacher (Admin only)
    """
    from app.utils.profile_picture_helpers import (
        validate_profile_picture,
        upload_profile_picture_to_cloudinary,
        delete_profile_picture_from_cloudinary,
        update_teacher_profile_picture
    )

    # Verify user is admin
    if current_user.user_type_enum != UserTypeEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can upload profile pictures for other teachers"
        )

    # Find teacher record
    teacher = await teacher_crud.get(db, id=teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )

    # Validate file
    await validate_profile_picture(file)

    # Delete old profile picture if exists
    if teacher.profile_picture_cloudinary_id:
        await delete_profile_picture_from_cloudinary(teacher.profile_picture_cloudinary_id)

    # Upload new picture
    cloudinary_url, cloudinary_public_id = await upload_profile_picture_to_cloudinary(
        file=file,
        folder="profiles/teachers",
        identifier=str(teacher.id)
    )

    # Update database
    await update_teacher_profile_picture(
        db=db,
        teacher_id=teacher.id,
        profile_picture_url=cloudinary_url,
        profile_picture_cloudinary_id=cloudinary_public_id
    )

    # Return updated profile
    teacher_with_metadata = await teacher_crud.get_with_metadata(db, id=teacher.id)
    return {
        "message": "Profile picture uploaded successfully",
        "profile_picture_url": cloudinary_url,
        "teacher": teacher_with_metadata
    }


@router.delete("/{teacher_id}/delete-picture", response_model=Dict[str, Any])
async def delete_teacher_profile_picture(
    teacher_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete profile picture for a specific teacher (Admin only)
    """
    from app.utils.profile_picture_helpers import (
        delete_profile_picture_from_cloudinary,
        update_teacher_profile_picture
    )

    # Verify user is admin
    if current_user.user_type_enum != UserTypeEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete profile pictures for other teachers"
        )

    # Find teacher record
    teacher = await teacher_crud.get(db, id=teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )

    # Delete from Cloudinary if exists
    if teacher.profile_picture_cloudinary_id:
        await delete_profile_picture_from_cloudinary(teacher.profile_picture_cloudinary_id)

    # Update database
    await update_teacher_profile_picture(
        db=db,
        teacher_id=teacher.id,
        profile_picture_url=None,
        profile_picture_cloudinary_id=None
    )

    # Return updated profile
    teacher_with_metadata = await teacher_crud.get_with_metadata(db, id=teacher.id)
    return {
        "message": "Profile picture deleted successfully",
        "teacher": teacher_with_metadata
    }
