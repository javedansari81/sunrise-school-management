"""
Transport Management API Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime
from decimal import Decimal
import calendar

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.transport import TransportType, TransportDistanceSlab
from app.crud.crud_transport import transport_enrollment_crud, transport_monthly_tracking_crud
from app.schemas.transport import (
    TransportTypeResponse, TransportDistanceSlabResponse,
    StudentTransportEnrollmentCreate, StudentTransportEnrollmentResponse,
    StudentTransportEnrollmentUpdate, EnhancedStudentTransportSummary,
    EnableTransportMonthlyTrackingRequest, StudentTransportMonthlyHistory,
    TransportPaymentRequest
)
from sqlalchemy import select

router = APIRouter()


# =====================================================
# Transport Types Endpoints
# =====================================================

@router.get("/transport-types", response_model=List[TransportTypeResponse])
async def get_transport_types(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all active transport types"""
    result = await db.execute(
        select(TransportType).where(TransportType.is_active == True)
    )
    transport_types = result.scalars().all()
    return transport_types


@router.get("/distance-slabs/{transport_type_id}", response_model=List[TransportDistanceSlabResponse])
async def get_distance_slabs(
    transport_type_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get distance slabs for a transport type"""
    result = await db.execute(
        select(TransportDistanceSlab)
        .where(
            TransportDistanceSlab.transport_type_id == transport_type_id,
            TransportDistanceSlab.is_active == True
        )
        .order_by(TransportDistanceSlab.distance_from_km)
    )
    slabs = result.scalars().all()
    return slabs


# =====================================================
# Student Enrollment Endpoints
# =====================================================

@router.post("/enroll", response_model=StudentTransportEnrollmentResponse)
async def enroll_student(
    enrollment_data: StudentTransportEnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Enroll a student in transport service
    Admin creates enrollment with transport type, distance, and calculated fee
    """
    try:
        # Check if student already has active enrollment
        existing = await transport_enrollment_crud.get_active_enrollment(
            db, enrollment_data.student_id, enrollment_data.session_year_id
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student already has an active transport enrollment for this session"
            )
        
        # Create enrollment
        enrollment = await transport_enrollment_crud.create_enrollment(db, enrollment_data)
        
        return enrollment
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enrolling student: {str(e)}"
        )


@router.put("/enrollment/{enrollment_id}", response_model=StudentTransportEnrollmentResponse)
async def update_enrollment(
    enrollment_id: int,
    enrollment_data: StudentTransportEnrollmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update transport enrollment"""
    enrollment = await transport_enrollment_crud.update_enrollment(
        db, enrollment_id, enrollment_data
    )
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    return enrollment


@router.post("/discontinue/{enrollment_id}")
async def discontinue_enrollment(
    enrollment_id: int,
    discontinue_date: date = Query(..., description="Date to discontinue service"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Discontinue transport service for a student"""
    enrollment = await transport_enrollment_crud.discontinue_enrollment(
        db, enrollment_id, discontinue_date
    )
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    return {
        "success": True,
        "message": "Transport service discontinued successfully",
        "enrollment_id": enrollment_id,
        "discontinue_date": discontinue_date
    }


# =====================================================
# Transport Summary and Listing
# =====================================================

@router.get("/students", response_model=List[EnhancedStudentTransportSummary])
async def get_transport_students(
    session_year: str = Query(..., description="Session year (e.g., 2025-26)"),
    class_id: Optional[int] = Query(None, description="Filter by class ID"),
    is_enrolled: Optional[bool] = Query(None, description="Filter by enrollment status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all students with transport enrollment status
    Supports filtering by class and enrollment status
    """
    try:
        summaries = await transport_enrollment_crud.get_enhanced_transport_summary(
            db, session_year, class_id, is_enrolled
        )
        return summaries
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching transport students: {str(e)}"
        )


# =====================================================
# Monthly Tracking Endpoints
# =====================================================

@router.post("/enable-monthly-tracking")
async def enable_monthly_tracking(
    request: EnableTransportMonthlyTrackingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Enable monthly tracking for transport enrollments
    Creates 12 monthly records with service enabled/disabled based on enrollment date
    """
    try:
        results = []
        
        for enrollment_id in request.enrollment_ids:
            records_created = await transport_monthly_tracking_crud.enable_monthly_tracking(
                db, enrollment_id, request.start_month, request.start_year
            )
            results.append({
                "enrollment_id": enrollment_id,
                "records_created": records_created
            })
        
        return {
            "success": True,
            "message": f"Monthly tracking enabled for {len(request.enrollment_ids)} enrollments",
            "results": results
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enabling monthly tracking: {str(e)}"
        )


@router.get("/monthly-history/{student_id}", response_model=StudentTransportMonthlyHistory)
async def get_monthly_history(
    student_id: int,
    session_year_id: int = Query(..., description="Session year ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get monthly transport history for a student"""
    history = await transport_monthly_tracking_crud.get_monthly_history(
        db, student_id, session_year_id
    )
    
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No transport enrollment found for this student"
        )
    
    return history


# =====================================================
# Payment Endpoints
# =====================================================

@router.post("/pay-monthly/{student_id}")
async def pay_monthly_transport(
    student_id: int,
    payment_data: TransportPaymentRequest,
    session_year_id: int = Query(..., description="Session year ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Process monthly transport payment
    Similar to fee payment system - distributes payment across selected months
    """
    try:
        # Get active enrollment
        enrollment = await transport_enrollment_crud.get_active_enrollment(
            db, student_id, session_year_id
        )
        
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active transport enrollment found for this student"
            )
        
        # Get monthly tracking records for selected months
        # Query by student_id and session_year_id (not enrollment_id) to handle re-enrollment
        # The records should be linked to the current active enrollment after re-enrollment
        from app.models.transport import TransportMonthlyTracking
        result = await db.execute(
            select(TransportMonthlyTracking)
            .where(
                TransportMonthlyTracking.student_id == student_id,
                TransportMonthlyTracking.session_year_id == session_year_id,
                TransportMonthlyTracking.academic_month.in_(payment_data.selected_months),
                TransportMonthlyTracking.is_service_enabled == True
            )
            .order_by(
                TransportMonthlyTracking.academic_year,
                TransportMonthlyTracking.academic_month
            )
        )
        monthly_records = result.scalars().all()

        if not monthly_records:
            selected = payment_data.selected_months
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No enabled months found for selected months: {selected}"
            )

        # Filter records with unpaid balance
        unpaid_records = []
        for record in monthly_records:
            balance = (
                Decimal(str(record.monthly_amount)) -
                Decimal(str(record.paid_amount))
            )
            if balance > 0:
                unpaid_records.append(record)

        if not unpaid_records:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected months are already fully paid"
            )

        # Distribute payment across months
        remaining_amount = payment_data.amount
        months_paid = []

        for record in unpaid_records:
            if remaining_amount <= 0:
                break

            balance = Decimal(str(record.monthly_amount)) - Decimal(str(record.paid_amount))

            if balance > 0:
                payment_for_month = min(remaining_amount, balance)
                record.paid_amount = Decimal(str(record.paid_amount)) + payment_for_month

                # Update payment status with proper Decimal comparison
                # Round to 2 decimal places to avoid precision issues
                paid_rounded = record.paid_amount.quantize(Decimal('0.01'))
                monthly_rounded = Decimal(str(record.monthly_amount)).quantize(Decimal('0.01'))

                if paid_rounded >= monthly_rounded:
                    record.payment_status_id = 2  # PAID
                elif record.paid_amount > 0:
                    record.payment_status_id = 3  # PARTIAL
                else:
                    record.payment_status_id = 1  # PENDING

                record.updated_at = datetime.now()
                remaining_amount -= payment_for_month

                months_paid.append({
                    "month": record.month_name,
                    "year": record.academic_year,
                    "amount_paid": float(payment_for_month)
                })
        
        # Create payment record
        from app.models.transport import TransportPayment
        payment = TransportPayment(
            enrollment_id=enrollment.id,
            student_id=student_id,
            amount=payment_data.amount,
            payment_method_id=payment_data.payment_method_id,
            payment_date=date.today(),
            transaction_id=payment_data.transaction_id or f"TXN{datetime.now().timestamp()}",
            remarks=payment_data.remarks
        )
        db.add(payment)
        
        await db.commit()
        
        return {
            "success": True,
            "message": "Payment processed successfully",
            "amount_paid": float(payment_data.amount),
            "months_paid": months_paid,
            "remaining_amount": float(remaining_amount)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing payment: {str(e)}"
        )

