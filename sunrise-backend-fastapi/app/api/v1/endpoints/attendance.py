from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime
import math

from app.core.database import get_db
from app.crud.crud_attendance import attendance_record_crud
from app.crud import student_crud, teacher_crud
from app.schemas.attendance import (
    AttendanceRecord, AttendanceRecordCreate, AttendanceRecordUpdate,
    AttendanceFilters, AttendanceListResponse,
    BulkAttendanceCreate, StudentAttendanceSummary,
    ClassAttendanceSummary, AttendanceStatistics
)
from app.schemas.user import UserTypeEnum
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()


# ============================================
# Main Listing Endpoint
# ============================================

@router.get("/", response_model=AttendanceListResponse)
@router.get("", response_model=AttendanceListResponse)
async def get_attendance_records(
    attendance_date: Optional[date] = Query(None, description="Filter by specific date"),
    from_date: Optional[date] = Query(None, description="Filter from date"),
    to_date: Optional[date] = Query(None, description="Filter to date"),
    class_id: Optional[int] = Query(None, description="Filter by class ID"),
    student_id: Optional[int] = Query(None, description="Filter by student ID"),
    attendance_status_id: Optional[int] = Query(None, description="Filter by status"),
    session_year_id: int = Query(4, description="Session year ID (default: 2025-26)"),
    search: Optional[str] = Query(None, description="Search by student name or roll number"),
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get attendance records with comprehensive filters
    
    Supports filtering by:
    - Specific date or date range
    - Class, student, status
    - Session year
    - Search by student name/roll number
    """
    filters = AttendanceFilters(
        attendance_date=attendance_date,
        from_date=from_date,
        to_date=to_date,
        class_id=class_id,
        student_id=student_id,
        attendance_status_id=attendance_status_id,
        session_year_id=session_year_id,
        search=search
    )
    
    skip = (page - 1) * per_page
    records, total = await attendance_record_crud.get_multi_with_filters(
        db, filters=filters, skip=skip, limit=per_page
    )
    
    total_pages = math.ceil(total / per_page) if total > 0 else 0
    
    return AttendanceListResponse(
        records=records,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


# ============================================
# Student Self-Service Endpoints (Must come before /{id} routes)
# ============================================

@router.get("/my-attendance", response_model=AttendanceListResponse)
async def get_my_attendance(
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month (1-12)"),
    year: Optional[int] = Query(None, ge=2020, le=2100, description="Filter by year"),
    from_date: Optional[date] = Query(None, description="Filter from date"),
    to_date: Optional[date] = Query(None, description="Filter to date"),
    session_year_id: int = Query(4, description="Session year ID (default: 2025-26)"),
    page: int = Query(1, ge=1),
    per_page: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get attendance records for the currently logged-in student

    Students can only view their own attendance records.
    Supports filtering by:
    - Month and year (for calendar view)
    - Date range
    - Session year
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

    # Calculate date range if month/year provided
    calculated_from_date = from_date
    calculated_to_date = to_date

    if month and year:
        # Calculate first and last day of the month
        from datetime import date as date_class
        import calendar

        calculated_from_date = date_class(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        calculated_to_date = date_class(year, month, last_day)

    # Build filters with student_id
    filters = AttendanceFilters(
        student_id=student.id,
        from_date=calculated_from_date,
        to_date=calculated_to_date,
        session_year_id=session_year_id
    )

    skip = (page - 1) * per_page
    records, total = await attendance_record_crud.get_multi_with_filters(
        db, filters=filters, skip=skip, limit=per_page
    )

    total_pages = math.ceil(total / per_page) if total > 0 else 0

    return AttendanceListResponse(
        records=records,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.get("/my-attendance/summary", response_model=StudentAttendanceSummary)
async def get_my_attendance_summary(
    session_year_id: int = Query(4, description="Session year ID"),
    from_date: Optional[date] = Query(None, description="Filter from date"),
    to_date: Optional[date] = Query(None, description="Filter to date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get attendance summary for the currently logged-in student

    Returns:
    - Total school days
    - Days present, absent, late, half-day, excused
    - Attendance percentage
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

    summary = await attendance_record_crud.get_student_summary(
        db,
        student_id=student.id,
        session_year_id=session_year_id,
        from_date=from_date,
        to_date=to_date
    )

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No attendance records found"
        )

    return summary


# ============================================
# Individual Record Endpoints
# ============================================

@router.post("/", response_model=AttendanceRecord, status_code=status.HTTP_201_CREATED)
async def create_attendance_record(
    attendance_data: AttendanceRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create single attendance record"""
    try:
        record = await attendance_record_crud.create(
            db, obj_in=attendance_data.model_dump(), marked_by=current_user.id
        )
        
        # Fetch with details
        detailed_record = await attendance_record_crud.get_with_details(db, id=record.id)
        return detailed_record
        
    except Exception as e:
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attendance record already exists for this student on this date"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating attendance record: {str(e)}"
        )


@router.get("/{id}", response_model=AttendanceRecord)
async def get_attendance_record(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get specific attendance record"""
    record = await attendance_record_crud.get_with_details(db, id=id)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    
    return record


@router.put("/{id}", response_model=AttendanceRecord)
async def update_attendance_record(
    id: int,
    attendance_data: AttendanceRecordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update attendance record"""
    record = await attendance_record_crud.get(db, id=id)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    
    updated_record = await attendance_record_crud.update(
        db, db_obj=record, obj_in=attendance_data.model_dump(exclude_unset=True)
    )
    
    # Fetch with details
    detailed_record = await attendance_record_crud.get_with_details(db, id=updated_record.id)
    return detailed_record


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attendance_record(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete attendance record"""
    record = await attendance_record_crud.get(db, id=id)

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )

    await attendance_record_crud.remove(db, id=id)
    return None


# ============================================
# Bulk Operations
# ============================================

@router.post("/bulk", response_model=dict)
async def create_bulk_attendance(
    attendance_data: BulkAttendanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mark attendance for multiple students at once

    This endpoint allows marking attendance for an entire class in one request.
    It will create new records or update existing ones for the given date.
    """
    result = await attendance_record_crud.create_bulk(
        db, bulk_data=attendance_data, marked_by=current_user.id
    )

    return {
        "message": "Bulk attendance processed successfully",
        "created": result["created"],
        "updated": result["updated"],
        "total_processed": result["total_processed"],
        "errors": result["errors"]
    }


# ============================================
# Student-Specific Endpoints
# ============================================

@router.get("/student/{student_id}/summary", response_model=StudentAttendanceSummary)
async def get_student_attendance_summary(
    student_id: int,
    session_year_id: int = Query(4, description="Session year ID"),
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get attendance summary for specific student

    Returns:
    - Total school days
    - Days present, absent, late, half-day, excused
    - Attendance percentage
    """
    summary = await attendance_record_crud.get_student_summary(
        db,
        student_id=student_id,
        session_year_id=session_year_id,
        from_date=from_date,
        to_date=to_date
    )

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No attendance records found for this student"
        )

    return summary


# ============================================
# Class-Specific Endpoints
# ============================================

@router.get("/class/{class_id}/date/{attendance_date}")
async def get_class_attendance_by_date(
    class_id: int,
    attendance_date: date,
    session_year_id: int = Query(4, description="Session year ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get attendance for entire class on specific date

    Returns list of all students in the class with their attendance status.
    Students without attendance records will show as null status.
    """
    records = await attendance_record_crud.get_class_attendance_by_date(
        db,
        class_id=class_id,
        attendance_date=attendance_date,
        session_year_id=session_year_id
    )

    return {
        "class_id": class_id,
        "attendance_date": attendance_date,
        "session_year_id": session_year_id,
        "students": records,
        "total_students": len(records),
        "marked_count": sum(1 for r in records if r.get("attendance_record_id") is not None)
    }


# ============================================
# Statistics and Reports
# ============================================

@router.get("/statistics/summary", response_model=AttendanceStatistics)
async def get_attendance_statistics(
    class_id: Optional[int] = Query(None, description="Filter by class ID"),
    from_date: Optional[date] = Query(None, description="Filter from date"),
    to_date: Optional[date] = Query(None, description="Filter to date"),
    session_year_id: int = Query(4, description="Session year ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get attendance statistics based on filters

    Returns:
    - Total records
    - Total present, absent, late
    - Overall attendance percentage
    """
    filters = AttendanceFilters(
        class_id=class_id,
        from_date=from_date,
        to_date=to_date,
        session_year_id=session_year_id
    )

    stats = await attendance_record_crud.get_attendance_statistics(db, filters=filters)

    # Build date range string
    date_range = "All time"
    if from_date and to_date:
        date_range = f"{from_date} to {to_date}"
    elif from_date:
        date_range = f"From {from_date}"
    elif to_date:
        date_range = f"Until {to_date}"

    return AttendanceStatistics(
        total_records=stats.get("total_records", 0),
        total_present=stats.get("total_present", 0),
        total_absent=stats.get("total_absent", 0),
        total_late=stats.get("total_late", 0),
        overall_attendance_percentage=stats.get("overall_attendance_percentage", 0.0),
        date_range=date_range
    )
