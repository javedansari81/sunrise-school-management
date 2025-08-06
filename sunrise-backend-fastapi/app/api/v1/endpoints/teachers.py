from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import math
import json
from datetime import datetime

from app.core.database import get_db
from app.crud import teacher_crud
from app.schemas.teacher import (
    Teacher, TeacherCreate, TeacherUpdate, TeacherProfile, TeacherListResponse, TeacherDashboard,
    GenderEnum, QualificationEnum, EmploymentStatusEnum, TeacherProfileUpdate
)
from app.api.deps import get_current_active_user
from app.models.user import User, UserTypeEnum

router = APIRouter()


@router.get("/test-public")
async def test_public_endpoint():
    """
    Simple test endpoint to verify public access works
    """
    return {"message": "Public endpoint is working!", "timestamp": "2025-01-26"}


@router.get("/", response_model=Dict[str, Any])
@router.get("", response_model=Dict[str, Any])  # Handle both with and without trailing slash
async def get_teachers(
    department_filter: Optional[str] = Query(None, description="Filter by department"),
    position_filter: Optional[str] = Query(None, description="Filter by position"),
    qualification_filter: Optional[int] = Query(None, description="Filter by qualification ID"),
    employment_status_filter: Optional[int] = Query(None, description="Filter by employment status ID"),
    search: Optional[str] = Query(None, description="Search by name, employee ID, or email"),
    is_active: bool = Query(True, description="Filter by active status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
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
    # Check if employee ID already exists
    existing_teacher = await teacher_crud.get_by_employee_id(
        db, employee_id=teacher_data.employee_id
    )
    if existing_teacher:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Teacher with this employee ID already exists"
        )

    # Check if email already exists (only if email is provided)
    if teacher_data.email:
        existing_email = await teacher_crud.get_by_email(
            db, email=teacher_data.email
        )
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Teacher with this email already exists"
            )

    # Create teacher with user account
    teacher = await teacher_crud.create_with_user_account(db, obj_in=teacher_data)

    # Return teacher with metadata
    teacher_with_metadata = await teacher_crud.get_with_metadata(db, id=teacher.id)
    return teacher_with_metadata


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


@router.get("/public/faculty", response_model=Dict[str, Any])
async def get_public_faculty(
    db: AsyncSession = Depends(get_db)
):
    """
    Get active teachers for public Faculty page display
    No authentication required - public endpoint
    """
    try:
        # Get only active teachers with basic information for public display
        teachers, total = await teacher_crud.get_multi_with_filters(
            db,
            skip=0,
            limit=100,  # Get up to 100 teachers for faculty page
            is_active=True
        )

        # Filter and format data for public display
        public_teachers = []
        for teacher in teachers:
            # Parse subjects JSON if it exists
            subjects_list = []
            if teacher.get('subjects'):
                try:
                    subjects_list = json.loads(teacher['subjects'])
                except (json.JSONDecodeError, TypeError):
                    subjects_list = []

            # Create public teacher profile
            public_teacher = {
                "id": teacher["id"],
                "full_name": f"{teacher['first_name']} {teacher['last_name']}",
                "first_name": teacher["first_name"],
                "last_name": teacher["last_name"],
                "employee_id": teacher["employee_id"],
                "position": teacher["position"],
                "department": teacher.get("department"),
                "subjects": subjects_list,
                "experience_years": teacher.get("experience_years", 0),
                "qualification_name": teacher.get("qualification_name"),
                "joining_date": teacher.get("joining_date"),
                "email": teacher.get("email"),  # Include email for contact
                "phone": teacher.get("phone"),  # Include phone for contact
                # Note: photo_url, bio, specializations, certifications not available in current schema
            }
            public_teachers.append(public_teacher)

        # Group teachers by department for better organization
        departments = {}
        for teacher in public_teachers:
            dept = teacher.get("department") or "General"
            if dept not in departments:
                departments[dept] = []
            departments[dept].append(teacher)

        return {
            "teachers": public_teachers,
            "departments": departments,
            "total": len(public_teachers),
            "message": "Faculty information retrieved successfully"
        }

    except Exception as e:
        # Log the error for debugging
        print(f"Error in get_public_faculty: {str(e)}")
        return {
            "teachers": [],
            "departments": {},
            "total": 0,
            "error": str(e),
            "message": "Failed to retrieve faculty information"
        }


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


@router.get("/options/departments")
async def get_departments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all available departments
    """
    departments = await teacher_crud.get_departments(db)
    return {"departments": departments}


@router.get("/options/positions")
async def get_positions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all available positions
    """
    positions = await teacher_crud.get_positions(db)
    return {"positions": positions}


@router.get("/options/qualifications")
async def get_qualifications():
    """
    Get all available qualifications
    """
    return {"qualifications": [qual.value for qual in QualificationEnum]}


@router.get("/options/employment-status")
async def get_employment_status():
    """
    Get all available employment status options
    """
    return {"employment_status": [status.value for status in EmploymentStatusEnum]}
