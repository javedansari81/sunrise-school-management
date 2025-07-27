from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
import math

from app.core.database import get_db
from app.crud import leave_request_crud, student_crud
from app.schemas.leave import (
    LeaveRequest, LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestWithStudent,
    LeaveApproval, LeaveFilters, LeaveListResponse, LeaveReport,
    LeaveStatusEnum, LeaveTypeEnum
)
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=LeaveListResponse)
async def get_leave_requests(
    student_id: Optional[int] = None,
    leave_type: Optional[LeaveTypeEnum] = None,
    status: Optional[LeaveStatusEnum] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    class_name: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get leave requests with comprehensive filters
    """
    filters = LeaveFilters(
        student_id=student_id,
        leave_type=leave_type,
        status=status,
        from_date=from_date,
        to_date=to_date,
        class_name=class_name
    )

    skip = (page - 1) * per_page
    leaves, total = await leave_request_crud.get_multi_with_filters(
        db, filters=filters, skip=skip, limit=per_page
    )

    # Convert to response format with student details
    leave_list = []
    for leave in leaves:
        leave_dict = {
            **leave.__dict__,
            "student_name": f"{leave.student.first_name} {leave.student.last_name}",
            "student_admission_number": leave.student.admission_number,
            "student_class": leave.student.current_class,
            "approver_name": f"{leave.approver.first_name} {leave.approver.last_name}" if leave.approver else None
        }
        leave_list.append(leave_dict)

    total_pages = math.ceil(total / per_page)

    return LeaveListResponse(
        leaves=leave_list,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.post("/", response_model=LeaveRequest)
async def create_leave_request(
    leave_data: LeaveRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new leave request
    """
    # Verify student exists
    student = await student_crud.get(db, id=leave_data.student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Validate dates
    if leave_data.start_date > leave_data.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be after end date"
        )

    # Calculate total days
    total_days = (leave_data.end_date - leave_data.start_date).days + 1
    leave_data.total_days = total_days

    leave_request = await leave_request_crud.create(db, obj_in=leave_data)
    return leave_request


@router.get("/{leave_id}", response_model=LeaveRequest)
async def get_leave_request(
    leave_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get specific leave request details
    """
    leave_request = await leave_request_crud.get_with_student(db, id=leave_id)
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
    if leave_request.status != LeaveStatusEnum.PENDING:
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

    # Only allow approval/rejection if status is pending
    if leave_request.status != LeaveStatusEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave request is not pending"
        )

    # Validate rejection reason if rejecting
    if approval_data.status == LeaveStatusEnum.REJECTED and not approval_data.rejection_reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rejection reason is required when rejecting a leave request"
        )

    updated_leave = await leave_request_crud.approve_request(
        db,
        leave_request=leave_request,
        approver_id=current_user.id,
        status=approval_data.status,
        rejection_reason=approval_data.rejection_reason
    )

    return updated_leave


@router.get("/student/{student_id}")
async def get_student_leave_history(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get leave history for a specific student
    """
    # Verify student exists
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Get leave history
    leave_history = await leave_request_crud.get_by_student(db, student_id=student_id)

    # Calculate summary
    total_leaves = len(leave_history)
    pending_requests = len([l for l in leave_history if l.status == LeaveStatusEnum.PENDING])
    approved_leaves = len([l for l in leave_history if l.status == LeaveStatusEnum.APPROVED])
    total_days_taken = sum(l.total_days for l in leave_history if l.status == LeaveStatusEnum.APPROVED)

    return {
        "student_id": student_id,
        "student_name": f"{student.first_name} {student.last_name}",
        "admission_number": student.admission_number,
        "current_class": student.current_class,
        "leave_history": leave_history,
        "summary": {
            "total_requests": total_leaves,
            "pending_requests": pending_requests,
            "approved_leaves": approved_leaves,
            "rejected_leaves": total_leaves - pending_requests - approved_leaves,
            "total_days_taken": total_days_taken
        }
    }


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


@router.get("/pending")
async def get_pending_leave_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all pending leave requests for approval
    """
    pending_requests = await leave_request_crud.get_pending_requests(db)

    # Convert to response format with student details
    pending_list = []
    for leave in pending_requests:
        leave_dict = {
            **leave.__dict__,
            "student_name": f"{leave.student.first_name} {leave.student.last_name}",
            "student_admission_number": leave.student.admission_number,
            "student_class": leave.student.current_class
        }
        pending_list.append(leave_dict)

    return {
        "pending_requests": pending_list,
        "total_pending": len(pending_list)
    }
