from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
import math

from app.core.database import get_db
from app.crud import fee_structure_crud, fee_record_crud, fee_payment_crud, student_crud
from app.schemas.fee import (
    FeeStructure, FeeStructureCreate, FeeStructureUpdate,
    FeeRecord, FeeRecordCreate, FeeRecordUpdate, FeeRecordWithStudent,
    FeePayment, FeePaymentCreate, FeePaymentUpdate,
    FeeFilters, FeeListResponse, FeeDashboard, FeeCollectionReport,
    SessionYearEnum, PaymentStatusEnum, PaymentTypeEnum
)
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=FeeListResponse)
async def get_fees(
    session_year: Optional[SessionYearEnum] = None,
    class_name: Optional[str] = None,
    month: Optional[int] = Query(None, ge=1, le=12),
    status: Optional[PaymentStatusEnum] = None,
    payment_type: Optional[PaymentTypeEnum] = None,
    student_id: Optional[int] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get fee records with comprehensive filters
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
        db, filters=filters, skip=skip, limit=per_page
    )

    # Convert to response format with student details
    fee_list = []
    for fee in fees:
        fee_dict = {
            **fee.__dict__,
            "student_name": f"{fee.student.first_name} {fee.student.last_name}",
            "student_admission_number": fee.student.admission_number,
            "student_class": fee.student.class_ref.name if fee.student.class_ref else None
        }
        fee_list.append(fee_dict)

    # Get summary statistics
    summary = await fee_record_crud.get_collection_summary(db, session_year=session_year)

    total_pages = math.ceil(total / per_page)

    return FeeListResponse(
        fees=fee_list,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        summary=summary
    )


@router.post("/", response_model=FeeRecord)
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


@router.get("/student/{student_id}")
async def get_student_fees(
    student_id: int,
    session_year: Optional[SessionYearEnum] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all fee records for a specific student
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
        "current_session": session_year or "2024-25",
        "fee_records": fee_records
    }


@router.post("/payment", response_model=FeePayment)
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
    session_year: Optional[SessionYearEnum] = None,
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
    session_year: Optional[SessionYearEnum] = None,
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


@router.post("/records", response_model=FeeRecord)
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


@router.put("/records/{fee_record_id}", response_model=FeeRecord)
async def update_fee_record(
    fee_record_id: int,
    fee_data: FeeRecordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing fee record
    """
    fee_record = await fee_record_crud.get(db, id=fee_record_id)
    if not fee_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fee record not found"
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
    session_year: Optional[SessionYearEnum] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get complete payment history for a student
    """
    # Verify student exists
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Get payment history
    payments = await fee_payment_crud.get_student_payment_history(
        db, student_id=student_id, session_year=session_year
    )

    return {
        "student_id": student_id,
        "student_name": f"{student.first_name} {student.last_name}",
        "payments": payments
    }


@router.get("/dashboard", response_model=FeeDashboard)
async def get_fee_dashboard(
    session_year: Optional[SessionYearEnum] = None,
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
