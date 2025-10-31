from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import math
import logging

from app.core.database import get_db
from app.crud import report_crud
from app.schemas.report import (
    UDISEReportResponse, StudentUDISEData,
    FeeTrackingReportResponse, FeeTrackingData
)
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/student-udise", response_model=UDISEReportResponse)
async def get_student_udise_report(
    session_year_id: Optional[int] = Query(None, description="Filter by session year ID"),
    class_id: Optional[int] = Query(None, description="Filter by class ID"),
    section: Optional[str] = Query(None, description="Filter by section"),
    gender_id: Optional[int] = Query(None, description="Filter by gender ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by name, admission number, or parent name"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(25, ge=1, le=100, description="Records per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get Student UDISE Report with comprehensive student information
    
    This endpoint provides detailed student data for UDISE (Unified District Information System for Education) reporting.
    Includes personal, academic, contact, parent/guardian, and emergency contact information.
    
    **Filters:**
    - session_year_id: Filter by specific session year
    - class_id: Filter by specific class
    - section: Filter by specific section
    - gender_id: Filter by gender
    - is_active: Filter by active/inactive status
    - search: Search across name, admission number, parent names
    
    **Pagination:**
    - page: Page number (default: 1)
    - per_page: Records per page (default: 25, max: 100)
    
    **Returns:**
    - List of students with all UDISE-required fields
    - Total count and pagination metadata
    - Summary statistics (gender breakdown, class breakdown, etc.)
    """
    logger.info(f"=== Student UDISE Report Request ===")
    logger.info(f"Filters: session_year={session_year_id}, class={class_id}, section={section}, "
                f"gender={gender_id}, is_active={is_active}, search={search}")
    logger.info(f"Pagination: page={page}, per_page={per_page}")
    
    try:
        # Get report data from CRUD
        students_data, total = await report_crud.get_udise_report_data(
            db,
            session_year_id=session_year_id,
            class_id=class_id,
            section=section,
            gender_id=gender_id,
            is_active=is_active,
            search=search,
            page=page,
            per_page=per_page
        )
        
        # Calculate pagination metadata
        total_pages = math.ceil(total / per_page) if total > 0 else 0
        
        # Calculate summary statistics
        summary = {
            "total_students": total,
            "active_students": sum(1 for s in students_data if s.get("is_active", False)),
            "inactive_students": sum(1 for s in students_data if not s.get("is_active", False)),
            "male_students": sum(1 for s in students_data if s.get("gender_name", "").lower() == "male"),
            "female_students": sum(1 for s in students_data if s.get("gender_name", "").lower() == "female"),
        }
        
        # Convert to Pydantic models
        students = [StudentUDISEData(**data) for data in students_data]
        
        logger.info(f"Successfully retrieved {len(students)} students out of {total} total")
        
        return UDISEReportResponse(
            students=students,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"Error generating UDISE report: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate UDISE report: {str(e)}"
        )


@router.get("/fee-tracking", response_model=FeeTrackingReportResponse)
async def get_fee_tracking_report(
    session_year_id: int = Query(..., description="Session year ID (required)"),
    class_id: Optional[int] = Query(None, description="Filter by class ID"),
    section: Optional[str] = Query(None, description="Filter by section"),
    payment_status: Optional[str] = Query(None, description="Filter by payment status (paid/partial/pending)"),
    transport_opted: Optional[bool] = Query(None, description="Filter by transport opted (true/false)"),
    pending_only: bool = Query(False, description="Show only students with pending fees"),
    search: Optional[str] = Query(None, description="Search by name or admission number"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(25, ge=1, le=100, description="Records per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get Fee Tracking Report with fee and transport payment details
    
    This endpoint provides comprehensive fee tracking information for students, including:
    - Regular fee payment status and amounts
    - Transport service enrollment and payment details
    - Combined totals and collection rates
    
    **Required Parameters:**
    - session_year_id: Session year for which to generate the report
    
    **Optional Filters:**
    - class_id: Filter by specific class
    - section: Filter by specific section
    - payment_status: Filter by fee payment status (paid/partial/pending)
    - transport_opted: Filter by transport enrollment (true/false)
    - pending_only: Show only students with pending fees
    - search: Search across student name, admission number
    
    **Pagination:**
    - page: Page number (default: 1)
    - per_page: Records per page (default: 25, max: 100)
    
    **Returns:**
    - List of students with fee and transport payment details
    - Total count and pagination metadata
    - Summary statistics (total amounts, collection rates, etc.)
    """
    logger.info(f"=== Fee Tracking Report Request ===")
    logger.info(f"Session Year: {session_year_id}")
    logger.info(f"Filters: class={class_id}, section={section}, payment_status={payment_status}, "
                f"transport_opted={transport_opted}, pending_only={pending_only}, search={search}")
    logger.info(f"Pagination: page={page}, per_page={per_page}")
    
    try:
        # Get report data from CRUD
        records_data, total, summary = await report_crud.get_fee_tracking_report_data(
            db,
            session_year_id=session_year_id,
            class_id=class_id,
            section=section,
            payment_status=payment_status,
            transport_opted=transport_opted,
            pending_only=pending_only,
            search=search,
            page=page,
            per_page=per_page
        )
        
        # Calculate pagination metadata
        total_pages = math.ceil(total / per_page) if total > 0 else 0
        
        # Convert Decimal to string for JSON serialization
        summary_serialized = {
            "total_students": summary["total_students"],
            "total_fee_amount": str(summary["total_fee_amount"]),
            "total_paid_amount": str(summary["total_paid_amount"]),
            "total_pending_amount": str(summary["total_pending_amount"]),
            "overall_collection_rate": round(summary["overall_collection_rate"], 2),
            "students_with_transport": summary["students_with_transport"],
            "transport_total_amount": str(summary["transport_total_amount"]),
            "transport_paid_amount": str(summary["transport_paid_amount"]),
            "transport_pending_amount": str(summary["transport_pending_amount"]),
        }
        
        # Convert to Pydantic models
        records = [FeeTrackingData(**data) for data in records_data]
        
        logger.info(f"Successfully retrieved {len(records)} records out of {total} total")
        logger.info(f"Summary: {summary_serialized}")
        
        return FeeTrackingReportResponse(
            records=records,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            summary=summary_serialized
        )
        
    except Exception as e:
        logger.error(f"Error generating fee tracking report: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate fee tracking report: {str(e)}"
        )

