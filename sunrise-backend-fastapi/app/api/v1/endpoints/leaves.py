from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
import math

from app.core.database import get_db
from app.crud.crud_leave import leave_request_crud, leave_balance_crud, leave_policy_crud
from app.crud import student_crud, teacher_crud
from app.schemas.leave import (
    LeaveRequest, LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestWithDetails,
    LeaveApproval, LeaveFilters, LeaveListResponse, LeaveReport,
    ApplicantTypeEnum, LeaveBalanceResponse, LeavePolicyResponse
)
from app.utils.identifier_helpers import (
    format_student_identifier, format_teacher_identifier
)
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=LeaveListResponse)
@router.get("", response_model=LeaveListResponse)  # Handle both with and without trailing slash
async def get_leave_requests(
    applicant_id: Optional[int] = None,
    applicant_type: Optional[ApplicantTypeEnum] = None,
    leave_type_id: Optional[int] = None,
    leave_status_id: Optional[int] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    class_name: Optional[str] = None,
    department: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get leave requests with comprehensive filters for both students and teachers
    """
    filters = LeaveFilters(
        applicant_id=applicant_id,
        applicant_type=applicant_type,
        leave_type_id=leave_type_id,
        leave_status_id=leave_status_id,
        from_date=from_date,
        to_date=to_date,
        class_name=class_name,
        department=department
    )

    skip = (page - 1) * per_page
    leaves, total = await leave_request_crud.get_multi_with_filters(
        db, filters=filters, skip=skip, limit=per_page
    )

    total_pages = math.ceil(total / per_page)

    return LeaveListResponse(
        leaves=leaves,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.post("/", response_model=LeaveRequest)
@router.post("", response_model=LeaveRequest)  # Handle both with and without trailing slash
async def create_leave_request(
    leave_data: LeaveRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new leave request for students or teachers
    """
    # Verify applicant exists
    if leave_data.applicant_type == ApplicantTypeEnum.STUDENT:
        applicant = await student_crud.get(db, id=leave_data.applicant_id)
        if not applicant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
    elif leave_data.applicant_type == ApplicantTypeEnum.TEACHER:
        applicant = await teacher_crud.get(db, id=leave_data.applicant_id)
        if not applicant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found"
            )

    # Validate dates
    if leave_data.start_date > leave_data.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be after end date"
        )

    # Calculate total days if not provided
    if not leave_data.total_days:
        total_days = (leave_data.end_date - leave_data.start_date).days + 1
        leave_data.total_days = total_days

    # Create leave request with user_id and applied_by set to current user
    # Only include fields that exist in the database model
    leave_dict = {
        'user_id': current_user.id,
        'applied_by': current_user.id,
        'leave_type_id': leave_data.leave_type_id,
        'start_date': leave_data.start_date,
        'end_date': leave_data.end_date,
        'total_days': leave_data.total_days,
        'reason': leave_data.reason,
        'applicant_type': leave_data.applicant_type.value,
        'applicant_id': leave_data.applicant_id,
        'is_half_day': leave_data.is_half_day,
        'half_day_period': leave_data.half_day_period,
        'medical_certificate_url': leave_data.medical_certificate_url,
        'emergency_contact': leave_data.emergency_contact,
    }

    leave_request = await leave_request_crud.create(db, obj_in=leave_dict)
    return leave_request


# Routes with path parameters moved to end to avoid conflicts with specific routes


@router.get("/pending", response_model=List[LeaveRequestWithDetails])
async def get_pending_leave_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all pending leave requests for approval
    """
    pending_leaves = await leave_request_crud.get_pending_requests(db)
    return pending_leaves


@router.get("/applicant/{applicant_type}/{applicant_id}", response_model=List[LeaveRequestWithDetails])
async def get_leave_requests_by_applicant(
    applicant_type: ApplicantTypeEnum,
    applicant_id: int,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get leave requests for a specific applicant (student or teacher)
    """
    leaves = await leave_request_crud.get_by_applicant(
        db, applicant_id=applicant_id, applicant_type=applicant_type, limit=limit
    )
    return leaves


@router.get("/statistics", response_model=dict)
async def get_leave_statistics(
    year: Optional[int] = Query(None, description="Year for statistics"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get leave management statistics
    """
    stats = await leave_request_crud.get_leave_statistics(db, year=year)
    return stats


@router.get("/reports/summary")
async def get_leave_summary_report(
    year: Optional[int] = Query(None, description="Year for the report"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get comprehensive leave summary report
    """
    # Get leave statistics
    stats = await leave_request_crud.get_leave_statistics(db, year=year)

    # Get monthly trend if year is specified
    monthly_trend = []
    if year:
        monthly_trend = await leave_request_crud.get_monthly_leave_trend(db, year=year)

    # Get class-wise breakdown
    class_wise_stats = await leave_request_crud.get_class_wise_leave_stats(db, year=year)

    # Get pending requests
    pending_requests = await leave_request_crud.get_pending_requests(db)

    return {
        "year": year or "All Time",
        "summary": {
            "total_requests": stats['total_requests'],
            "approved_requests": stats['approved_requests'],
            "rejected_requests": stats['rejected_requests'],
            "pending_requests": stats['pending_requests'],
            "total_days": stats['total_days'],
            "approval_rate": stats['approval_rate']
        },
        "leave_type_breakdown": stats['leave_type_breakdown'],
        "class_wise_breakdown": class_wise_stats,
        "monthly_trend": monthly_trend,
        "pending_requests_count": len(pending_requests)
    }





@router.get("/applicants/{applicant_type}")
async def get_available_applicants(
    applicant_type: ApplicantTypeEnum,
    search: Optional[str] = Query(None, description="Search by name or identifier"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get available applicants (students or teachers) with their human-readable identifiers

    This endpoint returns a list of applicants with their identifiers that can be used
    in the friendly leave request creation endpoint.
    """
    applicants = []

    if applicant_type == ApplicantTypeEnum.STUDENT:
        if search:
            students = await student_crud.search_students(db, search_term=search, limit=limit)
        else:
            students, _ = await student_crud.get_multi_with_filters(
                db, skip=0, limit=limit, is_active=True
            )

        for student in students:
            applicants.append({
                "identifier": format_student_identifier(student),
                "name": f"{student.first_name} {student.last_name}",
                "details": f"Class {getattr(student, 'current_class', 'N/A')} - {getattr(student, 'section', 'N/A')}",
                "type": "student",
                "legacy_identifier": getattr(student, 'admission_number', 'N/A'),
                "roll_number": getattr(student, 'roll_number', 'N/A')
            })

    elif applicant_type == ApplicantTypeEnum.TEACHER:
        if search:
            teachers = await teacher_crud.search_teachers(db, search_term=search, limit=limit)
        else:
            teachers, _ = await teacher_crud.get_multi_with_filters(
                db, skip=0, limit=limit, is_active=True
            )

        for teacher in teachers:
            applicants.append({
                "identifier": format_teacher_identifier(teacher),
                "name": f"{teacher.first_name} {teacher.last_name}",
                "details": f"{getattr(teacher, 'department', 'N/A')}",
                "type": "teacher",
                "legacy_identifier": teacher.employee_id
            })

    return {
        "applicant_type": applicant_type,
        "applicants": applicants,
        "total_found": len(applicants),
        "search_term": search
    }


@router.get("/{leave_id}", response_model=LeaveRequestWithDetails)
async def get_leave_request(
    leave_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get specific leave request details with all related information
    """
    leave_request = await leave_request_crud.get_with_details(db, id=leave_id)
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )

    return leave_request


@router.put("/{leave_id}", response_model=LeaveRequest)
async def update_leave_request(
    leave_id: int,
    leave_data: LeaveRequestUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update leave request (only if pending)
    """
    leave_request = await leave_request_crud.get(db, id=leave_id)
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )

    # Only allow updates if status is pending
    if leave_request.leave_status_id != 1:  # Not pending
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update leave request that is not pending"
        )

    # Validate dates if provided
    start_date = leave_data.start_date or leave_request.start_date
    end_date = leave_data.end_date or leave_request.end_date

    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be after end date"
        )

    # Update total days if dates changed
    if leave_data.start_date or leave_data.end_date:
        leave_data.total_days = (end_date - start_date).days + 1

    updated_leave = await leave_request_crud.update(
        db, db_obj=leave_request, obj_in=leave_data
    )
    return updated_leave


@router.delete("/{leave_id}")
async def delete_leave_request(
    leave_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a leave request (only allowed for pending requests)
    """
    leave_request = await leave_request_crud.get(db, id=leave_id)
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )

    # Only allow deletion for pending requests
    if leave_request.leave_status_id != 1:  # Not pending
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only delete pending leave requests"
        )

    await leave_request_crud.remove(db, id=leave_id)
    return {"message": "Leave request deleted successfully"}


@router.patch("/{leave_id}/approve", response_model=LeaveRequest)
async def approve_leave_request(
    leave_id: int,
    approval_data: LeaveApproval,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Approve or reject a leave request
    """
    leave_request = await leave_request_crud.get(db, id=leave_id)
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )

    # Check if already processed
    if leave_request.leave_status_id != 1:  # Not pending
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave request has already been processed"
        )

    updated_leave = await leave_request_crud.approve_request(
        db,
        leave_request=leave_request,
        reviewer_id=current_user.id,
        leave_status_id=approval_data.leave_status_id,
        review_comments=approval_data.approval_comments
    )

    return updated_leave
