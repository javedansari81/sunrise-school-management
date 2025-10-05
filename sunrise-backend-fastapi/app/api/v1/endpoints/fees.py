from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, func, select, text
from sqlalchemy.orm import joinedload, selectinload
from datetime import date
import math
import calendar

from app.core.database import get_db
from app.crud import fee_structure_crud, fee_record_crud, fee_payment_crud, student_crud
from app.crud.crud_monthly_fee import monthly_fee_tracking_crud, monthly_payment_allocation_crud
from app.schemas.fee import (
    FeeStructure, FeeStructureCreate, FeeStructureUpdate,
    FeeRecord, FeeRecordCreate, FeeRecordUpdate, FeeRecordWithStudent,
    FeePayment, FeePaymentCreate, FeePaymentUpdate,
    FeeFilters, FeeListResponse, FeeDashboard, FeeCollectionReport,
    SessionYearEnum, PaymentStatusEnum, PaymentTypeEnum,
    EnhancedStudentFeeSummary, StudentMonthlyFeeHistory, EnhancedPaymentRequest,
    EnableMonthlyTrackingRequest, MonthlyFeeTracking
)
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.student import Student
from app.models.fee import FeeRecord as FeeRecordModel, FeePayment as FeePaymentModel, MonthlyFeeTracking as MonthlyFeeTrackingModel

router = APIRouter()


@router.get("/", response_model=FeeListResponse)
@router.get("", response_model=FeeListResponse)  # Handle both with and without trailing slash
async def get_fees(
    session_year: Optional[SessionYearEnum] = SessionYearEnum.YEAR_2025_26,
    class_name: Optional[str] = None,
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
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get fee records with comprehensive filters and enhanced search capabilities
    Defaults to current financial year 2025-26
    """
    filters = FeeFilters(
        session_year=session_year,
        class_name=class_name,
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
                payment_type_id=payment_type_data["payment_type_id"],
                total_amount=payment_type_data["total_amount"],
                balance_amount=payment_type_data["total_amount"],
                due_date=payment_type_data["due_date"],
                payment_status_id=1  # Pending
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
        "current_class": student.current_class,
        "current_session": session_year.value if session_year else "2025-26",
        "fee_records": fee_records
    }


@router.post("/payment")
async def process_fee_payment(
    payment_data: FeePaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Process fee payment (full or partial)
    """
    # Get fee record
    fee_record = await fee_record_crud.get(db, id=payment_data.fee_record_id)
    if not fee_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fee record not found"
        )

    # Validate payment amount
    if payment_data.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount must be greater than 0"
        )

    if payment_data.amount > fee_record.balance_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment amount cannot exceed balance amount of {fee_record.balance_amount}"
        )

    # Create payment and update fee record
    payment = await fee_payment_crud.create_payment(
        db, obj_in=payment_data, fee_record=fee_record
    )

    return payment


@router.post("/student-submit/{student_id}")
async def student_submit_fee(
    student_id: int,
    submission_data: dict,  # {"payment_type": str, "amount": float, "payment_method_id": int, "transaction_id": str, "remarks": str}
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Allow students to submit fee payments with different frequencies
    Supports Monthly, Quarterly, Half Yearly, and Yearly payments
    """
    # Verify student exists and current user has permission
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Check if current user is the student or has admin/teacher role
    if current_user.user_type_id not in [1, 2] and student.user_id != current_user.id:  # 1=admin, 2=teacher
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit fees for your own account"
        )

    payment_type = submission_data.get("payment_type")
    amount = submission_data.get("amount", 0)
    payment_method_id = submission_data.get("payment_method_id")
    transaction_id = submission_data.get("transaction_id")
    remarks = submission_data.get("remarks", "")

    # Validate input
    if not payment_type or payment_type not in ["Monthly", "Quarterly", "Half Yearly", "Yearly"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment type. Must be one of: Monthly, Quarterly, Half Yearly, Yearly"
        )

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

    # Get payment type ID from mapping
    payment_type_mapping = {"Monthly": 1, "Quarterly": 2, "Half Yearly": 3, "Yearly": 4}
    payment_type_id = payment_type_mapping.get(payment_type)
    if not payment_type_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment type"
        )

    # Get current session year (2025-26)
    current_session_id = 4  # 2025-26 session year ID

    # Check if fee record exists for this student, session, and payment type
    fee_record = await fee_record_crud.get_by_student_session_type(
        db,
        student_id=student_id,
        session_year_id=current_session_id,
        payment_type_id=payment_type_id
    )

    if not fee_record:
        # Create new fee record if it doesn't exist
        fee_record_data = FeeRecordCreate(
            student_id=student_id,
            session_year_id=current_session_id,
            payment_type_id=payment_type_id,
            total_amount=amount,
            balance_amount=amount,
            due_date=date.today(),
            payment_status_id=1  # Pending
        )
        fee_record = await fee_record_crud.create(db, obj_in=fee_record_data)

    # Validate payment amount doesn't exceed balance
    if amount > fee_record.balance_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment amount ({amount}) cannot exceed balance amount ({fee_record.balance_amount})"
        )

    # Create payment record
    payment_data = FeePaymentCreate(
        fee_record_id=fee_record.id,
        amount=amount,
        payment_method_id=payment_method_id,
        payment_date=date.today(),
        transaction_id=transaction_id,
        remarks=remarks
    )

    # Process payment
    payment = await fee_payment_crud.create_payment(
        db, obj_in=payment_data, fee_record=fee_record
    )

    return {
        "message": "Fee payment submitted successfully",
        "payment": payment,
        "fee_record": fee_record,
        "remaining_balance": fee_record.balance_amount - amount
    }


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

    # Check if current user is the student or has admin/teacher role
    if current_user.user_type_id not in [1, 2] and student.user_id != current_user.id:  # 1=admin, 2=teacher
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


@router.post("/payments/lump-sum/{student_id}")
async def process_lump_sum_payment(
    student_id: int,
    payment_data: dict,  # {"amount": float, "payment_method": str, "transaction_id": str, "remarks": str}
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Process lump sum payment - automatically distribute across pending fee records
    """
    # Verify student exists
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    total_amount = payment_data.get("amount", 0)
    if total_amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount must be greater than 0"
        )

    # Get all pending fee records for the student (ordered by due date)
    pending_fees = await fee_record_crud.get_pending_fees_by_student(db, student_id=student_id)

    if not pending_fees:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending fees found for this student"
        )

    remaining_amount = total_amount
    payments_made = []

    # Process payments in order of due date
    for fee_record in pending_fees:
        if remaining_amount <= 0:
            break

        # Calculate payment amount for this record
        payment_amount = min(remaining_amount, fee_record.balance_amount)

        # Create payment record
        payment_create = FeePaymentCreate(
            fee_record_id=fee_record.id,
            amount=payment_amount,
            payment_method=payment_data.get("payment_method", "Cash"),
            transaction_id=payment_data.get("transaction_id", ""),
            payment_date=date.today(),
            remarks=f"Lump sum payment - {payment_data.get('remarks', '')}"
        )

        # Process the payment
        payment = await fee_payment_crud.create_payment(
            db, obj_in=payment_create, fee_record=fee_record
        )

        payments_made.append({
            "fee_record_id": fee_record.id,
            "amount_paid": payment_amount,
            "remaining_balance": fee_record.balance_amount - payment_amount
        })

        remaining_amount -= payment_amount

    # Calculate months covered (assuming monthly fees)
    months_covered = len([p for p in payments_made if p["remaining_balance"] == 0])

    return {
        "message": "Lump sum payment processed successfully",
        "total_amount": total_amount,
        "amount_used": total_amount - remaining_amount,
        "remaining_amount": remaining_amount,
        "months_covered": months_covered,
        "payments_made": payments_made
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
    """
    # Verify student exists
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Check if current user has permission to view this student's history
    if current_user.user_type_id not in [1, 2] and student.user_id != current_user.id:  # 1=admin, 2=teacher
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view payment history for your own account"
        )

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
        # Get all payments for this fee record with payment method relationship
        payments_query = select(FeePaymentModel).options(
            selectinload(FeePaymentModel.payment_method)
        ).where(FeePaymentModel.fee_record_id == fee_record.id).order_by(FeePaymentModel.created_at.desc())

        payments_result = await db.execute(payments_query)
        payments = payments_result.scalars().all()

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
            payment_detail = {
                "payment_id": payment.id,
                "amount": payment.amount,
                "payment_date": payment.payment_date,
                "payment_method": payment.payment_method.name if payment.payment_method else "Unknown",
                "transaction_id": payment.transaction_id,
                "receipt_number": payment.receipt_number,
                "remarks": payment.remarks,
                "created_at": payment.created_at
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
        "class": student.class_ref.name if student.class_ref else "",
        "session_year": session_year.value,
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
    if current_user.user_type_id not in [1, 2] and student.user_id != current_user.id:  # 1=admin, 2=teacher
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
            "email": "school@sunriseschool.edu"
        }
    }


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
    per_page: int = Query(20, ge=1, le=100),
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


@router.post("/pay-monthly-fee/{student_id}")
async def pay_monthly_fee(
    student_id: int,
    from_month: int = Query(..., ge=1, le=12, description="Starting month (1-12)"),
    to_month: int = Query(..., ge=1, le=12, description="Ending month (1-12)"),
    payment_method_id: int = Query(..., description="Payment method ID"),
    amount: float = Query(..., gt=0, description="Payment amount"),
    transaction_id: Optional[str] = Query(None, description="Transaction reference ID"),
    remarks: Optional[str] = Query(None, description="Payment remarks"),
    session_year: Optional[SessionYearEnum] = SessionYearEnum.YEAR_2025_26,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Process monthly fee payment for a student for specified month range
    Allows paying for multiple months at once (from_month to to_month)
    """
    from datetime import datetime, date

    # Validate month range
    if from_month > to_month:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="From month cannot be greater than to month"
        )

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

    # Calculate monthly fee and total months
    monthly_fee = float(fee_structure.total_annual_fee) / 12
    months_count = to_month - from_month + 1
    expected_amount = monthly_fee * months_count

    # Validate payment amount
    if amount > expected_amount * 1.1:  # Allow 10% buffer for convenience
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment amount ({amount}) exceeds expected amount ({expected_amount}) by more than 10%"
        )

    # Get or create fee record for the student
    existing_record = await fee_record_crud.get_by_student_and_session(
        db, student_id=student_id, session_year=session_year.value
    )

    if not existing_record:
        # Create new fee record
        fee_record_data = FeeRecordCreate(
            student_id=student_id,
            session_year_id=4,  # 2025-26
            payment_type_id=1,  # Default
            payment_status_id=1,  # Pending
            payment_method_id=payment_method_id,
            total_amount=fee_structure.total_annual_fee,
            paid_amount=0,
            balance_amount=fee_structure.total_annual_fee,
            due_date=date(2025, 4, 30),  # Default due date
            remarks=f"Monthly fee payment for {calendar.month_name[from_month]} to {calendar.month_name[to_month]}"
        )
        fee_record = await fee_record_crud.create(db, obj_in=fee_record_data)
    else:
        fee_record = existing_record

    # Create payment record
    payment_data = FeePaymentCreate(
        fee_record_id=fee_record.id,
        amount=amount,
        payment_method_id=payment_method_id,
        payment_date=date.today(),
        transaction_id=transaction_id,
        remarks=f"Payment for months {from_month} to {to_month}: {remarks}" if remarks else f"Payment for months {from_month} to {to_month}"
    )

    payment = await fee_payment_crud.create(db, obj_in=payment_data)

    # Update fee record amounts
    # Convert amount to Decimal for compatibility with database field
    from decimal import Decimal
    fee_record.paid_amount += Decimal(str(amount))
    fee_record.balance_amount = fee_record.total_amount - fee_record.paid_amount

    # Update payment status based on balance
    if fee_record.balance_amount <= 0:
        fee_record.payment_status_id = 2  # Paid
        fee_record.balance_amount = 0
    elif fee_record.paid_amount > 0:
        fee_record.payment_status_id = 3  # Partial

    await db.commit()
    await db.refresh(fee_record)
    await db.refresh(payment)

    # Calculate payment breakdown by month
    amount_per_month = amount / months_count
    months_paid = []

    for month in range(from_month, to_month + 1):
        months_paid.append({
            "month": month,
            "month_name": calendar.month_name[month],
            "amount_paid": amount_per_month,
            "expected_amount": monthly_fee,
            "status": "paid" if amount_per_month >= monthly_fee else "partial"
        })

    return {
        "success": True,
        "message": f"Payment of ₹{amount} processed successfully for {months_count} month(s)",
        "payment_id": payment.id,
        "fee_record_id": fee_record.id,
        "student": {
            "id": student.id,
            "name": f"{student.first_name} {student.last_name}",
            "admission_number": student.admission_number,
            "class": student.class_ref.name if student.class_ref else "Unknown"
        },
        "payment_details": {
            "amount": amount,
            "from_month": from_month,
            "to_month": to_month,
            "months_count": months_count,
            "amount_per_month": amount_per_month,
            "expected_per_month": monthly_fee,
            "transaction_id": transaction_id,
            "payment_date": date.today(),
            "months_paid": months_paid
        },
        "updated_balance": {
            "total_annual_fee": float(fee_record.total_amount),
            "total_paid": float(fee_record.paid_amount),
            "balance_remaining": float(fee_record.balance_amount),
            "payment_status": "Paid" if fee_record.balance_amount <= 0 else ("Partial" if fee_record.paid_amount > 0 else "Pending")
        }
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
    from datetime import datetime, date
    import calendar

    # Extract payment data
    amount = float(payment_data.get("amount", 0))
    payment_method = payment_data.get("payment_method", "CASH")  # Default to CASH
    selected_months = payment_data.get("selected_months", [])  # Can be month names or numbers
    session_year = payment_data.get("session_year", "2025-26")
    transaction_id = payment_data.get("transaction_id")
    remarks = payment_data.get("remarks", "")

    # Map payment method string to ID (based on configuration endpoint)
    payment_method_mapping = {
        "CASH": 1,
        "CHEQUE": 2,
        "ONLINE": 3,
        "UPI": 4,
        "CARD": 5
    }

    # Ensure payment_method_id is always set to a valid value
    if payment_method and isinstance(payment_method, str):
        payment_method_upper = payment_method.upper()
        payment_method_id = payment_method_mapping.get(payment_method_upper, 1)  # Default to CASH (ID: 1)
    else:
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

    if not payment_method:
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

    # Get session year ID
    session_year_mapping = {
        "2022-23": 1, "2023-24": 2, "2024-25": 3, "2025-26": 4, "2026-27": 5
    }
    session_year_id = session_year_mapping.get(session_year, 4)

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
            print(f"DEBUG: Creating fee record with payment_method_id={payment_method_id}, fee_structure.id={fee_structure.id}")
            fee_record_data = FeeRecordCreate(
                student_id=student_id,
                session_year_id=session_year_id,
                payment_type_id=1,  # Monthly
                payment_status_id=1,  # Pending
                payment_method_id=payment_method_id,
                fee_structure_id=fee_structure.id,
                is_monthly_tracked=True,
                total_amount=fee_structure.total_annual_fee,
                paid_amount=0,
                balance_amount=fee_structure.total_annual_fee,
                due_date=date(2025, 4, 30),
                remarks="Enhanced monthly payment system"
            )
            print(f"DEBUG: FeeRecordCreate object: payment_method_id={fee_record_data.payment_method_id}, fee_structure_id={fee_record_data.fee_structure_id}, is_monthly_tracked={fee_record_data.is_monthly_tracked}")
            fee_record = await fee_record_crud.create(db, obj_in=fee_record_data)
        else:
            fee_record = existing_fee_record

        # Create monthly tracking records for selected months
        available_months = []
        for month in selected_months:
            # Calculate due date (10th of each month)
            year = 2025 if month >= 4 else 2026  # Academic year Apr 2025 - Mar 2026
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
    payment_data = {
        "fee_record_id": available_months[0].fee_record_id,
        "amount": actual_amount_to_process,  # Use actual processable amount
        "payment_method_id": payment_method_id,  # This should be an integer
        "payment_date": date.today(),
        "transaction_id": transaction_id,
        "remarks": f"Enhanced monthly payment: {remarks}" if remarks else "Enhanced monthly payment"
    }

    # Create the payment record directly using the model
    from app.models.fee import FeePayment
    payment_record = FeePayment(**payment_data)
    db.add(payment_record)
    await db.flush()  # Get the ID without committing

    # Use the payment_record as our payment object
    payment = payment_record

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
        fee_record.payment_status_id = 2  # Paid
        fee_record.balance_amount = 0
    elif fee_record.paid_amount > 0:
        fee_record.payment_status_id = 3  # Partial

    await db.commit()
    await db.refresh(fee_record)
    await db.refresh(payment)

    # Calculate summary
    total_months_affected = len(payment_breakdown)
    fully_paid_months = len([m for m in payment_breakdown if m["status"] == "Paid"])
    partial_months = len([m for m in payment_breakdown if m["status"] == "Partial"])

    # Calculate any remaining amount that couldn't be processed
    remaining_unprocessed = amount - actual_amount_to_process

    return {
        "success": True,
        "message": f"Payment of ₹{actual_amount_to_process} processed: ₹{total_allocated} allocated across {total_months_affected} month(s)" + (f", ₹{remaining_unprocessed} could not be processed (no pending amounts)" if remaining_unprocessed > 0 else ""),
        "payment_id": payment.id,
        "original_amount": amount,
        "processed_amount": actual_amount_to_process,
        "remaining_unprocessed": remaining_unprocessed,
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
            "payment_date": date.today().isoformat()
        },
        "month_wise_breakdown": payment_breakdown,
        "updated_balance": {
            "total_annual_fee": float(fee_record.total_amount),
            "total_paid": float(fee_record.paid_amount),
            "balance_remaining": float(fee_record.balance_amount),
            "payment_status": "Paid" if fee_record.balance_amount <= 0 else ("Partial" if fee_record.paid_amount > 0 else "Pending")
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

    # Get session year ID
    session_year_mapping = {
        "2022-23": 1, "2023-24": 2, "2024-25": 3, "2025-26": 4, "2026-27": 5
    }
    session_year_id = session_year_mapping.get(session_year.value, 4)

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
        print(f"Error getting fee structure: {e}")
        # Use default monthly fee
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
                # Calculate year for this month (academic year: Apr 2025 - Mar 2026)
                year = 2025 if month >= 4 else 2026
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
                # Calculate year for this month (academic year: Apr 2025 - Mar 2026)
                year = 2025 if month >= 4 else 2026
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
            # Calculate year for this month (academic year: Apr 2025 - Mar 2026)
            year = 2025 if month >= 4 else 2026
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
    search: Optional[str] = Query(None, description="Search by student name or admission number"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
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
                detail="Monthly fee history not found for this student"
            )

        return history

    except ValueError as e:
        # Handle specific business logic errors
        error_message = str(e)
        if "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_message
            )
        elif "monthly tracking" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )

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

        # Debug logging
        print(f"DEBUG: Enabling monthly tracking for student_ids: {student_ids}")
        print(f"DEBUG: Request data: start_month={request.start_month}, start_year={request.start_year}")

        # Use a simpler approach - call the function for each student individually
        # This avoids the array parameter complexity
        results = []
        successful_count = 0
        total_records_created = 0
        fee_records_created = 0

        for student_id in student_ids:
            try:
                print(f"DEBUG: Processing student {student_id}")

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
                        "session_year_id": 4,
                        "start_month": request.start_month,
                        "start_year": request.start_year
                    }
                )

                # Process single result
                row = result.fetchone()
                if row:
                    print(f"DEBUG: Student {row.student_id} result: success={row.success}, message={row.message}")

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
                print(f"ERROR: Failed for student {student_id}: {str(student_error)}")
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

        print(f"DEBUG: Final results - successful: {successful_count}, total_records: {total_records_created}, fee_records: {fee_records_created}")

        return {
            "message": f"Monthly tracking enabled for {successful_count}/{len(student_ids)} students",
            "total_records_created": total_records_created,
            "fee_records_created": fee_records_created,
            "results": results
        }

    except Exception as e:
        await db.rollback()
        print(f"ERROR: Failed to enable monthly tracking: {str(e)}")
        print(f"ERROR: Exception type: {type(e).__name__}")
        import traceback
        print(f"ERROR: Full traceback: {traceback.format_exc()}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enable monthly tracking: {str(e)}"
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
