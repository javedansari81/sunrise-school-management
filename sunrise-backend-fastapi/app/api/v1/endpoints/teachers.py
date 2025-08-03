from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import math
import json

from app.core.database import get_db
from app.crud import teacher_crud
from app.schemas.teacher import (
    Teacher, TeacherCreate, TeacherUpdate, TeacherProfile, TeacherListResponse, TeacherDashboard,
    GenderEnum, QualificationEnum, EmploymentStatusEnum
)
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=TeacherListResponse)
@router.get("", response_model=TeacherListResponse)  # Handle both with and without trailing slash
async def get_teachers(
    department_filter: Optional[str] = Query(None, description="Filter by department"),
    position_filter: Optional[str] = Query(None, description="Filter by position"),
    qualification_filter: Optional[str] = Query(None, description="Filter by qualification"),
    employment_status_filter: Optional[str] = Query(None, description="Filter by employment status"),
    search: Optional[str] = Query(None, description="Search by name, employee ID, or email"),
    is_active: bool = Query(True, description="Filter by active status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all teachers with comprehensive filters
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

    return TeacherListResponse(
        teachers=teachers,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.post("/", response_model=Teacher)
@router.post("", response_model=Teacher)  # Handle both with and without trailing slash
async def create_teacher(
    teacher_data: TeacherCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new teacher
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

    # Check if email already exists
    existing_email = await teacher_crud.get_by_email(
        db, email=teacher_data.email
    )
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Teacher with this email already exists"
        )

    teacher = await teacher_crud.create(db, obj_in=teacher_data)
    return teacher


@router.get("/{teacher_id}", response_model=TeacherProfile)
async def get_teacher(
    teacher_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get teacher by ID with complete profile
    """
    teacher = await teacher_crud.get(db, id=teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )

    # Parse JSON fields
    subjects_list = []
    specializations_list = []
    certifications_list = []

    try:
        if teacher.subjects:
            subjects_list = json.loads(teacher.subjects)
    except (json.JSONDecodeError, TypeError):
        subjects_list = []

    try:
        if teacher.specializations:
            specializations_list = json.loads(teacher.specializations)
    except (json.JSONDecodeError, TypeError):
        specializations_list = []

    try:
        if teacher.certifications:
            certifications_list = json.loads(teacher.certifications)
    except (json.JSONDecodeError, TypeError):
        certifications_list = []

    # Create response with parsed lists
    teacher_dict = teacher.__dict__.copy()
    teacher_dict['subjects_list'] = subjects_list
    teacher_dict['specializations_list'] = specializations_list
    teacher_dict['certifications_list'] = certifications_list

    return teacher_dict


@router.put("/{teacher_id}", response_model=Teacher)
async def update_teacher(
    teacher_id: int,
    teacher_data: TeacherUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update teacher by ID
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
    return updated_teacher


@router.delete("/{teacher_id}")
async def delete_teacher(
    teacher_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Deactivate teacher by ID (soft delete)
    """
    teacher = await teacher_crud.get(db, id=teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )

    # Soft delete by setting is_active to False
    deactivated_teacher = await teacher_crud.remove(db, id=teacher_id)
    return {"message": "Teacher deactivated successfully", "teacher_id": teacher_id}


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
