from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, func, select, text
from sqlalchemy.orm import joinedload, selectinload
from datetime import date, datetime, timedelta
import math
import calendar
import logging

from app.core.database import get_db
from app.crud import fee_structure_crud, fee_record_crud, fee_payment_crud, student_crud, teacher_crud
from app.crud.crud_monthly_fee import monthly_fee_tracking_crud, monthly_payment_allocation_crud
from app.crud.metadata import payment_method_crud
from app.schemas.fee import (
    FeeStructure, FeeStructureCreate, FeeStructureUpdate,
    FeeRecord, FeeRecordCreate, FeeRecordUpdate, FeeRecordWithStudent,
    FeePayment, FeePaymentCreate, FeePaymentUpdate,
    FeeFilters, FeeListResponse, FeeDashboard, FeeCollectionReport,
    SessionYearEnum, PaymentStatusEnum, PaymentTypeEnum,
    EnhancedStudentFeeSummary, StudentMonthlyFeeHistory, EnhancedPaymentRequest,
    EnableMonthlyTrackingRequest, MonthlyFeeTracking,
    FeePaymentReversalRequest, FeePaymentPartialReversalRequest, FeePaymentReversalResponse
)
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.expense import Expense as ExpenseModel
from app.models.fee import FeeRecord as FeeRecordModel, FeePayment as FeePaymentModel, MonthlyFeeTracking as MonthlyFeeTrackingModel, MonthlyPaymentAllocation
from app.models.transport import StudentTransportEnrollment, TransportMonthlyTracking
from app.services.alert_service import alert_service
from app.services.receipt_generator import ReceiptGenerator
from app.services.cloudinary_receipt_service import CloudinaryReceiptService
from app.services.whatsapp_service import whatsapp_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=FeeListResponse)
@router.get("", response_model=FeeListResponse)  # Handle both with and without trailing slash
async def get_fees(
    session_year: Optional[SessionYearEnum] = SessionYearEnum.YEAR_2025_26,
    class_id: Optional[int] = Query(None, description="Filter by class ID"),
    month: Optional[int] = Query(None, ge=1, le=12),
    status: Optional[PaymentStatusEnum] = None,
    payment_type: Optional[PaymentTypeEnum] = None,
    student_id: Optional[int] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    search: Optional[str] = Query(None, description="Search by student name or admission number"),
    sort_by: Optional[str] = Query("due_date", description="Sort by: due_date, student_name, amount, status"),
    sort_order: Optional[str] = Query("asc", description="Sort order: asc or desc"),
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get fee records with comprehensive filters and enhanced search capabilities
    Defaults to current financial year 2025-26
    """
    filters = FeeFilters(
        session_year=session_year,
        class_id=class_id,
        month=month,
        status=status,
        payment_type=payment_type,
        student_id=student_id,
        from_date=from_date,
        to_date=to_date
    )

    skip = (page - 1) * per_page
    fees, total = await fee_record_crud.get_multi_with_filters(
        db, filters=filters, skip=skip, limit=per_page, search=search, sort_by=sort_by, sort_order=sort_order
    )

    # Convert to enhanced response format with student details
    fee_list = []
    for fee in fees:
        # Use the schema method to properly convert the ORM object
        try:
            fee_record = FeeRecord.from_orm_with_metadata(fee)
            # Add student details for the FeeRecordWithStudent schema
            student_name = f"{fee.student.first_name} {fee.student.last_name}" if fee.student else "Unknown"
            student_admission = fee.student.admission_number if fee.student else "Unknown"
            student_class = fee.student.class_ref.name if fee.student and fee.student.class_ref else "Unknown"

            fee_dict = fee_record.dict()
            fee_dict.update({
                "student_name": student_name,
                "student_admission_number": student_admission,
                "student_class": student_class,
                "is_overdue": fee.due_date < date.today() and fee.balance_amount > 0,
                "days_overdue": (date.today() - fee.due_date).days if fee.due_date < date.today() and fee.balance_amount > 0 else 0
            })
            fee_list.append(fee_dict)
        except Exception as e:
            # Fallback to manual construction if schema method fails
            student_name = f"{fee.student.first_name} {fee.student.last_name}" if fee.student else "Unknown"
            student_admission = fee.student.admission_number if fee.student else "Unknown"
            student_class = fee.student.class_ref.name if fee.student and fee.student.class_ref else "Unknown"

            fee_dict = {
                "id": fee.id,
                "student_id": fee.student_id,
                "session_year_id": fee.session_year_id,
                "payment_type_id": fee.payment_type_id,
                "payment_status_id": fee.payment_status_id,
                "payment_method_id": fee.payment_method_id,
                "total_amount": float(fee.total_amount),
                "paid_amount": float(fee.paid_amount),
                "balance_amount": float(fee.balance_amount),
                "due_date": fee.due_date,
                "payment_date": fee.payment_date,
                "transaction_id": fee.transaction_id,
                "remarks": fee.remarks,
                "created_at": fee.created_at,
                "updated_at": fee.updated_at,
                "student_name": student_name,
                "student_admission_number": student_admission,
                "student_class": student_class,
                "session_year_name": None,
                "payment_type_name": None,
                "payment_status_name": None,
                "payment_method_name": None,
                "is_overdue": fee.due_date < date.today() and fee.balance_amount > 0,
                "days_overdue": (date.today() - fee.due_date).days if fee.due_date < date.today() and fee.balance_amount > 0 else 0
            }
            fee_list.append(fee_dict)

    # Get enhanced summary statistics
    summary = await fee_record_crud.get_collection_summary(db, session_year=session_year)

    # Add additional analytics
    overdue_count = sum(1 for fee in fee_list if fee["is_overdue"])
    total_overdue_amount = sum(fee["balance_amount"] for fee in fee_list if fee["is_overdue"])

    # Safe division to avoid division by zero
    total_amount = summary.get("total_amount", 0) or 0
    paid_amount = summary.get("paid_amount", 0) or 0
    collection_efficiency = round((paid_amount / total_amount) * 100, 2) if total_amount > 0 else 0

    enhanced_summary = {
        **summary,
        "overdue_records": overdue_count,
        "overdue_amount": float(total_overdue_amount),
        "collection_efficiency": collection_efficiency
    }

    total_pages = math.ceil(total / per_page)

    return FeeListResponse(
        fees=fee_list,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        summary=enhanced_summary
    )


@router.post("/", response_model=FeeRecordWithStudent)
@router.post("", response_model=FeeRecordWithStudent)  # Handle both with and without trailing slash
async def create_fee_record(
    fee_data: FeeRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new fee record for a student with enhanced validation
    """
    # Verify student exists
    student = await student_crud.get(db, id=fee_data.student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Validate amount
    if fee_data.total_amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Total amount must be greater than 0"
        )

    # Validate balance amount matches total amount for new records
    if hasattr(fee_data, 'balance_amount') and fee_data.balance_amount != fee_data.total_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Balance amount must equal total amount for new fee records"
        )

    # Check for duplicate fee record for same student, session, and payment type
    existing_record = await fee_record_crud.get_by_student_session_type(
        db,
        student_id=fee_data.student_id,
        session_year_id=fee_data.session_year_id,
        payment_type_id=fee_data.payment_type_id
    )

    if existing_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fee record already exists for this student, session year, and payment type"
        )

    # Create fee record
    fee_record = await fee_record_crud.create(db, obj_in=fee_data)
    return fee_record


@router.post("/bulk-create/{student_id}")
async def create_bulk_fee_records(
    student_id: int,
    bulk_data: dict,  # {"session_year_id": int, "payment_types": [{"payment_type_id": int, "total_amount": float, "due_date": "YYYY-MM-DD"}]}
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create multiple fee records for a student with different payment types
    Useful for creating monthly, quarterly, half-yearly, and yearly fee records
    """
    # Verify student exists
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    session_year_id = bulk_data.get("session_year_id")
    payment_types = bulk_data.get("payment_types", [])

    if not session_year_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="session_year_id is required"
        )

    if not payment_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one payment type is required"
        )

    created_records = []
    errors = []

    for payment_type_data in payment_types:
        try:
            # Check for existing record
            existing_record = await fee_record_crud.get_by_student_session_type(
                db,
                student_id=student_id,
                session_year_id=session_year_id,
                payment_type_id=payment_type_data["payment_type_id"]
            )

            if existing_record:
                errors.append(f"Fee record already exists for payment type {payment_type_data['payment_type_id']}")
                continue

            # Create fee record data
            fee_record_data = FeeRecordCreate(
                student_id=student_id,
                session_year_id=session_year_id,
                class_id=student.class_id,  # Get class_id from student record
                payment_type_id=payment_type_data["payment_type_id"],
                total_amount=payment_type_data["total_amount"],
                balance_amount=payment_type_data["total_amount"],
                due_date=payment_type_data["due_date"],
                payment_status_id=1,  # Pending
                is_monthly_tracked=False  # Not monthly tracked for bulk creation
            )

            # Create fee record
            fee_record = await fee_record_crud.create(db, obj_in=fee_record_data)
            created_records.append(fee_record)

        except Exception as e:
            errors.append(f"Error creating record for payment type {payment_type_data.get('payment_type_id', 'unknown')}: {str(e)}")

    return {
        "message": f"Created {len(created_records)} fee records",
        "created_records": created_records,
        "errors": errors if errors else None
    }


@router.get("/student/{student_id}")
async def get_student_fees(
    student_id: int,
    session_year: Optional[SessionYearEnum] = SessionYearEnum.YEAR_2025_26,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all fee records for a specific student
    Defaults to current financial year 2025-26
    """
    # Verify student exists
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    fee_records = await fee_record_crud.get_by_student(
        db, student_id=student_id, session_year=session_year
    )

    return {
        "student_id": student_id,
        "student_name": f"{student.first_name} {student.last_name}",
        "admission_number": student.admission_number,
        "current_class": student.class_ref.name if student.class_ref else "",
        "current_session": session_year.value if session_year else "2025-26",
        "fee_records": fee_records
    }


# =====================================================
# Payment Reversal Endpoints
# =====================================================

@router.post("/payments/{payment_id}/reverse", response_model=FeePaymentReversalResponse)
async def reverse_payment_full(
    payment_id: int,
    reversal_request: FeePaymentReversalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Reverse an entire payment with all its allocations

    This endpoint allows admins to reverse a payment completely, undoing all
    monthly allocations and updating fee records accordingly.

    **Authorization:** Admin only (user_type_id = 1)

    **Business Rules:**
    - Cannot reverse a payment that is already reversed
    - Cannot reverse a reversal payment itself
    - Creates a new payment record with negative amount
    - Updates all affected monthly tracking records
    - Updates fee record totals and status
    - Creates audit log entry

    **Args:**
    - payment_id: ID of the payment to reverse
    - reversal_request: Contains reason and optional details

    **Returns:**
    - FeePaymentReversalResponse with reversal details
    """
    # Check admin authorization
    if current_user.user_type_id != 1:  # 1 = Admin
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can reverse payments"
        )

    try:
        result = await fee_payment_crud.reverse_payment_full(
            db,
            payment_id=payment_id,
            reason_id=reversal_request.reason_id,
            details=reversal_request.details,
            user_id=current_user.id
        )

        # Generate alert for payment reversal
        try:
            # Get student info using student_id from result
            from app.crud.metadata import reversal_reason_crud
            student_id = result.get("student_id")
            if student_id:
                student = await student_crud.get(db, id=student_id)
                if student:
                    # Get reversal reason description
                    reversal_reason = await reversal_reason_crud.get_by_id_async(db, id=reversal_request.reason_id)
                    reversal_reason_desc = reversal_reason.description if reversal_reason else "Unknown"

                    # Get current user name
                    actor_name = f"{current_user.first_name} {current_user.last_name}" if current_user.first_name else "Admin"

                    await alert_service.create_payment_reversal_alert(
                        db,
                        reversal_payment_id=result.get("reversal_payment_id"),
                        original_payment_id=payment_id,
                        student_name=f"{student.first_name} {student.last_name}",
                        class_name=student.class_ref.description if student.class_ref else "Unknown",
                        amount=result.get("reversal_amount", 0),
                        reversal_reason=reversal_reason_desc,
                        fee_type='TUITION',
                        actor_user_id=current_user.id,
                        actor_name=actor_name
                    )
        except Exception as e:
            # Log error but don't fail the reversal
            print(f"Failed to create payment reversal alert: {e}")

        return result
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


@router.post("/payments/{payment_id}/reverse-months", response_model=FeePaymentReversalResponse)
async def reverse_payment_partial(
    payment_id: int,
    reversal_request: FeePaymentPartialReversalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Reverse specific month allocations of a payment (partial reversal)

    This endpoint allows admins to reverse only specific months of a payment,
    leaving other months intact. Useful when some months were correct but others weren't.

    **Authorization:** Admin only (user_type_id = 1)

    **Business Rules:**
    - Cannot reverse all allocations (use full reversal instead)
    - Cannot reverse allocations that are already reversed
    - Cannot reverse a reversal payment itself
    - Creates a new payment record with negative amount (sum of selected allocations)
    - Updates only affected monthly tracking records
    - Updates fee record totals and status
    - Creates audit log entry

    **Args:**
    - payment_id: ID of the payment to partially reverse
    - reversal_request: Contains allocation_ids, reason, and optional details

    **Returns:**
    - FeePaymentReversalResponse with reversal details
    """
    # Check admin authorization
    if current_user.user_type_id != 1:  # 1 = Admin
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can reverse payments"
        )

    # Validate allocation_ids
    if not reversal_request.allocation_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one allocation ID must be provided"
        )

    try:
        result = await fee_payment_crud.reverse_payment_partial(
            db,
            payment_id=payment_id,
            allocation_ids=reversal_request.allocation_ids,
            reason_id=reversal_request.reason_id,
            details=reversal_request.details,
            user_id=current_user.id
        )

        # Generate alert for partial payment reversal
        try:
            # Get student info using student_id from result
            from app.crud.metadata import reversal_reason_crud
            student_id = result.get("student_id")
            if student_id:
                student = await student_crud.get(db, id=student_id)
                if student:
                    # Get reversal reason description
                    reversal_reason = await reversal_reason_crud.get_by_id_async(db, id=reversal_request.reason_id)
                    reversal_reason_desc = reversal_reason.description if reversal_reason else "Unknown"

                    # Get current user name
                    actor_name = f"{current_user.first_name} {current_user.last_name}" if current_user.first_name else "Admin"

                    await alert_service.create_payment_reversal_alert(
                        db,
                        reversal_payment_id=result.get("reversal_payment_id"),
                        original_payment_id=payment_id,
                        student_name=f"{student.first_name} {student.last_name}",
                        class_name=student.class_ref.description if student.class_ref else "Unknown",
                        amount=result.get("reversal_amount", 0),
                        reversal_reason=reversal_reason_desc,
                        fee_type='TUITION',
                        actor_user_id=current_user.id,
                        actor_name=actor_name
                    )
        except Exception as e:
            # Log error but don't fail the reversal
            print(f"Failed to create partial payment reversal alert: {e}")

        return result
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


@router.get("/student-options/{student_id}")
async def get_student_fee_options(
    student_id: int,
    session_year: Optional[SessionYearEnum] = SessionYearEnum.YEAR_2025_26,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get available fee payment options for a student
    Shows different payment frequencies and their amounts
    """
    # Verify student exists and current user has permission
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Check if current user is the student or has admin/teacher/super_admin role
    # 1=admin, 2=teacher, 6=super_admin can view any student's fee options
    if current_user.user_type_id not in [1, 2, 6] and student.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view fee options for your own account"
        )

    # Get fee structure for student's class and session
    fee_structure = await fee_structure_crud.get_by_class_and_session(
        db,
        class_name=student.class_ref.name if student.class_ref else "",
        session_year=session_year.value
    )

    if not fee_structure:
        return {
            "student_id": student_id,
            "student_name": f"{student.first_name} {student.last_name}",
            "class": student.class_ref.name if student.class_ref else "",
            "session_year": session_year.value,
            "message": "No fee structure found for this class and session",
            "payment_options": []
        }

    # Calculate payment amounts for different frequencies
    annual_fee = fee_structure.total_annual_fee
    payment_options = [
        {
            "payment_type": "Monthly",
            "payment_type_id": 1,
            "amount": round(annual_fee / 12, 2),
            "frequency": "12 payments per year",
            "description": "Pay monthly installments"
        },
        {
            "payment_type": "Quarterly",
            "payment_type_id": 2,
            "amount": round(annual_fee / 4, 2),
            "frequency": "4 payments per year",
            "description": "Pay quarterly installments"
        },
        {
            "payment_type": "Half Yearly",
            "payment_type_id": 3,
            "amount": round(annual_fee / 2, 2),
            "frequency": "2 payments per year",
            "description": "Pay half-yearly installments"
        },
        {
            "payment_type": "Yearly",
            "payment_type_id": 4,
            "amount": annual_fee,
            "frequency": "1 payment per year",
            "description": "Pay full annual fee"
        }
    ]

    # Get existing fee records to show current status
    existing_records = await fee_record_crud.get_by_student(
        db, student_id=student_id, session_year=session_year
    )

    # Add status to payment options
    for option in payment_options:
        existing_record = next(
            (record for record in existing_records if record.payment_type_id == option["payment_type_id"]),
            None
        )
        if existing_record:
            option["status"] = existing_record.payment_status_name
            option["paid_amount"] = existing_record.paid_amount
            option["balance_amount"] = existing_record.balance_amount
            option["due_date"] = existing_record.due_date
        else:
            option["status"] = "Not Created"
            option["paid_amount"] = 0
            option["balance_amount"] = option["amount"]
            option["due_date"] = None

    return {
        "student_id": student_id,
        "student_name": f"{student.first_name} {student.last_name}",
        "admission_number": student.admission_number,
        "class": student.class_ref.name if student.class_ref else "",
        "session_year": session_year.value,
        "annual_fee": annual_fee,
        "payment_options": payment_options
    }


@router.get("/history/{student_id}")
async def get_fee_history(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get complete fee payment history for a student
    """
    # Verify student exists
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Get all fee records for the student
    fee_records = await fee_record_crud.get_by_student(db, student_id=student_id)

    # Get payment history for each fee record
    payment_history = []
    for fee_record in fee_records:
        payments = await fee_payment_crud.get_by_fee_record(db, fee_record_id=fee_record.id)
        payment_history.extend([
            {
                **payment.__dict__,
                "fee_record_id": fee_record.id,
                "session_year": fee_record.session_year,
                "payment_type": fee_record.payment_type
            }
            for payment in payments
        ])

    # Sort by payment date (most recent first)
    payment_history.sort(key=lambda x: x.get('payment_date', date.min), reverse=True)

    return {
        "student_id": student_id,
        "student_name": f"{student.first_name} {student.last_name}",
        "admission_number": student.admission_number,
        "payment_history": payment_history
    }


@router.get("/structure", response_model=List[FeeStructure])
async def get_fee_structure(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get fee structure for different classes
    """
    fee_structures = await fee_structure_crud.get_all_structures(db)
    return fee_structures


@router.post("/structure", response_model=FeeStructure)
async def create_fee_structure(
    structure_data: FeeStructureCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create or update fee structure for a class
    """
    # Check if structure already exists for this class and session
    existing = await fee_structure_crud.get_by_class_and_session(
        db, class_name=structure_data.class_name, session_year=structure_data.session_year
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fee structure already exists for {structure_data.class_name} - {structure_data.session_year}"
        )

    fee_structure = await fee_structure_crud.create(db, obj_in=structure_data)
    return fee_structure


@router.put("/structure/{structure_id}", response_model=FeeStructure)
async def update_fee_structure(
    structure_id: int,
    structure_data: FeeStructureUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update fee structure
    """
    fee_structure = await fee_structure_crud.get(db, id=structure_id)
    if not fee_structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fee structure not found"
        )

    updated_structure = await fee_structure_crud.update(
        db, db_obj=fee_structure, obj_in=structure_data
    )
    return updated_structure


@router.get("/reports/pending")
async def get_pending_fees_report(
    session_year: Optional[SessionYearEnum] = SessionYearEnum.YEAR_2025_26,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get report of all pending fees
    """
    # Get overdue fees
    overdue_fees = await fee_record_crud.get_overdue_fees(db)

    # Get collection summary
    summary = await fee_record_crud.get_collection_summary(db, session_year=session_year)

    return {
        "summary": {
            "total_pending_amount": summary['pending_amount'],
            "total_students": summary['total_records'],
            "overdue_count": len(overdue_fees),
            "collection_rate": summary['collection_rate']
        },
        "overdue_fees": [
            {
                "id": fee.id,
                "student_name": f"{fee.student.first_name} {fee.student.last_name}",
                "admission_number": fee.student.admission_number,
                "class": fee.student.current_class,
                "total_amount": fee.total_amount,
                "balance_amount": fee.balance_amount,
                "due_date": fee.due_date,
                "days_overdue": (date.today() - fee.due_date).days
            }
            for fee in overdue_fees
        ]
    }


@router.get("/reports/collection")
async def get_fee_collection_report(
    session_year: Optional[SessionYearEnum] = SessionYearEnum.YEAR_2025_26,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get fee collection report by month/quarter/year
    """
    summary = await fee_record_crud.get_collection_summary(db, session_year=session_year)

    return {
        "session_year": session_year or "All Sessions",
        "collection_summary": {
            "total_amount": summary['total_amount'],
            "collected_amount": summary['paid_amount'],
            "pending_amount": summary['pending_amount'],
            "collection_rate": summary['collection_rate'],
            "total_records": summary['total_records'],
            "paid_records": summary['paid_records']
        }
    }


@router.post("/records", response_model=FeeRecordWithStudent)
async def create_fee_record(
    fee_data: FeeRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new fee record for a student
    """
    # Verify student exists
    student = await student_crud.get(db, id=fee_data.student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Create fee record
    fee_record = await fee_record_crud.create(db, obj_in=fee_data)
    return fee_record


@router.put("/records/{fee_record_id}", response_model=FeeRecordWithStudent)
async def update_fee_record(
    fee_record_id: int,
    fee_data: FeeRecordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing fee record with enhanced validation
    """
    fee_record = await fee_record_crud.get(db, id=fee_record_id)
    if not fee_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fee record not found"
        )

    # Validate total amount if being updated
    if hasattr(fee_data, 'total_amount') and fee_data.total_amount is not None:
        if fee_data.total_amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Total amount must be greater than 0"
            )

        # Ensure total amount is not less than already paid amount
        if fee_data.total_amount < fee_record.paid_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Total amount cannot be less than already paid amount ({fee_record.paid_amount})"
            )

    # Validate balance amount if being updated
    if hasattr(fee_data, 'balance_amount') and fee_data.balance_amount is not None:
        total_amount = fee_data.total_amount if hasattr(fee_data, 'total_amount') and fee_data.total_amount is not None else fee_record.total_amount
        expected_balance = total_amount - fee_record.paid_amount

        if fee_data.balance_amount != expected_balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Balance amount must be {expected_balance} (total - paid)"
            )

    updated_record = await fee_record_crud.update(db, db_obj=fee_record, obj_in=fee_data)
    return updated_record


@router.delete("/records/{fee_record_id}")
async def delete_fee_record(
    fee_record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a fee record (only if no payments made)
    """
    fee_record = await fee_record_crud.get(db, id=fee_record_id)
    if not fee_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fee record not found"
        )

    # Check if any payments have been made
    if fee_record.paid_amount > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete fee record with payments. Please contact administrator."
        )

    await fee_record_crud.remove(db, id=fee_record_id)
    return {"message": "Fee record deleted successfully"}


@router.get("/payments/history/{student_id}")
async def get_payment_history(
    student_id: int,
    session_year: Optional[SessionYearEnum] = SessionYearEnum.YEAR_2025_26,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get comprehensive payment history for a student with record-wise details
    Enhanced with receipt and WhatsApp metadata for Fee Receipt History feature
    """
    # Verify student exists
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Check if current user has permission to view this student's history
    # 1=admin, 2=teacher, 6=super_admin can view any student's history
    if current_user.user_type_id not in [1, 2, 6] and student.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view payment history for your own account"
        )

    # Get parent phone for WhatsApp resend capability
    parent_phone = student.phone or student.father_phone or student.mother_phone

    # Get all fee records for the student in the specified session
    fee_records = await fee_record_crud.get_by_student(
        db, student_id=student_id, session_year=session_year
    )

    # Build comprehensive payment history
    payment_history = []
    total_paid = 0
    total_due = 0
    individual_payments_total = 0  # Track sum of individual payment amounts

    for fee_record in fee_records:
        # Get all payments for this fee record with payment method and allocations relationships
        payments_query = select(FeePaymentModel).options(
            selectinload(FeePaymentModel.payment_method),
            selectinload(FeePaymentModel.allocations).selectinload(MonthlyPaymentAllocation.monthly_tracking)
        ).where(FeePaymentModel.fee_record_id == fee_record.id).order_by(FeePaymentModel.created_at.desc())

        payments_result = await db.execute(payments_query)
        payments = payments_result.scalars().all()

        # Get all allocations for this fee record to check for reversals across all payments
        all_allocations_query = select(MonthlyPaymentAllocation).join(
            FeePaymentModel
        ).where(FeePaymentModel.fee_record_id == fee_record.id)
        all_allocations_result = await db.execute(all_allocations_query)
        all_allocations = all_allocations_result.scalars().all()

        # Build a set of allocation IDs that have been reversed
        reversed_allocation_ids = set()
        for alloc in all_allocations:
            if alloc.is_reversal and alloc.reverses_allocation_id:
                reversed_allocation_ids.add(alloc.reverses_allocation_id)

        record_info = {
            "fee_record_id": fee_record.id,
            "payment_type": fee_record.payment_type_name,
            "payment_type_id": fee_record.payment_type_id,
            "total_amount": fee_record.total_amount,
            "paid_amount": fee_record.paid_amount,
            "balance_amount": fee_record.balance_amount,
            "due_date": fee_record.due_date,
            "status": fee_record.payment_status_name,
            "session_year": fee_record.session_year_name,
            "payments": []
        }

        # Add individual payment details
        for payment in payments:
            # Build allocations list for this payment
            # Only include non-reversal allocations that haven't been reversed
            allocations_list = []
            if payment.allocations:
                for alloc in payment.allocations:
                    # Skip reversal allocations (negative amounts)
                    if alloc.is_reversal:
                        continue

                    # Check if this allocation has been reversed
                    # by checking if its ID is in the reversed_allocation_ids set
                    if alloc.id in reversed_allocation_ids:
                        continue

                    # Include this allocation as it hasn't been reversed
                    allocations_list.append({
                        "id": alloc.id,
                        "allocated_amount": float(alloc.allocated_amount),
                        "month": alloc.monthly_tracking.academic_month if alloc.monthly_tracking else None,
                        "month_name": alloc.monthly_tracking.month_name if alloc.monthly_tracking else None,
                        "is_reversal": alloc.is_reversal
                    })

            # Calculate months covered count
            months_covered = len(allocations_list)

            # Build receipt metadata
            receipt_available = bool(payment.receipt_cloudinary_url)
            receipt_metadata = {
                "available": receipt_available,
                "receipt_number": payment.receipt_number or f"FEE-{payment.id:06d}",
                "receipt_url": payment.receipt_cloudinary_url,
                "generated_at": payment.created_at.isoformat() if payment.created_at else None
            }

            # Build WhatsApp metadata
            # Check if receipt exists and parent phone is available for resend capability
            can_resend = receipt_available and bool(parent_phone) and not payment.is_reversal and not payment.is_reversed

            whatsapp_metadata = {
                "sent": getattr(payment, 'whatsapp_sent', False) or False,
                "sent_at": getattr(payment, 'whatsapp_sent_at', None).isoformat() if getattr(payment, 'whatsapp_sent_at', None) else None,
                "status": getattr(payment, 'whatsapp_status', None),
                "can_resend": can_resend
            }

            payment_detail = {
                "payment_id": payment.id,
                "amount": payment.amount,
                "payment_date": payment.payment_date,
                "payment_method": payment.payment_method.description if payment.payment_method else "Unknown",
                "transaction_id": payment.transaction_id,
                "receipt_number": payment.receipt_number,
                "remarks": payment.remarks,
                "created_at": payment.created_at,
                "is_reversal": payment.is_reversal,
                "is_reversed": payment.is_reversed,
                "can_be_reversed": payment.can_be_reversed,
                "reversed_by_payment_id": payment.reversed_by_payment_id,
                "allocations": allocations_list,
                "months_covered": months_covered,  # NEW: Count of months covered
                "receipt": receipt_metadata,  # NEW: Receipt metadata
                "whatsapp": whatsapp_metadata  # NEW: WhatsApp metadata
            }
            record_info["payments"].append(payment_detail)
            individual_payments_total += float(payment.amount)  # Add to individual total

        # Sort payments by date (most recent first)
        record_info["payments"].sort(key=lambda x: x["payment_date"], reverse=True)

        payment_history.append(record_info)
        # Use individual payment amounts instead of fee_record.paid_amount for consistency
        # total_paid += fee_record.paid_amount  # OLD: This causes discrepancy
        # individual_payments_total is already calculated above in the loop
        total_due += fee_record.balance_amount

    # Get student's fee structure to calculate total annual fee
    from app.crud.crud_fee import fee_structure_crud
    fee_structure = await fee_structure_crud.get_by_class_and_session(
        db,
        class_name=student.class_ref.name if student.class_ref else "",
        session_year=session_year.value
    )

    total_annual_fee = float(fee_structure.total_annual_fee) if fee_structure else 0.0

    # Sort fee records by payment type (Monthly, Quarterly, etc.)
    payment_history.sort(key=lambda x: x["payment_type_id"])

    return {
        "student_id": student_id,
        "student_name": f"{student.first_name} {student.last_name}",
        "admission_number": student.admission_number,
        "roll_number": student.roll_number,
        "class": student.class_ref.name if student.class_ref else "",
        "session_year": session_year.value,
        "parent_phone": parent_phone,  # NEW: For resend functionality
        "summary": {
            "total_amount": total_annual_fee,
            "total_paid": individual_payments_total,  # Use sum of individual payments for consistency
            "individual_payments_total": individual_payments_total,  # Debug field
            "total_due": total_due,
            "total_records": len(payment_history),
            "total_payments": sum(len(record["payments"]) for record in payment_history)
        },
        "payment_history": payment_history
    }


@router.get("/payment-receipt/{payment_id}")
async def get_payment_receipt(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed payment receipt information
    """
    # Get payment record
    payment = await fee_payment_crud.get(db, id=payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment record not found"
        )

    # Get associated fee record and student
    fee_record = await fee_record_crud.get_with_student(db, id=payment.fee_record_id)
    if not fee_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated fee record not found"
        )

    student = fee_record.student

    # Check if current user has permission to view this receipt
    # 1=admin, 2=teacher, 6=super_admin can view any student's receipts
    if current_user.user_type_id not in [1, 2, 6] and student.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view receipts for your own payments"
        )

    return {
        "receipt_info": {
            "payment_id": payment.id,
            "receipt_number": payment.receipt_number or f"RCP-{payment.id:06d}",
            "payment_date": payment.payment_date,
            "amount": payment.amount,
            "payment_method": payment.payment_method_name,
            "transaction_id": payment.transaction_id,
            "remarks": payment.remarks
        },
        "student_info": {
            "student_id": student.id,
            "student_name": f"{student.first_name} {student.last_name}",
            "admission_number": student.admission_number,
            "class": student.class_ref.name if student.class_ref else "",
            "session_year": fee_record.session_year_name
        },
        "fee_info": {
            "fee_record_id": fee_record.id,
            "payment_type": fee_record.payment_type_name,
            "total_amount": fee_record.total_amount,
            "paid_amount": fee_record.paid_amount,
            "balance_amount": fee_record.balance_amount,
            "due_date": fee_record.due_date,
            "status": fee_record.payment_status_name
        },
        "school_info": {
            "name": "Sunrise School",
            "address": "School Address",
            "phone": "School Phone",
            "email": "school@sunrise.com"
        }
    }


@router.post("/receipts/resend-whatsapp/{payment_id}")
async def resend_receipt_whatsapp(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Resend receipt via WhatsApp
    Restricted to admin users only

    This endpoint allows administrators to resend fee receipts to parents via WhatsApp.
    Useful when parents lose the original message or need a copy of the receipt.

    **Authorization:** Admin only (user_type_id = 1)

    **Requirements:**
    - Receipt must be generated and uploaded to Cloudinary
    - Parent phone number must be available
    - Payment must not be reversed or a reversal payment

    **Returns:**
    - success: Boolean indicating if message was sent
    - message: User-friendly message
    - message_sid: Twilio message SID (for tracking)
    - sent_at: Timestamp when message was sent
    """
    # Permission check: Only admin can resend
    if current_user.user_type_id not in [1]:  # 1 = admin
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can resend receipts"
        )

    # Get payment with receipt
    payment = await fee_payment_crud.get(db, id=payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    # Check if payment is reversed or a reversal
    if payment.is_reversal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot resend receipt for reversal payments"
        )

    if payment.is_reversed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot resend receipt for reversed payments"
        )

    # Check if receipt exists
    if not payment.receipt_cloudinary_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Receipt not available for this payment. Please generate the receipt first."
        )

    # Get student and parent phone
    fee_record = await fee_record_crud.get_with_student(db, id=payment.fee_record_id)
    if not fee_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated fee record not found"
        )

    student = fee_record.student
    parent_phone = student.phone or student.father_phone or student.mother_phone

    if not parent_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No parent phone number available for this student"
        )

    # Send WhatsApp notification using media receipt template
    logger.info(f"WhatsApp resend requested for payment {payment_id} by admin {current_user.id}")
    logger.info(f"Receipt URL: {payment.receipt_cloudinary_url}")
    logger.info(f"Parent phone: {parent_phone}")

    try:
        whatsapp_result = await whatsapp_service.send_fee_media_receipt(
            phone_number=parent_phone,
            student_name=f"{student.first_name} {student.last_name}",
            amount=float(payment.amount),
            receipt_url=payment.receipt_cloudinary_url,
            payment_id=payment.id
        )

        if whatsapp_result.get("success"):
            return {
                "success": True,
                "message": f"Receipt sent successfully to {parent_phone}",
                "message_sid": whatsapp_result.get('message_sid'),
                "sent_at": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send WhatsApp: {whatsapp_result.get('error', 'Unknown error')}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resend WhatsApp for payment {payment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send WhatsApp: {str(e)}"
        )


@router.get("/dashboard", response_model=FeeDashboard)
async def get_fee_dashboard(
    session_year: Optional[SessionYearEnum] = SessionYearEnum.YEAR_2025_26,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get fee management dashboard data
    """
    # Get collection summary
    summary = await fee_record_crud.get_collection_summary(db, session_year=session_year)

    # Get total students count
    total_students = await student_crud.get_dashboard_stats(db)

    # Get overdue fees
    overdue_fees = await fee_record_crud.get_overdue_fees(db)
    overdue_amount = sum(fee.balance_amount for fee in overdue_fees)

    return FeeDashboard(
        total_students=total_students['total_students'],
        total_fees_collected=summary['paid_amount'],
        total_fees_pending=summary['pending_amount'],
        overdue_fees=overdue_amount,
        collection_rate=summary['collection_rate'],
        monthly_collection=[],  # TODO: Implement monthly collection data
        class_wise_collection=[],  # TODO: Implement class-wise collection data
        payment_method_breakdown=[]  # TODO: Implement payment method breakdown
    )



# Dashboard endpoints have been moved to app/api/v1/endpoints/dashboard.py
# for better code organization and separation of concerns


@router.get("/analytics")
async def get_fee_analytics(
    session_year: Optional[SessionYearEnum] = SessionYearEnum.YEAR_2025_26,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get comprehensive fee analytics and statistics
    """
    # Get collection summary
    summary = await fee_record_crud.get_collection_summary(db, session_year=session_year)

    # Get overdue fees
    overdue_fees = await fee_record_crud.get_overdue_fees(db)
    overdue_amount = sum(fee.balance_amount for fee in overdue_fees)
    overdue_count = len(overdue_fees)

    # Calculate additional metrics
    collection_efficiency = round((summary.get("paid_amount", 0) / summary.get("total_amount", 1)) * 100, 2)

    # Get payment method breakdown (simplified version)
    all_fees = await fee_record_crud.get_multi_with_filters(
        db,
        filters=FeeFilters(session_year=session_year),
        skip=0,
        limit=1000
    )

    payment_methods = {}
    for fee_record, _ in [all_fees]:
        for fee in fee_record:
            if fee.payment_method_id:
                method_name = fee.payment_method_name if hasattr(fee, 'payment_method_name') else 'Unknown'
                if method_name not in payment_methods:
                    payment_methods[method_name] = {"count": 0, "amount": 0}
                payment_methods[method_name]["count"] += 1
                payment_methods[method_name]["amount"] += fee.paid_amount

    return {
        "session_year": session_year.value,
        "overall_summary": {
            **summary,
            "collection_efficiency": collection_efficiency,
            "overdue_records": overdue_count,
            "overdue_amount": overdue_amount
        },
        "payment_method_breakdown": [
            {"method": method, "count": data["count"], "amount": data["amount"]}
            for method, data in payment_methods.items()
        ],
        "generated_at": date.today()
    }


@router.get("/metadata", deprecated=True)
async def get_fee_metadata(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    DEPRECATED: Use /configuration/fee-management/ instead

    This endpoint returns all metadata but is inefficient.
    Use the service-specific configuration endpoint for better performance:
    - Reduced payload size by 60-80%
    - Faster loading times
    - Only relevant metadata for fee management
    """
    from app.crud.metadata import (
        session_year_crud, payment_status_crud, payment_method_crud,
        class_crud, gender_crud, user_type_crud
    )

    # Get all metadata using async methods
    session_years = await session_year_crud.get_all_async(db)
    payment_statuses = await payment_status_crud.get_all_async(db)
    payment_methods = await payment_method_crud.get_all_async(db)
    classes = await class_crud.get_all_async(db)
    genders = await gender_crud.get_all_async(db)
    user_types = await user_type_crud.get_all_async(db)

    # Define payment frequency options (replacing payment types)
    payment_frequencies = [
        {"id": "monthly", "name": "Monthly", "description": "Pay monthly fees"},
        {"id": "quarterly", "name": "Quarterly", "description": "Pay quarterly fees (3 months)"},
        {"id": "half_yearly", "name": "Half Yearly", "description": "Pay half-yearly fees (6 months)"},
        {"id": "yearly", "name": "Yearly", "description": "Pay full year fees"}
    ]

    # Define months for payment tracking
    months = [
        {"id": 1, "name": "January", "short": "Jan"},
        {"id": 2, "name": "February", "short": "Feb"},
        {"id": 3, "name": "March", "short": "Mar"},
        {"id": 4, "name": "April", "short": "Apr"},
        {"id": 5, "name": "May", "short": "May"},
        {"id": 6, "name": "June", "short": "Jun"},
        {"id": 7, "name": "July", "short": "Jul"},
        {"id": 8, "name": "August", "short": "Aug"},
        {"id": 9, "name": "September", "short": "Sep"},
        {"id": 10, "name": "October", "short": "Oct"},
        {"id": 11, "name": "November", "short": "Nov"},
        {"id": 12, "name": "December", "short": "Dec"}
    ]

    return {
        "session_years": [{"id": sy.id, "name": sy.name, "is_current": getattr(sy, 'is_current', False)} for sy in session_years],
        "classes": [{"id": c.id, "name": c.name, "description": getattr(c, 'description', c.name)} for c in classes],
        "payment_statuses": [{"id": ps.id, "name": ps.name, "color_code": getattr(ps, 'color_code', '#000000')} for ps in payment_statuses],
        "payment_methods": [{"id": pm.id, "name": pm.name, "requires_reference": getattr(pm, 'requires_reference', False)} for pm in payment_methods],
        "genders": [{"id": g.id, "name": g.name} for g in genders],
        "user_types": [{"id": ut.id, "name": ut.name} for ut in user_types],
        "payment_frequencies": payment_frequencies,
        "months": months,
        "current_session_year": {"id": 4, "name": "2025-26"},
        "current_month": date.today().month,
        "current_year": date.today().year
    }


@router.get("/students-due")
async def get_students_with_due_fees(
    session_year: Optional[SessionYearEnum] = SessionYearEnum.YEAR_2025_26,
    frequency: Optional[str] = Query("monthly", description="Payment frequency: monthly, quarterly, half_yearly, yearly"),
    class_id: Optional[int] = None,
    search: Optional[str] = Query(None, description="Search by student name or admission number"),
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all students with their fee due status based on selected frequency
    Shows monthly/quarterly/half-yearly/yearly fee status for each student
    """
    from app.crud import student_crud
    from datetime import datetime, date
    import calendar

    # Get current date info
    current_date = date.today()
    current_month = current_date.month
    current_year = current_date.year

    # Get students with filters
    students_query = select(Student).options(
        joinedload(Student.class_ref)
    ).where(Student.is_active == True)

    if class_id:
        students_query = students_query.where(Student.class_id == class_id)

    if search:
        students_query = students_query.where(
            or_(
                func.concat(Student.first_name, ' ', Student.last_name).ilike(f"%{search}%"),
                Student.admission_number.ilike(f"%{search}%")
            )
        )

    # Get total count
    count_result = await db.execute(select(func.count(Student.id)).where(students_query.whereclause))
    total = count_result.scalar()

    # Get paginated students
    skip = (page - 1) * per_page
    students_result = await db.execute(
        students_query.offset(skip).limit(per_page)
    )
    students = students_result.scalars().all()

    # Process each student's fee status
    students_with_fees = []
    for student in students:
        # Get student's fee structure
        fee_structure = await fee_structure_crud.get_by_class_and_session(
            db,
            class_name=student.class_ref.name if student.class_ref else "",
            session_year=session_year.value
        )

        if not fee_structure:
            continue

        # Calculate monthly fee amount
        monthly_fee = float(fee_structure.total_annual_fee) / 12

        # Get student's payment history
        payments_query = select(FeePaymentModel).join(FeeRecordModel).where(
            and_(
                FeeRecordModel.student_id == student.id,
                FeeRecordModel.session_year_id == 4  # 2025-26
            )
        )
        payments_result = await db.execute(payments_query)
        payments = payments_result.scalars().all()

        # Calculate fee status based on frequency
        fee_status = calculate_fee_status(
            frequency, monthly_fee, payments, current_date, fee_structure.total_annual_fee
        )

        student_data = {
            "id": student.id,
            "admission_number": student.admission_number,
            "name": f"{student.first_name} {student.last_name}",
            "class": student.class_ref.name if student.class_ref else "Unknown",
            "section": student.section,
            "phone": student.phone,
            "email": student.email,
            "monthly_fee": monthly_fee,
            "annual_fee": float(fee_structure.total_annual_fee),
            "fee_status": fee_status,
            "total_paid": sum(p.amount for p in payments),
            "total_due": fee_status.get("total_due", 0),
            "overdue_amount": fee_status.get("overdue_amount", 0),
            "status_summary": fee_status.get("status", "Unknown")
        }

        students_with_fees.append(student_data)

    total_pages = math.ceil(total / per_page)

    return {
        "students": students_with_fees,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "frequency": frequency,
        "session_year": session_year.value,
        "current_month": current_month,
        "current_year": current_year
    }


def calculate_fee_status(frequency: str, monthly_fee: float, payments: list, current_date: date, annual_fee: float):
    """Calculate fee status based on payment frequency"""
    from datetime import datetime
    import calendar

    current_month = current_date.month
    current_year = current_date.year

    # Calculate total paid amount
    total_paid = sum(p.amount for p in payments)

    if frequency == "monthly":
        # For monthly, check each month from April to current month
        months_status = []
        total_due = 0
        overdue_amount = 0

        # Academic year starts from April
        start_month = 4  # April
        months_to_check = []

        # Generate months from April of current academic year
        for i in range(12):
            month = ((start_month - 1 + i) % 12) + 1
            year = current_year if month >= start_month else current_year + 1
            months_to_check.append((month, year))

            # Only check up to current month
            if month == current_month and year == current_year:
                break

        for month, year in months_to_check:
            month_due = monthly_fee
            month_paid = 0  # Calculate from payments for this month

            if month_paid >= month_due:
                status = "paid"
            elif month_paid > 0:
                status = "partial"
            elif month < current_month or year < current_year:
                status = "overdue"
                overdue_amount += (month_due - month_paid)
            else:
                status = "pending"

            total_due += month_due

            months_status.append({
                "month": month,
                "year": year,
                "month_name": calendar.month_name[month],
                "due_amount": month_due,
                "paid_amount": month_paid,
                "status": status
            })

        return {
            "type": "monthly",
            "months": months_status,
            "total_due": total_due,
            "total_paid": total_paid,
            "overdue_amount": overdue_amount,
            "status": "overdue" if overdue_amount > 0 else ("paid" if total_paid >= total_due else "pending")
        }

    elif frequency == "quarterly":
        # For quarterly, divide year into 4 quarters
        quarterly_fee = annual_fee / 4
        quarters = [
            {"name": "Q1 (Apr-Jun)", "months": [4, 5, 6], "due": quarterly_fee},
            {"name": "Q2 (Jul-Sep)", "months": [7, 8, 9], "due": quarterly_fee},
            {"name": "Q3 (Oct-Dec)", "months": [10, 11, 12], "due": quarterly_fee},
            {"name": "Q4 (Jan-Mar)", "months": [1, 2, 3], "due": quarterly_fee}
        ]

        quarters_status = []
        total_due = 0
        overdue_amount = 0

        for quarter in quarters:
            # Check if this quarter is due based on current date
            is_due = any(month <= current_month for month in quarter["months"])

            if is_due:
                quarter_paid = 0  # Calculate from payments
                quarter_due = quarter["due"]

                if quarter_paid >= quarter_due:
                    status = "paid"
                elif quarter_paid > 0:
                    status = "partial"
                else:
                    # Check if overdue (past the quarter end)
                    last_month = max(quarter["months"])
                    if current_month > last_month:
                        status = "overdue"
                        overdue_amount += (quarter_due - quarter_paid)
                    else:
                        status = "pending"

                total_due += quarter_due

                quarters_status.append({
                    "quarter": quarter["name"],
                    "months": quarter["months"],
                    "due_amount": quarter_due,
                    "paid_amount": quarter_paid,
                    "status": status
                })

        return {
            "type": "quarterly",
            "quarters": quarters_status,
            "total_due": total_due,
            "total_paid": total_paid,
            "overdue_amount": overdue_amount,
            "status": "overdue" if overdue_amount > 0 else ("paid" if total_paid >= total_due else "pending")
        }

    elif frequency == "half_yearly":
        # For half-yearly, divide into 2 halves
        half_yearly_fee = annual_fee / 2
        halves = [
            {"name": "First Half (Apr-Sep)", "months": [4, 5, 6, 7, 8, 9], "due": half_yearly_fee},
            {"name": "Second Half (Oct-Mar)", "months": [10, 11, 12, 1, 2, 3], "due": half_yearly_fee}
        ]

        # Similar logic as quarterly
        return {
            "type": "half_yearly",
            "halves": [],  # Implement similar to quarterly
            "total_due": annual_fee if current_month >= 4 else half_yearly_fee,
            "total_paid": total_paid,
            "overdue_amount": 0,
            "status": "paid" if total_paid >= annual_fee else "pending"
        }

    else:  # yearly
        return {
            "type": "yearly",
            "total_due": annual_fee,
            "total_paid": total_paid,
            "overdue_amount": max(0, annual_fee - total_paid) if current_month > 6 else 0,  # Overdue after 6 months
            "status": "paid" if total_paid >= annual_fee else ("overdue" if current_month > 6 else "pending")
        }


@router.get("/summary")
async def get_fee_summary(
    session_year: Optional[SessionYearEnum] = SessionYearEnum.YEAR_2025_26,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get comprehensive fee collection summary for the dashboard
    Shows total collected, pending, overdue amounts and student counts before any filters
    """
    from datetime import datetime, date

    current_date = date.today()
    current_month = current_date.month

    # Get all active students for the session
    students_query = select(Student).options(
        joinedload(Student.class_ref)
    ).where(
        and_(
            Student.is_active == True,
            Student.session_year_id == 4  # 2025-26
        )
    )

    students_result = await db.execute(students_query)
    students = students_result.scalars().all()

    # Initialize summary counters
    summary = {
        "total_students": len(students),
        "total_expected_amount": 0,
        "total_collected_amount": 0,
        "total_pending_amount": 0,
        "total_overdue_amount": 0,
        "students_paid": 0,
        "students_partial": 0,
        "students_pending": 0,
        "students_overdue": 0,
        "monthly_breakdown": [],
        "class_wise_summary": {},
        "collection_efficiency": 0
    }

    # Get all payments for the session
    payments_query = select(FeePaymentModel).join(FeeRecordModel).where(
        FeeRecordModel.session_year_id == 4  # 2025-26
    )
    payments_result = await db.execute(payments_query)
    all_payments = payments_result.scalars().all()

    total_collected = sum(p.amount for p in all_payments)
    summary["total_collected_amount"] = float(total_collected)

    # Process each student
    for student in students:
        # Get student's fee structure
        fee_structure = await fee_structure_crud.get_by_class_and_session(
            db,
            class_name=student.class_ref.name if student.class_ref else "",
            session_year=session_year.value
        )

        if not fee_structure:
            continue

        annual_fee = float(fee_structure.total_annual_fee)
        monthly_fee = annual_fee / 12

        summary["total_expected_amount"] += annual_fee

        # Get student's payments
        student_payments = [p for p in all_payments if any(
            fr.student_id == student.id for fr in [p.fee_record] if fr
        )]

        student_paid = sum(p.amount for p in student_payments)

        # Calculate months due up to current month
        months_due = current_month - 3 if current_month >= 4 else current_month + 9  # Academic year starts April
        expected_till_now = monthly_fee * months_due

        # Determine student status
        if student_paid >= expected_till_now:
            summary["students_paid"] += 1
        elif student_paid > 0:
            if student_paid < expected_till_now * 0.5:  # Less than 50% paid
                summary["students_overdue"] += 1
                summary["total_overdue_amount"] += (expected_till_now - student_paid)
            else:
                summary["students_partial"] += 1
        else:
            if months_due > 0:
                summary["students_overdue"] += 1
                summary["total_overdue_amount"] += expected_till_now
            else:
                summary["students_pending"] += 1

        # Class-wise summary
        class_name = student.class_ref.name if student.class_ref else "Unknown"
        if class_name not in summary["class_wise_summary"]:
            summary["class_wise_summary"][class_name] = {
                "total_students": 0,
                "total_expected": 0,
                "total_collected": 0,
                "students_paid": 0,
                "students_pending": 0
            }

        summary["class_wise_summary"][class_name]["total_students"] += 1
        summary["class_wise_summary"][class_name]["total_expected"] += annual_fee
        summary["class_wise_summary"][class_name]["total_collected"] += student_paid

        if student_paid >= expected_till_now:
            summary["class_wise_summary"][class_name]["students_paid"] += 1
        else:
            summary["class_wise_summary"][class_name]["students_pending"] += 1

    # Calculate pending amount
    summary["total_pending_amount"] = summary["total_expected_amount"] - summary["total_collected_amount"] - summary["total_overdue_amount"]

    # Calculate collection efficiency
    if summary["total_expected_amount"] > 0:
        summary["collection_efficiency"] = round(
            (summary["total_collected_amount"] / summary["total_expected_amount"]) * 100, 2
        )

    # Monthly breakdown for current academic year
    for month in range(1, 13):
        month_name = calendar.month_name[month]
        # Calculate expected collection for this month
        expected_for_month = summary["total_students"] * (summary["total_expected_amount"] / summary["total_students"] / 12) if summary["total_students"] > 0 else 0

        # Get actual collections for this month (simplified)
        actual_for_month = 0  # Would need to calculate from payment dates

        summary["monthly_breakdown"].append({
            "month": month,
            "month_name": month_name,
            "expected": float(expected_for_month),
            "collected": float(actual_for_month),
            "efficiency": round((actual_for_month / expected_for_month * 100), 2) if expected_for_month > 0 else 0
        })

    return {
        "summary": summary,
        "session_year": session_year.value,
        "current_month": current_month,
        "generated_at": current_date
    }


@router.post("/pay-monthly-enhanced/{student_id}")
async def pay_monthly_enhanced(
    student_id: int,
    payment_data: dict,  # {"amount": float, "payment_method_id": int, "selected_months": [4,5,6], "session_year": str, "transaction_id": str, "remarks": str}
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Enhanced monthly fee payment system that:
    1. Accepts any payment amount (full/partial/multi-month)
    2. Automatically allocates to months (e.g., 3200 rs = 3 full months + 200 rs partial)
    3. Prevents duplicate payments for already-paid months
    4. Supports session year filtering
    5. Allows admin to select specific months to pay

    Example: 3200 rs for 1000/month = 3 full months + 200 rs partial for 4th month
    """

    # Extract payment data
    amount = float(payment_data.get("amount", 0))
    payment_method_id = payment_data.get("payment_method_id", 1)  # Default to CASH (ID: 1)
    selected_months = payment_data.get("selected_months", [])  # Can be month names or numbers
    session_year = payment_data.get("session_year", "2025-26")
    transaction_id = payment_data.get("transaction_id")
    remarks = payment_data.get("remarks", "")

    # Parse payment date (defaults to today)
    payment_date_str = payment_data.get("payment_date")
    if payment_date_str:
        try:
            payment_date = datetime.strptime(payment_date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            payment_date = date.today()
    else:
        payment_date = date.today()

    # Ensure payment_method_id is a valid integer
    if not isinstance(payment_method_id, int):
        try:
            payment_method_id = int(payment_method_id)
        except (ValueError, TypeError):
            payment_method_id = 1  # Default to CASH (ID: 1)

    # Validate payment_method_id is in valid range (1-6 based on our configuration)
    if payment_method_id < 1 or payment_method_id > 6:
        payment_method_id = 1  # Default to CASH (ID: 1)

    # Month name to number mapping
    month_name_to_number = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }

    # Convert month names to numbers if needed
    month_numbers = []
    for month in selected_months:
        if isinstance(month, str):
            month_num = month_name_to_number.get(month)
            if month_num:
                month_numbers.append(month_num)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid month name: {month}"
                )
        elif isinstance(month, int):
            if 1 <= month <= 12:
                month_numbers.append(month)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid month number: {month}. Must be between 1 and 12"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid month format: {month}. Must be month name or number"
            )

    # Validate inputs
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount must be greater than 0"
        )

    if not payment_method_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment method is required"
        )

    if not month_numbers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one valid month must be selected"
        )

    # Use month_numbers for the rest of the function
    selected_months = month_numbers

    # Get student
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Get session year ID and derive start year from session year name
    session_year_mapping = {
        "2022-23": 1, "2023-24": 2, "2024-25": 3, "2025-26": 4, "2026-27": 5
    }
    session_year_id = session_year_mapping.get(session_year, 4)

    # Derive the start year from the session year name (e.g., "2026-27" -> 2026)
    # This ensures correct year calculation for any session year (past, current, or future)
    session_start_year = int(session_year.split("-")[0])

    # Get student's fee structure to calculate monthly fee
    fee_structure = await fee_structure_crud.get_by_class_id_and_session_id(
        db,
        class_id=student.class_id,
        session_year_id=session_year_id
    )

    if not fee_structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fee structure not found for student's class"
        )

    monthly_fee = float(fee_structure.total_annual_fee) / 12

    # Get existing monthly tracking records for selected months
    existing_tracking = await db.execute(
        select(MonthlyFeeTrackingModel)
        .where(
            and_(
                MonthlyFeeTrackingModel.student_id == student_id,
                MonthlyFeeTrackingModel.session_year_id == session_year_id,
                MonthlyFeeTrackingModel.academic_month.in_(selected_months)
            )
        )
        .order_by(MonthlyFeeTrackingModel.academic_month)
    )
    tracking_records = existing_tracking.scalars().all()

    # Check for already fully paid months
    fully_paid_months = []
    available_months = []

    for record in tracking_records:
        if float(record.paid_amount) >= float(record.monthly_amount):
            fully_paid_months.append({
                "month": record.academic_month,
                "month_name": calendar.month_name[record.academic_month],
                "paid_amount": float(record.paid_amount),
                "monthly_amount": float(record.monthly_amount)
            })
        else:
            available_months.append(record)

    # If some months are already fully paid, inform the user
    if fully_paid_months:
        paid_month_names = [m["month_name"] for m in fully_paid_months]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The following months are already fully paid: {', '.join(paid_month_names)}. Please select different months."
        )

    # If no tracking records exist for selected months, create them
    if not available_months:
        # Get or create fee record first
        existing_fee_record = await fee_record_crud.get_by_student_session_type(
            db, student_id=student_id, session_year_id=session_year_id, payment_type_id=1
        )

        if not existing_fee_record:
            # Create new fee record
            fee_record_data = FeeRecordCreate(
                student_id=student_id,
                session_year_id=session_year_id,
                class_id=student.class_id,  # Get class_id from student record
                payment_type_id=1,  # Monthly
                payment_status_id=1,  # Pending
                payment_method_id=payment_method_id,
                fee_structure_id=fee_structure.id,
                is_monthly_tracked=True,
                total_amount=fee_structure.total_annual_fee,
                paid_amount=0,
                balance_amount=fee_structure.total_annual_fee,
                due_date=date(session_start_year, 4, 30),
                remarks="Enhanced monthly payment system"
            )
            fee_record = await fee_record_crud.create(db, obj_in=fee_record_data)
        else:
            fee_record = existing_fee_record

        # Create monthly tracking records for selected months
        available_months = []
        for month in selected_months:
            # Calculate due date (10th of each month) using session_start_year
            # April-December = start_year, January-March = start_year + 1
            year = session_start_year if month >= 4 else session_start_year + 1
            due_date = date(year, month, 10)

            monthly_tracking = MonthlyFeeTrackingModel(
                fee_record_id=fee_record.id,
                student_id=student_id,
                session_year_id=session_year_id,
                academic_month=month,
                academic_year=year,
                month_name=calendar.month_name[month],
                monthly_amount=monthly_fee,
                paid_amount=0,
                due_date=due_date,
                payment_status_id=1  # Pending
            )
            db.add(monthly_tracking)
            available_months.append(monthly_tracking)

        await db.commit()
        # Refresh to get IDs
        for record in available_months:
            await db.refresh(record)

    # Now allocate the payment amount to available months
    # Sort months by academic order (April = 4 first, March = 3 last)
    available_months.sort(key=lambda x: x.academic_month if x.academic_month >= 4 else x.academic_month + 12)

    # First, calculate how much can actually be allocated
    total_allocatable = 0
    for month_record in available_months:
        month_balance = float(month_record.monthly_amount) - float(month_record.paid_amount)
        total_allocatable += month_balance

    # The actual amount to process is the minimum of payment amount and allocatable amount
    actual_amount_to_process = min(amount, total_allocatable)

    # Create the payment record with the actual amount that will be processed
    payment_data = FeePaymentCreate(
        fee_record_id=available_months[0].fee_record_id,
        amount=actual_amount_to_process,  # Use actual processable amount
        payment_method_id=payment_method_id,  # Use payment_method_id directly (integer)
        payment_date=payment_date,  # Use payment_date from request (defaults to today)
        transaction_id=transaction_id,
        remarks=f"Enhanced monthly payment: {remarks}" if remarks else "Enhanced monthly payment"
    )

    # Create the payment record using CRUD
    payment = await fee_payment_crud.create(db, obj_in=payment_data)

    # Allocate payment to months using the smart allocation logic
    remaining_amount = actual_amount_to_process  # Use the actual processable amount
    allocations = []
    payment_breakdown = []
    total_allocated = 0

    for month_record in available_months:
        if remaining_amount <= 0:
            break

        # Calculate how much this month needs
        month_balance = float(month_record.monthly_amount) - float(month_record.paid_amount)

        # Allocate the minimum of remaining amount or month balance
        allocation_amount = min(remaining_amount, month_balance)

        if allocation_amount > 0:
            # Create allocation record
            allocations.append({
                "monthly_tracking_id": month_record.id,
                "amount": allocation_amount
            })

            # Track for response
            payment_breakdown.append({
                "month": month_record.academic_month,
                "month_name": month_record.month_name,
                "monthly_fee": float(month_record.monthly_amount),
                "previous_paid": float(month_record.paid_amount),
                "allocated_amount": allocation_amount,
                "new_paid_amount": float(month_record.paid_amount) + allocation_amount,
                "remaining_balance": month_balance - allocation_amount,
                "status": "Paid" if (month_balance - allocation_amount) <= 0.01 else "Partial"
            })

            remaining_amount -= allocation_amount
            total_allocated += allocation_amount

    # Process the allocations
    if allocations:
        await monthly_payment_allocation_crud.allocate_payment_to_months(
            db, payment.id, allocations
        )

    # Update the main fee record with the payment amount (should equal total_allocated now)
    fee_record = await fee_record_crud.get(db, id=available_months[0].fee_record_id)
    # Convert allocated amount to Decimal for compatibility with database field
    from decimal import Decimal

    # Verify that payment amount equals total allocated (they should be equal now)
    if abs(float(payment.amount) - total_allocated) > 0.01:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment amount (₹{payment.amount}) does not match allocated amount (₹{total_allocated})"
        )

    fee_record.paid_amount += Decimal(str(payment.amount))  # Use payment amount for consistency
    fee_record.balance_amount = fee_record.total_amount - fee_record.paid_amount

    # Update payment status
    if fee_record.balance_amount <= 0:
        fee_record.payment_status_id = 2  # PAID
        fee_record.balance_amount = 0
    elif fee_record.paid_amount > 0:
        fee_record.payment_status_id = 3  # PARTIAL

    await db.commit()
    await db.refresh(fee_record)
    await db.refresh(payment)

    # Calculate summary
    total_months_affected = len(payment_breakdown)
    fully_paid_months = len([m for m in payment_breakdown if m["status"] == "Paid"])
    partial_months = len([m for m in payment_breakdown if m["status"] == "Partial"])

    # Calculate any remaining amount that couldn't be processed
    remaining_unprocessed = amount - actual_amount_to_process

    # Generate receipt PDF and upload to Cloudinary
    receipt_url = None
    receipt_number = None
    try:
        logger.info(f"Generating receipt for payment {payment.id}")

        # Get payment method description
        payment_method = await payment_method_crud.get_by_id_async(db, id=payment_method_id)
        payment_method_desc = payment_method.description if payment_method else "Cash"

        # Generate receipt number
        receipt_number = f"FEE-{payment.id:06d}"

        # Prepare payment data for receipt (enhanced with payment_date_str)
        payment_date_str = payment.payment_date.strftime('%d-%b-%Y') if payment.payment_date else 'N/A'
        payment_data = {
            'id': payment.id,
            'amount': float(payment.amount),
            'payment_method': payment_method_desc,
            'payment_date': payment.payment_date,
            'payment_date_str': payment_date_str,
            'transaction_id': payment.transaction_id or 'N/A',
            'receipt_number': receipt_number
        }

        # Prepare student data for receipt (enhanced with address and mobile)
        student_data = {
            'name': f"{student.first_name} {student.last_name}",
            'admission_number': student.admission_number,
            'class_name': f"{student.class_ref.description} - {student.section}" if student.class_ref and student.section else (student.class_ref.description if student.class_ref else 'N/A'),
            'roll_number': student.roll_number or 'N/A',
            'father_name': student.father_name,
            'mobile': student.father_phone or student.phone or 'N/A',
            'father_phone': student.father_phone or 'N/A',
            'address': student.address or ''
        }

        # Prepare fee summary
        fee_summary = {
            'total_annual_fee': float(fee_record.total_amount),
            'total_paid': float(fee_record.paid_amount),
            'balance_remaining': float(fee_record.balance_amount)
        }

        # Check if student has transport enrollment for current session
        transport_data = None
        try:
            from app.crud.crud_transport import student_transport_enrollment_crud
            transport_enrollment = await db.execute(
                select(StudentTransportEnrollment)
                .where(StudentTransportEnrollment.student_id == student.id)
                .where(StudentTransportEnrollment.session_year_id == fee_record.session_year_id)
                .where(StudentTransportEnrollment.is_active == True)
            )
            enrollment = transport_enrollment.scalar_one_or_none()

            if enrollment:
                # Get transport payment summary
                from app.models.transport import TransportMonthlyTracking
                transport_summary = await db.execute(
                    select(
                        func.sum(TransportMonthlyTracking.monthly_amount).label('total_amount'),
                        func.sum(TransportMonthlyTracking.paid_amount).label('total_paid')
                    )
                    .where(TransportMonthlyTracking.enrollment_id == enrollment.id)
                    .where(TransportMonthlyTracking.is_service_enabled == True)
                )
                summary = transport_summary.one()

                total_transport = float(summary.total_amount or 0)
                paid_transport = float(summary.total_paid or 0)
                balance_transport = total_transport - paid_transport

                # Get paid months
                paid_months_query = await db.execute(
                    select(TransportMonthlyTracking.month_name)
                    .where(TransportMonthlyTracking.enrollment_id == enrollment.id)
                    .where(TransportMonthlyTracking.payment_status_id == 2)  # Paid status
                    .order_by(TransportMonthlyTracking.academic_month)
                )
                paid_months = [row[0] for row in paid_months_query.fetchall()]

                transport_data = {
                    'monthly_fee': float(enrollment.monthly_fee),
                    'total_paid': paid_transport,
                    'balance': balance_transport,
                    'months_covered': paid_months
                }
        except Exception as transport_error:
            logger.warning(f"Could not fetch transport data: {str(transport_error)}")
            # Continue without transport data

        # Get admin user name who processed the payment
        created_by_name = f"{current_user.first_name} {current_user.last_name}" if current_user else None

        # Generate receipt PDF (enhanced with transport data and created_by_name)
        receipt_generator = ReceiptGenerator()
        pdf_buffer = receipt_generator.generate_receipt(
            payment_data=payment_data,
            student_data=student_data,
            month_breakdown=payment_breakdown,
            fee_summary=fee_summary,
            transport_data=transport_data,
            created_by_name=created_by_name
        )

        # Upload to Cloudinary
        cloudinary_service = CloudinaryReceiptService()
        receipt_url, cloudinary_public_id = cloudinary_service.upload_receipt(
            pdf_buffer=pdf_buffer,
            payment_id=payment.id,
            receipt_number=receipt_number
        )

        # Update payment record with receipt information
        payment.receipt_number = receipt_number
        payment.receipt_cloudinary_url = receipt_url
        payment.receipt_cloudinary_id = cloudinary_public_id

        await db.commit()
        await db.refresh(payment)

        logger.info(f"Receipt generated and uploaded successfully: {receipt_url}")

    except Exception as e:
        # Log error but don't fail the payment
        logger.error(f"Failed to generate/upload receipt: {str(e)}")
        import traceback
        traceback.print_exc()
        # Continue with payment response even if receipt generation fails

    # Generate alert for fee payment
    try:
        # Get payment method description
        payment_method = await payment_method_crud.get_by_id_async(db, id=payment_method_id)
        payment_method_desc = payment_method.description if payment_method else "Cash"

        # Get current user name
        actor_name = f"{current_user.first_name} {current_user.last_name}" if current_user.first_name else "Admin"

        # Build months paid string using month names
        months_paid_list = [m["month_name"] for m in payment_breakdown]
        months_paid_str = ", ".join(months_paid_list) if months_paid_list else None

        print(f"Creating fee payment alert for student {student.id}, payment {payment.id}")
        await alert_service.create_fee_payment_alert(
            db,
            payment_id=payment.id,
            student_id=student.id,
            student_name=f"{student.first_name} {student.last_name}",
            class_name=student.class_ref.description if student.class_ref else "Unknown",
            amount=float(actual_amount_to_process),
            payment_method=payment_method_desc,
            fee_type='TUITION',
            months_paid=months_paid_str,
            actor_user_id=current_user.id,
            actor_name=actor_name
        )
        print(f"Fee payment alert created successfully")
    except Exception as e:
        # Log error but don't fail the payment
        import traceback
        print(f"Failed to create fee payment alert: {e}")
        traceback.print_exc()

    # =====================================================
    # WhatsApp Notification - Using approved media template
    # Template: school_fee_media_template_v1 (4 variables)
    # Sends receipt PDF attachment with clickable link
    # =====================================================
    whatsapp_result = None
    whatsapp_status = None
    whatsapp_error = None
    try:
        # Check available phone numbers in priority order: father > mother > guardian > student
        contact_phone = None
        for phone_field in [student.father_phone, student.mother_phone, student.guardian_phone, student.phone]:
            is_valid, validated_phone = whatsapp_service.validate_phone_number(phone_field)
            if is_valid and validated_phone:
                contact_phone = validated_phone
                break

        if contact_phone:
            # Send WhatsApp notification using media receipt template (with PDF attachment)
            whatsapp_result = await whatsapp_service.send_fee_media_receipt(
                phone_number=contact_phone,
                student_name=f"{student.first_name} {student.last_name}",
                amount=float(actual_amount_to_process),
                receipt_url=receipt_url,
                payment_id=payment.id
            )

            logger.info(f"WhatsApp notification sent for payment {payment.id}: {whatsapp_result}")
            whatsapp_status = whatsapp_result.get("status", "UNKNOWN")
            whatsapp_error = whatsapp_result.get("error")
        else:
            whatsapp_status = "NO_PHONE"
            whatsapp_error = "No valid phone number available (checked father, mother, guardian, student)"
            logger.info(f"WhatsApp not sent for payment {payment.id}: No valid phone number")

    except Exception as e:
        import traceback
        logger.error(f"Failed to send WhatsApp notification for payment {payment.id}: {e}")
        traceback.print_exc()
        whatsapp_status = "ERROR"
        whatsapp_error = str(e)[:500]

    return {
        "success": True,
        "message": f"Payment of ₹{actual_amount_to_process} processed: ₹{total_allocated} allocated across {total_months_affected} month(s)" + (f", ₹{remaining_unprocessed} could not be processed (no pending amounts)" if remaining_unprocessed > 0 else ""),
        "payment_id": payment.id,
        "original_amount": amount,
        "processed_amount": actual_amount_to_process,
        "remaining_unprocessed": remaining_unprocessed,
        "receipt": {
            "available": receipt_url is not None,
            "receipt_number": receipt_number,
            "receipt_url": receipt_url
        },
        "student": {
            "id": student.id,
            "name": f"{student.first_name} {student.last_name}",
            "admission_number": student.admission_number,
            "class": student.class_ref.name if student.class_ref else "Unknown"
        },
        "payment_summary": {
            "total_amount": amount,
            "amount_allocated": total_allocated,
            "amount_remaining": amount - total_allocated,
            "months_affected": total_months_affected,
            "fully_paid_months": fully_paid_months,
            "partial_months": partial_months,
            "transaction_id": transaction_id,
            "payment_date": payment_date.isoformat()
        },
        "month_wise_breakdown": payment_breakdown,
        "updated_balance": {
            "total_annual_fee": float(fee_record.total_amount),
            "total_paid": float(fee_record.paid_amount),
            "balance_remaining": float(fee_record.balance_amount),
            "payment_status": "Paid" if fee_record.balance_amount <= 0 else ("Partial" if fee_record.paid_amount > 0 else "Pending")
        },
        "whatsapp_notification": {
            "sent": whatsapp_result.get("success", False) if whatsapp_result else False,
            "status": whatsapp_result.get("status") if whatsapp_result else whatsapp_status,
            "message_sid": whatsapp_result.get("message_sid") if whatsapp_result else None,
            "phone_number": student.phone if student.phone else None,
            "error": whatsapp_result.get("error") if whatsapp_result else whatsapp_error
        }
    }


@router.post("/pay-combined/{student_id}")
async def pay_combined_tuition_transport(
    student_id: int,
    payment_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Combined tuition + transport fee payment endpoint.
    Processes both tuition and transport payments in a single transaction
    and generates a unified receipt with both payment details.

    Expected payment_data format:
    {
        "tuition": {
            "amount": float,
            "payment_method_id": int,
            "selected_months": [4, 5, 6],
            "session_year": "2025-26",
            "transaction_id": "TXN123",
            "remarks": "Monthly fee payment",
            "payment_date": "2026-01-29"  # Optional, defaults to today
        },
        "transport": {
            "amount": float,
            "selected_months": [4, 5, 6],  # academic month numbers
            "session_year_id": int,
            "payment_date": "2026-01-29"  # Optional, defaults to today
        }
    }
    """
    from decimal import Decimal
    from app.models.transport import StudentTransportEnrollment, TransportMonthlyTracking, TransportPayment, TransportPaymentAllocation
    from sqlalchemy.orm import selectinload

    tuition_data = payment_data.get("tuition", {})
    transport_data = payment_data.get("transport", {})

    # Validate tuition data
    tuition_amount = float(tuition_data.get("amount", 0))
    tuition_payment_method_id = tuition_data.get("payment_method_id", 1)
    tuition_selected_months = tuition_data.get("selected_months", [])
    session_year = tuition_data.get("session_year", "2025-26")
    transaction_id = tuition_data.get("transaction_id", f"TXN{datetime.now().timestamp()}")
    remarks = tuition_data.get("remarks", "")

    # Parse payment date from tuition data (defaults to today)
    payment_date_str = tuition_data.get("payment_date")
    if payment_date_str:
        try:
            payment_date = datetime.strptime(payment_date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            payment_date = date.today()
    else:
        payment_date = date.today()

    # Validate transport data
    transport_amount = float(transport_data.get("amount", 0))
    transport_selected_months = transport_data.get("selected_months", [])
    transport_session_year_id = transport_data.get("session_year_id", 4)  # Default to 2025-26

    if tuition_amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tuition payment amount must be greater than 0"
        )

    if not tuition_selected_months:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one tuition month must be selected"
        )

    if transport_amount <= 0 or not transport_selected_months:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transport payment amount and months are required for combined payment"
        )

    # Get session year ID and derive start year from session year name
    session_year_mapping = {
        "2022-23": 1, "2023-24": 2, "2024-25": 3, "2025-26": 4, "2026-27": 5
    }
    session_year_id = session_year_mapping.get(session_year, 4)

    # Derive the start year from the session year name (e.g., "2026-27" -> 2026)
    # This ensures correct year calculation for any session year (past, current, or future)
    session_start_year = int(session_year.split("-")[0])

    # Get student with class relationship
    student = await db.execute(
        select(Student)
        .options(selectinload(Student.class_ref))
        .where(Student.id == student_id)
    )
    student = student.scalar_one_or_none()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # =====================================================
    # PART 1: Process Tuition Fee Payment
    # =====================================================

    # Get fee structure
    fee_structure = await fee_structure_crud.get_by_class_id_and_session_id(
        db, class_id=student.class_id, session_year_id=session_year_id
    )

    if not fee_structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fee structure not found for student's class"
        )

    monthly_fee = float(fee_structure.total_annual_fee) / 12

    # =====================================================
    # STEP 1: Get existing tracking records for selected months
    # =====================================================

    # Query for existing tracking records for the selected months
    existing_tracking = await db.execute(
        select(MonthlyFeeTrackingModel)
        .where(
            and_(
                MonthlyFeeTrackingModel.student_id == student_id,
                MonthlyFeeTrackingModel.session_year_id == session_year_id,
                MonthlyFeeTrackingModel.academic_month.in_(tuition_selected_months)
            )
        )
        .order_by(MonthlyFeeTrackingModel.academic_month)
    )
    tuition_tracking_records = list(existing_tracking.scalars().all())

    # =====================================================
    # STEP 2: Find or create the fee record
    # =====================================================

    # First, check if there's ANY existing tracking record for this student/session
    # This helps us find the correct fee_record_id even if selected months don't have records yet
    any_tracking_query = await db.execute(
        select(MonthlyFeeTrackingModel)
        .where(
            and_(
                MonthlyFeeTrackingModel.student_id == student_id,
                MonthlyFeeTrackingModel.session_year_id == session_year_id
            )
        )
        .limit(1)
    )
    any_tracking_record = any_tracking_query.scalars().first()

    # Get or create fee record
    fee_record = None

    # If we found any existing tracking record, use its fee_record_id
    if any_tracking_record:
        fee_record_query = await db.execute(
            select(FeeRecordModel).where(FeeRecordModel.id == any_tracking_record.fee_record_id)
        )
        fee_record = fee_record_query.scalars().first()

    # If no fee record found from tracking records, try the standard lookup
    if not fee_record:
        fee_record = await fee_record_crud.get_by_student_session_type(
            db, student_id=student_id, session_year_id=session_year_id, payment_type_id=1
        )

    # Only create a new fee record if none exists
    if not fee_record:
        fee_record = await fee_record_crud.create(db, obj_in=FeeRecordCreate(
            student_id=student_id,
            session_year_id=session_year_id,
            class_id=student.class_id,  # Get class_id from student record
            payment_type_id=1,  # Monthly
            payment_status_id=1,  # Pending
            payment_method_id=tuition_payment_method_id,
            fee_structure_id=fee_structure.id,
            is_monthly_tracked=True,
            total_amount=fee_structure.total_annual_fee,
            paid_amount=Decimal("0"),
            balance_amount=fee_structure.total_annual_fee,
            due_date=date(session_start_year, 4, 30),
            remarks="Combined tuition + transport payment"
        ))

    # Create tracking records for months that don't exist
    for month_num in tuition_selected_months:
        exists = any(r.academic_month == month_num for r in tuition_tracking_records)
        if not exists:
            # Calculate year for this month using session_start_year
            # April-December = start_year, January-March = start_year + 1
            year = session_start_year if month_num >= 4 else session_start_year + 1
            # Calculate due date (last day of the month)
            last_day = calendar.monthrange(year, month_num)[1]
            due_date = date(year, month_num, last_day)

            new_record = MonthlyFeeTrackingModel(
                fee_record_id=fee_record.id,
                student_id=student_id,
                session_year_id=session_year_id,
                academic_month=month_num,
                academic_year=year,
                month_name=calendar.month_name[month_num],
                monthly_amount=monthly_fee,
                paid_amount=0,
                due_date=due_date,
                payment_status_id=1  # Pending (same as original pay_monthly_enhanced)
            )
            db.add(new_record)
            tuition_tracking_records.append(new_record)

    await db.flush()

    # Filter for available months (not fully paid)
    available_tuition_months = [
        r for r in tuition_tracking_records
        if float(r.paid_amount) < float(r.monthly_amount)
    ]

    if not available_tuition_months:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected tuition months are already fully paid"
        )

    # Sort by academic month
    available_tuition_months.sort(key=lambda x: x.academic_month if x.academic_month >= 4 else x.academic_month + 12)

    # Calculate actual tuition amount to process
    total_tuition_allocatable = sum(
        float(r.monthly_amount) - float(r.paid_amount) for r in available_tuition_months
    )
    actual_tuition_amount = min(tuition_amount, total_tuition_allocatable)

    # Create tuition payment record
    tuition_payment_data = FeePaymentCreate(
        fee_record_id=fee_record.id,
        amount=actual_tuition_amount,
        payment_method_id=tuition_payment_method_id,
        payment_date=payment_date,
        transaction_id=transaction_id,
        remarks=f"Combined payment: {remarks}" if remarks else "Combined tuition + transport payment"
    )
    tuition_payment = await fee_payment_crud.create(db, obj_in=tuition_payment_data)

    # Allocate tuition payment to months
    remaining_tuition = actual_tuition_amount
    tuition_breakdown = []

    for month_record in available_tuition_months:
        if remaining_tuition <= 0:
            break

        month_balance = float(month_record.monthly_amount) - float(month_record.paid_amount)
        allocation_amount = min(remaining_tuition, month_balance)

        if allocation_amount > 0:
            # Create allocation
            allocation = MonthlyPaymentAllocation(
                fee_payment_id=tuition_payment.id,
                monthly_tracking_id=month_record.id,
                allocated_amount=allocation_amount,
                created_by=current_user.id
            )
            db.add(allocation)

            # Update tracking record - only update paid_amount (balance_amount is computed property)
            previous_paid = float(month_record.paid_amount)
            month_record.paid_amount = previous_paid + allocation_amount

            # Calculate balance for response (don't set on model - it's a computed property)
            new_balance = float(month_record.monthly_amount) - float(month_record.paid_amount)
            payment_status_text = "Paid" if new_balance <= 0.01 else "Partial"

            # Update payment_status_id (not payment_status)
            if new_balance <= 0.01:
                month_record.payment_status_id = 2  # PAID
            elif month_record.paid_amount > 0:
                month_record.payment_status_id = 3  # PARTIAL

            tuition_breakdown.append({
                "month": month_record.academic_month,
                "month_name": month_record.month_name,
                "monthly_fee": float(month_record.monthly_amount),
                "previous_paid": previous_paid,
                "allocated_amount": allocation_amount,
                "new_paid_amount": float(month_record.paid_amount),
                "remaining_balance": new_balance,
                "status": payment_status_text
            })

            remaining_tuition -= allocation_amount

    # Update fee record totals
    fee_record.paid_amount = float(fee_record.paid_amount) + actual_tuition_amount
    fee_record.balance_amount = float(fee_record.total_amount) - float(fee_record.paid_amount)

    await db.flush()

    # =====================================================
    # PART 2: Process Transport Fee Payment
    # =====================================================
    from app.models.transport import StudentTransportEnrollment as STE, TransportMonthlyTracking as TMT
    from app.models.transport import TransportPayment, TransportPaymentAllocation

    # Get active transport enrollment
    enrollment_result = await db.execute(
        select(STE)
        .options(selectinload(STE.transport_type))
        .where(
            STE.student_id == student_id,
            STE.session_year_id == transport_session_year_id,
            STE.is_active == True
        )
    )
    transport_enrollment = enrollment_result.scalar_one_or_none()

    if not transport_enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active transport enrollment found for this student"
        )

    # Get monthly tracking records for selected transport months
    transport_tracking_result = await db.execute(
        select(TMT)
        .where(
            TMT.student_id == student_id,
            TMT.session_year_id == transport_session_year_id,
            TMT.academic_month.in_(transport_selected_months),
            TMT.is_service_enabled == True
        )
        .order_by(TMT.academic_year, TMT.academic_month)
    )
    transport_monthly_records = list(transport_tracking_result.scalars().all())

    if not transport_monthly_records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No enabled transport months found for selected months"
        )

    # Filter for unpaid transport months
    unpaid_transport_records = [
        r for r in transport_monthly_records
        if Decimal(str(r.monthly_amount)) - Decimal(str(r.paid_amount)) > 0
    ]

    if not unpaid_transport_records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected transport months are already fully paid"
        )

    # Create transport payment record
    transport_payment = TransportPayment(
        enrollment_id=transport_enrollment.id,
        student_id=student_id,
        amount=transport_amount,
        payment_method_id=tuition_payment_method_id,  # Same payment method
        payment_date=payment_date,
        transaction_id=f"{transaction_id}-T",
        remarks="Combined tuition + transport payment (Transport)",
        created_by=current_user.id
    )
    db.add(transport_payment)
    await db.flush()

    # Distribute transport payment across months
    remaining_transport = Decimal(str(transport_amount))
    transport_breakdown = []

    for record in unpaid_transport_records:
        if remaining_transport <= 0:
            break

        # Capture previous paid amount BEFORE updating
        previous_paid = float(record.paid_amount)
        balance = Decimal(str(record.monthly_amount)) - Decimal(str(record.paid_amount))

        if balance > 0:
            payment_for_month = min(remaining_transport, balance)
            record.paid_amount = Decimal(str(record.paid_amount)) + payment_for_month

            # Create transport allocation record
            transport_allocation = TransportPaymentAllocation(
                transport_payment_id=transport_payment.id,
                monthly_tracking_id=record.id,
                allocated_amount=float(payment_for_month),
                is_reversal=False,
                created_by=current_user.id
            )
            db.add(transport_allocation)

            # Update payment status
            paid_rounded = record.paid_amount.quantize(Decimal('0.01'))
            monthly_rounded = Decimal(str(record.monthly_amount)).quantize(Decimal('0.01'))

            if paid_rounded >= monthly_rounded:
                record.payment_status_id = 2  # PAID
            elif record.paid_amount > 0:
                record.payment_status_id = 3  # PARTIAL

            record.updated_at = datetime.now()
            remaining_transport -= payment_for_month

            transport_breakdown.append({
                "month_name": record.month_name,
                "academic_year": record.academic_year,
                "monthly_amount": float(record.monthly_amount),
                "previous_paid": previous_paid,  # Amount paid before this transaction
                "paid_amount": float(record.paid_amount),  # Total paid after this transaction
                "balance_amount": float(Decimal(str(record.monthly_amount)) - record.paid_amount),
                "allocated_amount": float(payment_for_month),  # Amount paid in this transaction
                "status": "Paid" if paid_rounded >= monthly_rounded else "Partial"
            })

    # Commit all changes
    await db.commit()

    # Refresh records
    await db.refresh(tuition_payment)
    await db.refresh(transport_payment)
    await db.refresh(fee_record)

    # =====================================================
    # PART 3: Generate Combined Receipt
    # =====================================================
    receipt_url = None
    receipt_number = None

    # Calculate transport totals after payment (needed for both receipt and response)
    transport_total_result = await db.execute(
        select(
            func.sum(TMT.paid_amount).label('total_paid'),
            func.sum(TMT.monthly_amount - TMT.paid_amount).label('total_balance'),
            func.sum(TMT.monthly_amount).label('total_fee')
        ).where(TMT.enrollment_id == transport_enrollment.id)
    )
    transport_totals = transport_total_result.first()

    try:
        # Generate receipt number
        receipt_number = f"RCP-{tuition_payment.id:06d}"

        # Get payment method description
        payment_method = await payment_method_crud.get_by_id_async(db, id=tuition_payment_method_id)
        payment_method_name = payment_method.description if payment_method else "Cash"

        # Format payment date for receipt display
        payment_date_str = payment_date.strftime('%d-%b-%Y') if payment_date else 'N/A'

        # Prepare payment data for receipt
        receipt_payment_data = {
            'id': tuition_payment.id,
            'amount': float(actual_tuition_amount) + float(transport_amount),  # Combined total
            'tuition_amount': float(actual_tuition_amount),
            'transport_amount': float(transport_amount),
            'payment_method': payment_method_name,
            'payment_date': payment_date,
            'payment_date_str': payment_date_str,  # Formatted date string for receipt
            'transaction_id': transaction_id,
            'receipt_number': receipt_number
        }

        # Prepare student data for receipt
        student_data = {
            'name': f"{student.first_name} {student.last_name}",
            'admission_number': student.admission_number,
            'class_name': student.class_ref.description if student.class_ref else 'N/A',
            'roll_number': student.roll_number or 'N/A',
            'father_name': student.father_name,
            'phone': student.phone
        }

        # Prepare fee summary
        fee_summary = {
            'total_annual_fee': float(fee_record.total_amount),
            'total_paid': float(fee_record.paid_amount),
            'balance_remaining': float(fee_record.balance_amount)
        }

        # Prepare transport data for receipt with monthly breakdown
        transport_receipt_data = {
            'monthly_fee': float(transport_enrollment.monthly_fee),
            'total_fee': float(transport_totals.total_fee or 0) if transport_totals else 0,
            'total_paid': float(transport_totals.total_paid or 0) if transport_totals else 0,
            'balance': float(transport_totals.total_balance or 0) if transport_totals else 0,
            'monthly_breakdown': transport_breakdown,  # This contains the months paid in THIS transaction
            'current_payment_amount': float(transport_amount),
            'months_covered': [m['month_name'] for m in transport_breakdown]
        }

        # Get admin user name
        created_by_name = f"{current_user.first_name} {current_user.last_name}" if current_user else None

        # Generate receipt PDF
        receipt_generator = ReceiptGenerator()
        pdf_buffer = receipt_generator.generate_receipt(
            payment_data=receipt_payment_data,
            student_data=student_data,
            month_breakdown=tuition_breakdown,
            fee_summary=fee_summary,
            transport_data=transport_receipt_data,
            created_by_name=created_by_name
        )

        # Upload to Cloudinary
        cloudinary_service = CloudinaryReceiptService()
        receipt_url, cloudinary_public_id = cloudinary_service.upload_receipt(
            pdf_buffer=pdf_buffer,
            payment_id=tuition_payment.id,
            receipt_number=receipt_number
        )

        # Update tuition payment with receipt info
        tuition_payment.receipt_number = receipt_number
        tuition_payment.receipt_cloudinary_url = receipt_url
        tuition_payment.receipt_cloudinary_id = cloudinary_public_id

        await db.commit()
        await db.refresh(tuition_payment)

        logger.info(f"Combined receipt generated: {receipt_url}")

    except Exception as e:
        logger.error(f"Failed to generate combined receipt: {str(e)}")
        import traceback
        traceback.print_exc()

    # =====================================================
    # PART 4: Create Alert for Combined Payment
    # =====================================================
    try:
        # Get payment method description for alert
        payment_method = await payment_method_crud.get_by_id_async(db, id=tuition_payment_method_id)
        payment_method_desc = payment_method.description if payment_method else "Cash"

        # Get current user name
        actor_name = f"{current_user.first_name} {current_user.last_name}" if current_user.first_name else "Admin"

        # Build months paid string for tuition
        tuition_months_list = [m["month_name"] for m in tuition_breakdown]
        tuition_months_str = ", ".join(tuition_months_list) if tuition_months_list else None

        # Build months paid string for transport
        transport_months_list = [m["month_name"] for m in transport_breakdown]
        transport_months_str = ", ".join(transport_months_list) if transport_months_list else None

        # Combined months string
        months_paid_str = tuition_months_str
        if transport_months_str:
            months_paid_str = f"Tuition: {tuition_months_str}; Transport: {transport_months_str}"

        # Total combined amount
        total_amount = float(actual_tuition_amount) + float(transport_amount)

        print(f"Creating combined fee payment alert for student {student.id}")
        await alert_service.create_fee_payment_alert(
            db,
            payment_id=tuition_payment.id,
            student_id=student.id,
            student_name=f"{student.first_name} {student.last_name}",
            class_name=student.class_ref.description if student.class_ref else "Unknown",
            amount=total_amount,
            payment_method=payment_method_desc,
            fee_type='COMBINED',  # Indicate this is a combined payment
            months_paid=months_paid_str,
            actor_user_id=current_user.id,
            actor_name=actor_name
        )
        print(f"Combined fee payment alert created successfully")
    except Exception as e:
        # Log error but don't fail the payment
        import traceback
        print(f"Failed to create combined fee payment alert: {e}")
        traceback.print_exc()

    # =====================================================
    # PART 5: WhatsApp Notification - Using approved template
    # Template: school_fee_text_receipt_v6 (2 variables)
    # =====================================================
    whatsapp_result = None
    whatsapp_status = None
    whatsapp_error = None
    try:
        # Total combined amount for WhatsApp
        total_combined_amount = float(actual_tuition_amount) + float(transport_amount)

        # Check available phone numbers in priority order: father > mother > guardian > student
        contact_phone = None
        for phone_field in [student.father_phone, student.mother_phone, student.guardian_phone, student.phone]:
            is_valid, validated_phone = whatsapp_service.validate_phone_number(phone_field)
            if is_valid and validated_phone:
                contact_phone = validated_phone
                break

        if contact_phone:
            # Send WhatsApp notification using media receipt template (with PDF attachment)
            whatsapp_result = await whatsapp_service.send_fee_media_receipt(
                phone_number=contact_phone,
                student_name=f"{student.first_name} {student.last_name}",
                amount=total_combined_amount,
                receipt_url=receipt_url,
                payment_id=tuition_payment.id
            )

            logger.info(f"WhatsApp notification sent for combined payment {tuition_payment.id}: {whatsapp_result}")
            whatsapp_status = whatsapp_result.get("status", "UNKNOWN")
            whatsapp_error = whatsapp_result.get("error")
        else:
            whatsapp_status = "NO_PHONE"
            whatsapp_error = "No valid phone number available (checked father, mother, guardian, student)"
            logger.info(f"WhatsApp not sent for combined payment {tuition_payment.id}: No valid phone number")

    except Exception as e:
        import traceback
        logger.error(f"Failed to send WhatsApp notification for combined payment {tuition_payment.id}: {e}")
        traceback.print_exc()
        whatsapp_status = "ERROR"
        whatsapp_error = str(e)[:500]

    # Return combined response
    return {
        "success": True,
        "message": f"Combined payment of ₹{actual_tuition_amount + transport_amount} processed (Tuition: ₹{actual_tuition_amount}, Transport: ₹{transport_amount})",
        "tuition_payment": {
            "payment_id": tuition_payment.id,
            "amount": float(actual_tuition_amount),
            "months_affected": len(tuition_breakdown),
            "month_breakdown": tuition_breakdown
        },
        "transport_payment": {
            "payment_id": transport_payment.id,
            "amount": float(transport_amount),
            "months_affected": len(transport_breakdown),
            "month_breakdown": transport_breakdown
        },
        "receipt": {
            "available": receipt_url is not None,
            "receipt_number": receipt_number,
            "receipt_url": receipt_url
        },
        "student": {
            "id": student.id,
            "name": f"{student.first_name} {student.last_name}",
            "admission_number": student.admission_number,
            "class": student.class_ref.name if student.class_ref else "Unknown"
        },
        "updated_balances": {
            "tuition": {
                "total_annual_fee": float(fee_record.total_amount),
                "total_paid": float(fee_record.paid_amount),
                "balance_remaining": float(fee_record.balance_amount)
            },
            "transport": {
                "total_fee": float(transport_totals.total_fee or 0) if transport_totals else 0,
                "total_paid": float(transport_totals.total_paid or 0) if transport_totals else 0,
                "balance_remaining": float(transport_totals.total_balance or 0) if transport_totals else 0
            }
        }
    }


@router.get("/available-months/{student_id}")
async def get_available_months_for_payment(
    student_id: int,
    session_year: Optional[SessionYearEnum] = SessionYearEnum.YEAR_2025_26,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get available months for payment (months that are not fully paid)
    This helps the admin select which months to pay for
    """
    import calendar

    # Get student
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Get session year ID and derive start year from session year name
    session_year_mapping = {
        "2022-23": 1, "2023-24": 2, "2024-25": 3, "2025-26": 4, "2026-27": 5
    }
    session_year_id = session_year_mapping.get(session_year.value, 4)

    # Derive the start year from the session year name (e.g., "2026-27" -> 2026)
    # This ensures correct year calculation for any session year (past, current, or future)
    session_start_year = int(session_year.value.split("-")[0])

    # Get student's fee structure - try multiple approaches
    fee_structure = None
    monthly_fee = 1000.0  # Default fallback

    try:
        # First try to get fee structure by class and session
        if student.class_ref:
            fee_structure = await fee_structure_crud.get_by_class_and_session(
                db,
                class_name=student.class_ref.name,
                session_year=session_year.value
            )

        if fee_structure:
            monthly_fee = float(fee_structure.total_annual_fee) / 12
        else:
            # Fallback: try to get from existing monthly tracking records
            existing_tracking = await db.execute(
                select(MonthlyFeeTrackingModel.monthly_amount)
                .where(
                    and_(
                        MonthlyFeeTrackingModel.student_id == student_id,
                        MonthlyFeeTrackingModel.session_year_id == session_year_id
                    )
                )
                .limit(1)
            )
            existing_amount = existing_tracking.scalar()
            if existing_amount:
                monthly_fee = float(existing_amount)
            else:
                # Final fallback: use default amount based on class
                class_defaults = {
                    "Class 1": 800, "Class 2": 800, "Class 3": 900, "Class 4": 900, "Class 5": 900,
                    "Class 6": 1000, "Class 7": 1000, "Class 8": 1100, "Class 9": 1200, "Class 10": 1200,
                    "Class 11": 1300, "Class 12": 1300
                }
                class_name = student.class_ref.name if student.class_ref else "Class 10"
                monthly_fee = class_defaults.get(class_name, 1000.0)

    except Exception as e:
        # Use default monthly fee if fee structure lookup fails
        monthly_fee = 1000.0

    # Get existing monthly tracking records
    existing_tracking = await db.execute(
        select(MonthlyFeeTrackingModel)
        .where(
            and_(
                MonthlyFeeTrackingModel.student_id == student_id,
                MonthlyFeeTrackingModel.session_year_id == session_year_id
            )
        )
        .order_by(MonthlyFeeTrackingModel.academic_month)
    )
    tracking_records = existing_tracking.scalars().all()

    # Academic year months (April to March)
    academic_months = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]

    available_months = []
    paid_months = []

    # Create a lookup for existing records
    tracking_lookup = {record.academic_month: record for record in tracking_records}

    for month in academic_months:
        month_name = calendar.month_name[month]

        if month in tracking_lookup:
            record = tracking_lookup[month]
            paid_amount = float(record.paid_amount)
            monthly_amount = float(record.monthly_amount)
            balance = monthly_amount - paid_amount

            if balance > 0.01:  # Not fully paid (allowing for small rounding differences)
                # Calculate year for this month using session_start_year
                # April-December = start_year, January-March = start_year + 1
                year = session_start_year if month >= 4 else session_start_year + 1
                available_months.append({
                    "month": month,
                    "month_name": month_name,
                    "year": year,
                    "monthly_fee": monthly_amount,
                    "paid_amount": paid_amount,
                    "balance_amount": balance,
                    "status": "Partial" if paid_amount > 0 else "Pending",
                    "can_pay": True
                })
            else:
                # Calculate year for this month using session_start_year
                # April-December = start_year, January-March = start_year + 1
                year = session_start_year if month >= 4 else session_start_year + 1
                paid_months.append({
                    "month": month,
                    "month_name": month_name,
                    "year": year,
                    "monthly_fee": monthly_amount,
                    "paid_amount": paid_amount,
                    "balance_amount": 0,
                    "status": "Paid",
                    "can_pay": False
                })
        else:
            # No tracking record exists, so it's available for payment
            # Calculate year for this month using session_start_year
            # April-December = start_year, January-March = start_year + 1
            year = session_start_year if month >= 4 else session_start_year + 1
            available_months.append({
                "month": month,
                "month_name": month_name,
                "year": year,
                "monthly_fee": monthly_fee,
                "paid_amount": 0,
                "balance_amount": monthly_fee,
                "status": "Pending",
                "can_pay": True
            })

    return {
        "student": {
            "id": student.id,
            "name": f"{student.first_name} {student.last_name}",
            "admission_number": student.admission_number,
            "roll_number": student.roll_number,
            "class": student.class_ref.name if student.class_ref else "Unknown"
        },
        "session_year": session_year.value,
        "monthly_fee": monthly_fee,
        "total_annual_fee": float(fee_structure.total_annual_fee) if fee_structure else monthly_fee * 12,
        "available_months": available_months,
        "paid_months": paid_months,
        "summary": {
            "total_months": 12,
            "available_months": len(available_months),
            "paid_months": len(paid_months),
            "total_pending_amount": sum(m["balance_amount"] for m in available_months)
        }
    }


@router.get("/monthly-history/{student_id}")
async def get_monthly_payment_history(
    student_id: int,
    session_year: Optional[SessionYearEnum] = SessionYearEnum.YEAR_2025_26,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed monthly payment history for a student
    Shows which months are paid, due, overdue, or partially paid
    """
    from datetime import datetime, date

    # Get student
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Get student's fee structure
    fee_structure = await fee_structure_crud.get_by_class_and_session(
        db,
        class_name=student.class_ref.name if student.class_ref else "",
        session_year=session_year.value
    )

    if not fee_structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fee structure not found for student's class"
        )

    monthly_fee = float(fee_structure.total_annual_fee) / 12
    current_date = date.today()
    current_month = current_date.month
    current_year = current_date.year

    # Get all payments for the student
    payments_query = select(FeePaymentModel).join(FeeRecordModel).where(
        and_(
            FeeRecordModel.student_id == student_id,
            FeeRecordModel.session_year_id == 4  # 2025-26
        )
    ).order_by(FeePaymentModel.payment_date)

    payments_result = await db.execute(payments_query)
    payments = payments_result.scalars().all()

    # Create monthly history (Academic year: April to March)
    monthly_history = []
    academic_months = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]  # Apr to Mar

    total_paid = 0
    total_due = 0
    total_overdue = 0

    for i, month in enumerate(academic_months):
        # Determine year for this month
        if month >= 4:  # Apr-Dec of current academic year
            year = current_year if current_month >= 4 else current_year - 1
        else:  # Jan-Mar of next calendar year
            year = current_year + 1 if current_month >= 4 else current_year

        # Check if this month is due (up to current month)
        is_due = False
        if year < current_year:
            is_due = True
        elif year == current_year:
            is_due = month <= current_month

        # Calculate payments for this month (simplified allocation)
        # In a real system, you'd track payments per month more precisely
        month_paid = 0
        if payments and total_paid < (i + 1) * monthly_fee:
            remaining_for_month = min(monthly_fee, sum(p.amount for p in payments) - i * monthly_fee)
            month_paid = max(0, remaining_for_month)

        # Determine status
        if month_paid >= monthly_fee:
            status = "paid"
            status_color = "#10B981"  # Green
        elif month_paid > 0:
            status = "partial"
            status_color = "#F59E0B"  # Yellow
        elif is_due:
            if month < current_month or year < current_year:
                status = "overdue"
                status_color = "#EF4444"  # Red
                total_overdue += (monthly_fee - month_paid)
            else:
                status = "due"
                status_color = "#F59E0B"  # Orange
        else:
            status = "upcoming"
            status_color = "#6B7280"  # Gray

        if is_due:
            total_due += monthly_fee

        total_paid += month_paid

        # Find specific payments for this month
        month_payments = []
        for payment in payments:
            # Simplified: assume payments are allocated chronologically
            # In practice, you'd need more sophisticated month allocation
            month_payments.append({
                "id": payment.id,
                "amount": float(payment.amount),
                "payment_date": payment.payment_date,
                "transaction_id": payment.transaction_id,
                "remarks": payment.remarks
            })

        monthly_history.append({
            "month": month,
            "year": year,
            "month_name": calendar.month_name[month],
            "month_short": calendar.month_abbr[month],
            "due_amount": monthly_fee,
            "paid_amount": month_paid,
            "balance": monthly_fee - month_paid,
            "status": status,
            "status_color": status_color,
            "is_due": is_due,
            "is_current": (month == current_month and year == current_year),
            "payments": month_payments[:1] if month_payments else []  # Show first payment for simplicity
        })

    # Calculate summary
    summary = {
        "total_annual_fee": float(fee_structure.total_annual_fee),
        "monthly_fee": monthly_fee,
        "total_paid": sum(p.amount for p in payments),
        "total_due": total_due,
        "total_overdue": total_overdue,
        "balance_remaining": float(fee_structure.total_annual_fee) - sum(p.amount for p in payments),
        "months_paid": len([m for m in monthly_history if m["status"] == "paid"]),
        "months_partial": len([m for m in monthly_history if m["status"] == "partial"]),
        "months_overdue": len([m for m in monthly_history if m["status"] == "overdue"]),
        "months_due": len([m for m in monthly_history if m["status"] == "due"]),
        "payment_efficiency": round((sum(p.amount for p in payments) / total_due * 100), 2) if total_due > 0 else 0
    }

    return {
        "student": {
            "id": student.id,
            "name": f"{student.first_name} {student.last_name}",
            "admission_number": student.admission_number,
            "class": student.class_ref.name if student.class_ref else "Unknown",
            "section": student.section
        },
        "session_year": session_year.value,
        "monthly_history": monthly_history,
        "summary": summary,
        "current_month": current_month,
        "current_year": current_year,
        "generated_at": current_date
    }


# =====================================================
# Enhanced Monthly Fee Management Endpoints
# =====================================================

@router.get("/enhanced-students-summary")
async def get_enhanced_students_summary(
    session_year_id: int = Query(..., description="Session year ID"),
    class_id: Optional[int] = Query(None, description="Filter by class ID"),
    payment_status_id: Optional[int] = Query(None, description="Filter by payment status ID"),
    search: Optional[str] = Query(None, description="Search by student name or admission number"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(25, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get enhanced student fee summary with both legacy and monthly tracking data
    Shows comprehensive fee status for all students
    """
    offset = (page - 1) * per_page

    summaries = await monthly_fee_tracking_crud.get_enhanced_student_summary(
        db=db,
        session_year_id=session_year_id,
        class_id=class_id,
        payment_status_id=payment_status_id,
        search=search,
        limit=per_page,
        offset=offset
    )

    # Get total count for pagination
    total = len(summaries)  # This is approximate
    total_pages = math.ceil(total / per_page)

    return {
        "students": summaries,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "has_monthly_tracking": any(s.has_monthly_tracking for s in summaries)
    }


@router.get("/my-fees")
async def get_my_fees(
    session_year_id: int = Query(4, description="Session year ID (default: 2025-26)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get fee information for the currently logged-in student
    Students can only view their own fee information
    Returns comprehensive fee statistics and monthly history
    """
    # Verify user is a student
    if current_user.user_type_id != 3:  # 3 = STUDENT
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only accessible to students"
        )

    # Get student profile from current user using user_id
    student = await student_crud.get_by_user_id(db, user_id=current_user.id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found for current user"
        )

    # Load metadata relationships for the student
    student = await student_crud.get_with_metadata(db, id=student.id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found for current user"
        )

    # Extract student info early to avoid lazy loading issues
    student_id = student.id
    admission_number = student.admission_number
    student_name = f"{student.first_name} {student.last_name}"
    class_name = student.class_ref.description if student.class_ref else "N/A"

    try:
        # Get enhanced student summary (single student)
        summaries = await monthly_fee_tracking_crud.get_enhanced_student_summary(
            db=db,
            session_year_id=session_year_id,
            class_id=None,
            search=admission_number,  # Search by admission number to get specific student
            limit=1,
            offset=0
        )

        if not summaries or len(summaries) == 0:
            # Student doesn't have fee records yet
            return {
                "student_id": student_id,
                "admission_number": admission_number,
                "student_name": student_name,
                "class_name": class_name,
                "has_fee_records": False,
                "has_monthly_tracking": False,
                "message": "No fee records found for current session year"
            }

        summary = summaries[0]

        # Get monthly history if available
        monthly_history = None
        has_monthly_tracking = summary.has_monthly_tracking if summary else False

        if has_monthly_tracking:
            try:
                monthly_history = await monthly_fee_tracking_crud.get_student_monthly_history(
                    db=db,
                    student_id=student_id,
                    session_year_id=session_year_id
                )

                # If monthly_history is None, it means tracking is not properly set up
                if monthly_history is None:
                    # Update the flag to reflect actual state
                    has_monthly_tracking = False

            except Exception as e:
                # If monthly history fails for unexpected reasons, continue without it
                monthly_history = None
                has_monthly_tracking = False

        return {
            "student_id": student_id,
            "admission_number": admission_number,
            "student_name": student_name,
            "class_name": class_name,
            "has_fee_records": True,
            "has_monthly_tracking": has_monthly_tracking,
            "summary": summary,
            "monthly_history": monthly_history
        }

    except ValueError as e:
        # Handle specific business logic errors gracefully
        # Return a user-friendly response instead of raising an exception
        return {
            "student_id": student_id,
            "admission_number": admission_number,
            "student_name": student_name,
            "class_name": class_name,
            "has_fee_records": False,
            "has_monthly_tracking": False,
            "message": "No fee records found for the selected session year"
        }
    except Exception as e:
        # Only raise HTTP exception for unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching fee information: {str(e)}"
        )


@router.get("/my-monthly-history")
async def get_my_monthly_history(
    session_year_id: int = Query(4, description="Session year ID (default: 2025-26)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed monthly fee history for the currently logged-in student
    Students can only view their own monthly payment history
    """
    # Verify user is a student
    if current_user.user_type_id != 3:  # 3 = STUDENT
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only accessible to students"
        )

    # Get student profile from current user using user_id
    student = await student_crud.get_by_user_id(db, user_id=current_user.id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found for current user"
        )

    # Load metadata relationships for the student
    student = await student_crud.get_with_metadata(db, id=student.id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found for current user"
        )

    # Extract student info early to avoid lazy loading issues
    student_id = student.id
    student_name = f"{student.first_name} {student.last_name}"
    class_name = student.class_ref.description if student.class_ref else "N/A"

    try:
        history = await monthly_fee_tracking_crud.get_student_monthly_history(
            db=db,
            student_id=student_id,
            session_year_id=session_year_id
        )

        if not history:
            return {
                "student_id": student_id,
                "student_name": student_name,
                "class_name": class_name,
                "has_monthly_tracking": False,
                "message": "Monthly fee tracking is not enabled for the selected session year. Please contact the administration."
            }

        return history

    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching monthly history: {str(e)}"
        )


@router.get("/enhanced-monthly-history/{student_id}")
async def get_enhanced_student_monthly_history(
    student_id: int,
    session_year_id: int = Query(..., description="Session year ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed monthly fee history for a specific student using enhanced tracking
    Shows month-wise payment status and history
    """
    try:
        history = await monthly_fee_tracking_crud.get_student_monthly_history(
            db=db,
            student_id=student_id,
            session_year_id=session_year_id
        )

        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Monthly fee tracking is not enabled for this student in the selected session year"
            )

        return history

    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while fetching monthly history: {str(e)}"
        )


@router.post("/enable-monthly-tracking")
async def enable_monthly_tracking(
    request: EnableMonthlyTrackingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Complete monthly tracking enablement including fee record creation
    This handles the complete workflow:
    1. Creates fee records for students who don't have them
    2. Enables monthly tracking for all selected students
    3. Creates monthly tracking records
    """
    try:
        # Convert fee_record_ids to student_ids (they're actually student_ids from frontend)
        student_ids = request.fee_record_ids

        # Use a simpler approach - call the function for each student individually
        # This avoids the array parameter complexity
        results = []
        successful_count = 0
        total_records_created = 0
        fee_records_created = 0

        for student_id in student_ids:
            try:
                # Call function for single student
                result = await db.execute(
                    text("""
                        SELECT * FROM enable_monthly_tracking_complete(
                            ARRAY[:student_id]::INTEGER[],
                            :session_year_id,
                            :start_month,
                            :start_year
                        )
                    """),
                    {
                        "student_id": student_id,
                        "session_year_id": request.session_year_id,
                        "start_month": request.start_month,
                        "start_year": request.start_year
                    }
                )

                # Process single result
                row = result.fetchone()
                if row:
                    if row.success:
                        successful_count += 1
                        total_records_created += row.monthly_records_created
                        if row.fee_record_created:
                            fee_records_created += 1

                    results.append({
                        "student_id": row.student_id,
                        "student_name": row.student_name,
                        "fee_record_id": row.fee_record_id,
                        "fee_record_created": row.fee_record_created,
                        "success": row.success,
                        "records_created": row.monthly_records_created,
                        "message": row.message
                    })

            except Exception as student_error:
                results.append({
                    "student_id": student_id,
                    "student_name": f"Student {student_id}",
                    "fee_record_id": None,
                    "fee_record_created": False,
                    "success": False,
                    "records_created": 0,
                    "message": f"Error: {str(student_error)}"
                })

        await db.commit()

        return {
            "message": f"Monthly tracking enabled for {successful_count}/{len(student_ids)} students",
            "total_records_created": total_records_created,
            "fee_records_created": fee_records_created,
            "results": results
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enable monthly tracking: {str(e)}"
        )


@router.delete("/monthly-tracking/{student_id}/{session_year_id}")
async def delete_monthly_tracking_records(
    student_id: int,
    session_year_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete monthly tracking records for a student and session year.
    This is useful for resetting monthly tracking when records have incorrect data.

    IMPORTANT: Only deletes records with no payments (payment_status_id = 1 and paid_amount = 0)
    """
    try:
        # Check if user has permission (admin/super_admin only)
        if current_user.user_type_id not in [1, 6]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can delete monthly tracking records"
            )

        # Verify student exists
        student = await student_crud.get(db, id=student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )

        # Get monthly tracking records that can be deleted (unpaid only)
        result = await db.execute(
            select(MonthlyFeeTrackingModel)
            .where(
                and_(
                    MonthlyFeeTrackingModel.student_id == student_id,
                    MonthlyFeeTrackingModel.session_year_id == session_year_id,
                    MonthlyFeeTrackingModel.payment_status_id == 1,  # Pending status
                    MonthlyFeeTrackingModel.paid_amount == 0
                )
            )
        )
        unpaid_records = result.scalars().all()

        # Check if there are paid records that cannot be deleted
        paid_result = await db.execute(
            select(func.count(MonthlyFeeTrackingModel.id))
            .where(
                and_(
                    MonthlyFeeTrackingModel.student_id == student_id,
                    MonthlyFeeTrackingModel.session_year_id == session_year_id,
                    or_(
                        MonthlyFeeTrackingModel.payment_status_id != 1,
                        MonthlyFeeTrackingModel.paid_amount > 0
                    )
                )
            )
        )
        paid_count = paid_result.scalar() or 0

        if not unpaid_records:
            if paid_count > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot delete: {paid_count} records have payments. Only unpaid records can be deleted."
                )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No monthly tracking records found for this student and session year"
            )

        # Delete unpaid records
        deleted_count = 0
        for record in unpaid_records:
            await db.delete(record)
            deleted_count += 1

        await db.commit()

        return {
            "message": f"Successfully deleted {deleted_count} monthly tracking records",
            "student_id": student_id,
            "session_year_id": session_year_id,
            "deleted_count": deleted_count,
            "skipped_paid_records": paid_count
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete monthly tracking records: {str(e)}"
        )


@router.get("/validate-payment-consistency/{student_id}")
async def validate_payment_consistency(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Validate payment data consistency for a specific student
    Checks for mismatches between payment records, fee records, and monthly tracking
    """
    try:
        # Get student
        student = await student_crud.get(db, id=student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )

        # Check fee records vs payments
        fee_records = await fee_record_crud.get_by_student(db, student_id=student_id)

        inconsistencies = []

        for record in fee_records:
            # Get payments for this record
            payments = await fee_payment_crud.get_by_fee_record(db, fee_record_id=record.id)
            payments_sum = sum(payment.amount for payment in payments)

            if record.paid_amount != payments_sum:
                inconsistencies.append({
                    "type": "fee_record_mismatch",
                    "fee_record_id": record.id,
                    "fee_record_paid": float(record.paid_amount),
                    "payments_sum": float(payments_sum),
                    "difference": float(record.paid_amount - payments_sum)
                })

        # Check monthly tracking vs allocations
        monthly_records_query = select(MonthlyFeeTracking).where(
            MonthlyFeeTracking.student_id == student_id
        )
        monthly_result = await db.execute(monthly_records_query)
        monthly_records = monthly_result.scalars().all()

        for month_record in monthly_records:
            allocations_query = select(MonthlyPaymentAllocation).where(
                MonthlyPaymentAllocation.monthly_tracking_id == month_record.id
            )
            allocations_result = await db.execute(allocations_query)
            allocations = allocations_result.scalars().all()

            allocations_sum = sum(allocation.allocated_amount for allocation in allocations)

            if month_record.paid_amount != allocations_sum:
                inconsistencies.append({
                    "type": "monthly_tracking_mismatch",
                    "monthly_tracking_id": month_record.id,
                    "month_name": month_record.month_name,
                    "academic_year": month_record.academic_year,
                    "monthly_paid": float(month_record.paid_amount),
                    "allocations_sum": float(allocations_sum),
                    "difference": float(month_record.paid_amount - allocations_sum)
                })

        return {
            "student_id": student_id,
            "student_name": f"{student.first_name} {student.last_name}",
            "is_consistent": len(inconsistencies) == 0,
            "inconsistencies_count": len(inconsistencies),
            "inconsistencies": inconsistencies
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating payment consistency: {str(e)}"
        )


# =====================================================
# WhatsApp Service Test Endpoint
# =====================================================

@router.post("/whatsapp/test")
async def test_whatsapp_service(
    phone_number: str = Query(..., description="Phone number to send test message to"),
    message: Optional[str] = Query(None, description="Optional custom message"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Test WhatsApp service connectivity by sending a simple test message.

    Use this endpoint to verify that:
    1. Twilio credentials are correct
    2. WhatsApp sender number is properly configured
    3. Messages can be delivered to the recipient

    Example: POST /api/v1/fees/whatsapp/test?phone_number=9876543210
    """
    logger.info(f"WhatsApp test requested by user {current_user.id} to {phone_number}")

    # Send test message
    result = await whatsapp_service.send_test_message(
        phone_number=phone_number,
        custom_message=message
    )

    return {
        "test_type": "whatsapp_connectivity",
        "requested_by": current_user.email,
        "result": result,
        "troubleshooting": {
            "if_error_63007": "Your WhatsApp number is not registered with Twilio. Go to Twilio Console → Messaging → Senders → WhatsApp senders",
            "if_error_63016": "Recipient phone number is not registered on WhatsApp",
            "sandbox_option": "For testing, you can use Twilio sandbox number +14155238886 (recipient must opt-in first)"
        }
    }
