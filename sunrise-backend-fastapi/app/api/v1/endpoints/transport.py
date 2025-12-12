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
from app.crud.crud_transport import (
    transport_enrollment_crud, transport_monthly_tracking_crud, transport_payment_crud
)
from app.crud import student_crud
from app.crud.metadata import payment_method_crud
from app.schemas.transport import (
    TransportTypeResponse, TransportDistanceSlabResponse,
    StudentTransportEnrollmentCreate, StudentTransportEnrollmentResponse,
    StudentTransportEnrollmentUpdate, EnhancedStudentTransportSummary,
    EnableTransportMonthlyTrackingRequest, StudentTransportMonthlyHistory,
    TransportPaymentRequest, TransportPaymentReversalRequest,
    TransportPartialReversalRequest, TransportPaymentReversalResponse,
    TransportPaymentResponse, TransportPaymentAllocationResponse
)
from sqlalchemy import select
from app.services.alert_service import alert_service

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

        # Create payment record first
        from app.models.transport import TransportPayment, TransportPaymentAllocation
        payment = TransportPayment(
            enrollment_id=enrollment.id,
            student_id=student_id,
            amount=payment_data.amount,
            payment_method_id=payment_data.payment_method_id,
            payment_date=date.today(),
            transaction_id=payment_data.transaction_id or f"TXN{datetime.now().timestamp()}",
            remarks=payment_data.remarks,
            created_by=current_user.id
        )
        db.add(payment)
        await db.flush()  # Get payment ID

        # Distribute payment across months and create allocations
        remaining_amount = payment_data.amount
        months_paid = []

        for record in unpaid_records:
            if remaining_amount <= 0:
                break

            balance = Decimal(str(record.monthly_amount)) - Decimal(str(record.paid_amount))

            if balance > 0:
                payment_for_month = min(remaining_amount, balance)
                record.paid_amount = Decimal(str(record.paid_amount)) + payment_for_month

                # Create allocation record
                allocation = TransportPaymentAllocation(
                    transport_payment_id=payment.id,
                    monthly_tracking_id=record.id,
                    allocated_amount=payment_for_month,
                    is_reversal=False,
                    created_by=current_user.id
                )
                db.add(allocation)

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

        await db.commit()

        # Generate alert for transport fee payment
        try:
            # Get student info
            student = await student_crud.get(db, id=student_id)
            if student:
                # Get payment method description
                payment_method = await payment_method_crud.get_by_id_async(db, id=payment_data.payment_method_id)
                payment_method_desc = payment_method.description if payment_method else "Cash"

                # Get current user name
                actor_name = f"{current_user.first_name} {current_user.last_name}" if current_user.first_name else "Admin"

                # Build months paid string
                months_paid_str = ", ".join([m["month"] for m in months_paid]) if months_paid else None

                await alert_service.create_fee_payment_alert(
                    db,
                    payment_id=payment.id,
                    student_id=student.id,
                    student_name=f"{student.first_name} {student.last_name}",
                    class_name=student.class_ref.description if student.class_ref else "Unknown",
                    amount=float(payment_data.amount),
                    payment_method=payment_method_desc,
                    fee_type='TRANSPORT',
                    months_paid=months_paid_str,
                    actor_user_id=current_user.id,
                    actor_name=actor_name
                )
        except Exception as e:
            # Log error but don't fail the payment
            print(f"Failed to create transport fee payment alert: {e}")

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


# =====================================================
# Payment History Endpoint
# =====================================================

@router.get("/payments/history/{student_id}", response_model=List[TransportPaymentResponse])
async def get_transport_payment_history(
    student_id: int,
    session_year_id: int = Query(..., description="Session year ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get payment history for a student with allocations
    Filters out already-reversed allocations
    """
    try:
        from app.models.transport import TransportPayment, TransportPaymentAllocation
        from sqlalchemy.orm import selectinload

        # Get enrollment
        enrollment = await transport_enrollment_crud.get_active_enrollment(
            db, student_id, session_year_id
        )

        if not enrollment:
            return []

        # Get all payments for this enrollment with proper relationship loading
        from app.models.transport import TransportMonthlyTracking

        result = await db.execute(
            select(TransportPayment)
            .options(
                selectinload(TransportPayment.allocations).selectinload(TransportPaymentAllocation.monthly_tracking)
            )
            .where(TransportPayment.enrollment_id == enrollment.id)
            .order_by(TransportPayment.payment_date.desc(), TransportPayment.id.desc())
        )
        payments = result.scalars().all()

        # Get all allocations for this enrollment to check for reversals across all payments
        all_allocations_query = select(TransportPaymentAllocation).join(
            TransportPayment
        ).where(TransportPayment.enrollment_id == enrollment.id)
        all_allocations_result = await db.execute(all_allocations_query)
        all_allocations = all_allocations_result.scalars().all()

        # Build a set of allocation IDs that have been reversed
        reversed_allocation_ids = set()
        for alloc in all_allocations:
            if alloc.is_reversal and alloc.reverses_allocation_id:
                reversed_allocation_ids.add(alloc.reverses_allocation_id)

        # Build response with filtered allocations
        payment_responses = []
        for payment in payments:
            # Filter out reversed allocations
            filtered_allocations = [
                alloc for alloc in payment.allocations
                if alloc.id not in reversed_allocation_ids
            ]

            # Build allocation responses
            allocation_responses = []
            for alloc in filtered_allocations:
                allocation_responses.append(TransportPaymentAllocationResponse(
                    id=alloc.id,
                    transport_payment_id=alloc.transport_payment_id,
                    monthly_tracking_id=alloc.monthly_tracking_id,
                    allocated_amount=alloc.allocated_amount,
                    is_reversal=alloc.is_reversal,
                    reverses_allocation_id=alloc.reverses_allocation_id,
                    created_at=alloc.created_at,
                    month_name=alloc.monthly_tracking.month_name if alloc.monthly_tracking else None,
                    academic_year=alloc.monthly_tracking.academic_year if alloc.monthly_tracking else None,
                    academic_month=alloc.monthly_tracking.academic_month if alloc.monthly_tracking else None
                ))

            payment_responses.append(TransportPaymentResponse(
                id=payment.id,
                enrollment_id=payment.enrollment_id,
                student_id=payment.student_id,
                amount=payment.amount,
                payment_method_id=payment.payment_method_id,
                payment_date=payment.payment_date,
                transaction_id=payment.transaction_id,
                remarks=payment.remarks,
                receipt_number=payment.receipt_number,
                created_at=payment.created_at,
                is_reversal=payment.is_reversal,
                reverses_payment_id=payment.reverses_payment_id,
                reversed_by_payment_id=payment.reversed_by_payment_id,
                reversal_reason_id=payment.reversal_reason_id,
                reversal_type=payment.reversal_type,
                can_be_reversed=payment.can_be_reversed,
                is_reversed=payment.is_reversed,
                allocations=allocation_responses
            ))

        return payment_responses

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching payment history: {str(e)}"
        )


# =====================================================
# Payment Reversal Endpoints
# =====================================================

@router.post("/payments/{payment_id}/reverse/full", response_model=TransportPaymentReversalResponse)
async def reverse_transport_payment_full(
    payment_id: int,
    reversal_data: TransportPaymentReversalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Reverse an entire transport payment

    This will:
    - Create a new reversal payment with negative amount
    - Reverse all month allocations
    - Update monthly tracking records
    - Mark original payment as reversed
    """
    try:
        result = await transport_payment_crud.reverse_payment_full(
            db,
            payment_id=payment_id,
            reason_id=reversal_data.reason_id,
            details=reversal_data.details,
            user_id=current_user.id
        )

        # Generate alert for transport payment reversal
        try:
            from app.crud.metadata import reversal_reason_crud
            # Get student info from the result
            student_id = result.get("student_id")
            if student_id:
                student = await student_crud.get(db, id=student_id)
                if student:
                    # Get reversal reason description
                    reversal_reason = await reversal_reason_crud.get_by_id_async(db, id=reversal_data.reason_id)
                    reversal_reason_desc = reversal_reason.description if reversal_reason else "Unknown"

                    # Get current user name
                    actor_name = f"{current_user.first_name} {current_user.last_name}" if current_user.first_name else "Admin"

                    await alert_service.create_payment_reversal_alert(
                        db,
                        reversal_payment_id=result.get("reversal_payment_id"),
                        original_payment_id=payment_id,
                        student_name=f"{student.first_name} {student.last_name}",
                        class_name=student.class_ref.description if student.class_ref else "Unknown",
                        amount=result.get("reversed_amount", 0),  # Use "reversed_amount"
                        reversal_reason=reversal_reason_desc,
                        fee_type='TRANSPORT',
                        actor_user_id=current_user.id,
                        actor_name=actor_name
                    )
        except Exception as e:
            # Log error but don't fail the reversal
            print(f"Failed to create transport payment reversal alert: {e}")

        return TransportPaymentReversalResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reversing payment: {str(e)}"
        )


@router.post("/payments/{payment_id}/reverse/partial", response_model=TransportPaymentReversalResponse)
async def reverse_transport_payment_partial(
    payment_id: int,
    reversal_data: TransportPartialReversalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Reverse specific month allocations of a transport payment

    This will:
    - Create a new reversal payment with negative amount for selected months
    - Reverse only the specified month allocations
    - Update monthly tracking records for affected months
    - Allow multiple partial reversals on the same payment
    """
    try:
        result = await transport_payment_crud.reverse_payment_partial(
            db,
            payment_id=payment_id,
            allocation_ids=reversal_data.allocation_ids,
            reason_id=reversal_data.reason_id,
            details=reversal_data.details,
            user_id=current_user.id
        )

        # Generate alert for partial transport payment reversal
        try:
            from app.crud.metadata import reversal_reason_crud
            # Get student info from the result
            student_id = result.get("student_id")
            if student_id:
                student = await student_crud.get(db, id=student_id)
                if student:
                    # Get reversal reason description
                    reversal_reason = await reversal_reason_crud.get_by_id_async(db, id=reversal_data.reason_id)
                    reversal_reason_desc = reversal_reason.description if reversal_reason else "Unknown"

                    # Get current user name
                    actor_name = f"{current_user.first_name} {current_user.last_name}" if current_user.first_name else "Admin"

                    await alert_service.create_payment_reversal_alert(
                        db,
                        reversal_payment_id=result.get("reversal_payment_id"),
                        original_payment_id=payment_id,
                        student_name=f"{student.first_name} {student.last_name}",
                        class_name=student.class_ref.description if student.class_ref else "Unknown",
                        amount=result.get("reversed_amount", 0),  # Use "reversed_amount"
                        reversal_reason=reversal_reason_desc,
                        fee_type='TRANSPORT',
                        actor_user_id=current_user.id,
                        actor_name=actor_name
                    )
        except Exception as e:
            # Log error but don't fail the reversal
            print(f"Failed to create partial transport payment reversal alert: {e}")

        return TransportPaymentReversalResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reversing payment: {str(e)}"
        )

