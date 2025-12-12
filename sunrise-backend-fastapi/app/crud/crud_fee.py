from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_, or_, func, extract, case, exists
from datetime import date, datetime

from app.crud.base import CRUDBase
from app.models.fee import FeeStructure, FeeRecord, FeePayment, MonthlyPaymentAllocation, MonthlyFeeTracking, FeePaymentAuditLog
from app.models.student import Student
from app.models.user import User
from app.models.metadata import SessionYear, PaymentStatus
from app.schemas.fee import (
    FeeStructureCreate, FeeStructureUpdate,
    FeeRecordCreate, FeeRecordUpdate,
    FeePaymentCreate, FeePaymentUpdate,
    FeeFilters, PaymentStatusEnum, SessionYearEnum
)
from decimal import Decimal
import json


class CRUDFeeStructure(CRUDBase[FeeStructure, FeeStructureCreate, FeeStructureUpdate]):
    async def get_by_class_and_session(
        self, db: AsyncSession, *, class_name: str, session_year: str
    ) -> Optional[FeeStructure]:
        # Import here to avoid circular imports
        from app.models.metadata import Class, SessionYear

        result = await db.execute(
            select(FeeStructure)
            .join(Class, FeeStructure.class_id == Class.id)
            .join(SessionYear, FeeStructure.session_year_id == SessionYear.id)
            .where(
                and_(
                    Class.name == class_name,
                    SessionYear.name == session_year
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_class_id_and_session_id(
        self, db: AsyncSession, *, class_id: int, session_year_id: int
    ) -> Optional[FeeStructure]:
        """Get fee structure by class ID and session year ID (more efficient)"""
        result = await db.execute(
            select(FeeStructure).where(
                and_(
                    FeeStructure.class_id == class_id,
                    FeeStructure.session_year_id == session_year_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_all_structures(self, db: AsyncSession) -> List[FeeStructure]:
        result = await db.execute(
            select(FeeStructure)
            .options(joinedload(FeeStructure.class_ref), joinedload(FeeStructure.session_year))
            .order_by(FeeStructure.class_id)
        )
        return result.scalars().all()


class CRUDFeeRecord(CRUDBase[FeeRecord, FeeRecordCreate, FeeRecordUpdate]):
    async def get_with_student(self, db: AsyncSession, id: int) -> Optional[FeeRecord]:
        result = await db.execute(
            select(FeeRecord)
            .options(joinedload(FeeRecord.student))
            .where(FeeRecord.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_student_session_type(
        self,
        db: AsyncSession,
        *,
        student_id: int,
        session_year_id: int,
        payment_type_id: int
    ) -> Optional[FeeRecord]:
        """Get fee record by student, session year, and payment type"""
        result = await db.execute(
            select(FeeRecord).where(
                and_(
                    FeeRecord.student_id == student_id,
                    FeeRecord.session_year_id == session_year_id,
                    FeeRecord.payment_type_id == payment_type_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_multi_with_filters(
        self,
        db: AsyncSession,
        *,
        filters: FeeFilters,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        sort_by: Optional[str] = "due_date",
        sort_order: Optional[str] = "asc"
    ) -> tuple[List[FeeRecord], int]:
        query = select(FeeRecord).options(
            joinedload(FeeRecord.student).joinedload(Student.class_ref)
        )
        
        # Apply filters
        conditions = []
        
        if filters.session_year:
            conditions.append(FeeRecord.session_year.has(name=filters.session_year.value))
        
        if filters.status:
            conditions.append(FeeRecord.payment_status.has(name=filters.status.value))

        if filters.payment_type:
            conditions.append(FeeRecord.payment_type.has(name=filters.payment_type.value))
        
        if filters.student_id:
            conditions.append(FeeRecord.student_id == filters.student_id)

        if filters.class_id:
            # Filter directly by class_id in fee_records table
            conditions.append(FeeRecord.class_id == filters.class_id)

        if filters.from_date:
            conditions.append(FeeRecord.due_date >= filters.from_date)
        
        if filters.to_date:
            conditions.append(FeeRecord.due_date <= filters.to_date)
        
        if filters.month:
            conditions.append(extract('month', FeeRecord.due_date) == filters.month)

        # Add search functionality
        if search:
            search_conditions = or_(
                func.concat(Student.first_name, ' ', Student.last_name).ilike(f"%{search}%"),
                Student.admission_number.ilike(f"%{search}%")
            )
            conditions.append(search_conditions)
            # Need explicit join for WHERE clause filtering
            query = query.join(Student)

        if conditions:
            query = query.where(and_(*conditions))

        # Add sorting
        sort_column = FeeRecord.due_date  # default
        if sort_by == "student_name":
            sort_column = func.concat(Student.first_name, ' ', Student.last_name)
            # Need explicit join for ORDER BY clause
            if not search:  # Only join if not already joined for search
                query = query.join(Student)
        elif sort_by == "amount":
            sort_column = FeeRecord.total_amount
        elif sort_by == "status":
            sort_column = FeeRecord.payment_status_id
        elif sort_by == "due_date":
            sort_column = FeeRecord.due_date

        if sort_order == "desc":
            sort_column = sort_column.desc()

        # Get total count
        count_query = select(func.count(FeeRecord.id))
        # Add join if search is used (needed for WHERE clause with Student fields)
        if search:
            count_query = count_query.join(Student)
        if conditions:
            count_query = count_query.where(and_(*conditions))

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = query.order_by(sort_column).offset(skip).limit(limit)
        result = await db.execute(query)
        
        return result.scalars().all(), total

    async def get_by_student(
        self, db: AsyncSession, *, student_id: int, session_year: Optional[str] = None
    ) -> List[FeeRecord]:
        query = select(FeeRecord).options(
            joinedload(FeeRecord.payment_type),
            joinedload(FeeRecord.payment_status),
            joinedload(FeeRecord.session_year)
        ).where(FeeRecord.student_id == student_id)

        if session_year:
            query = query.where(FeeRecord.session_year.has(name=session_year))

        query = query.order_by(FeeRecord.created_at.desc())
        result = await db.execute(query)
        return result.scalars().all()

    async def get_overdue_fees(self, db: AsyncSession) -> List[FeeRecord]:
        today = date.today()
        result = await db.execute(
            select(FeeRecord)
            .options(joinedload(FeeRecord.student))
            .where(
                and_(
                    FeeRecord.due_date < today,
                    FeeRecord.payment_status.has(PaymentStatus.name.in_([PaymentStatusEnum.PENDING.value, PaymentStatusEnum.PARTIAL.value]))
                )
            )
            .order_by(FeeRecord.due_date)
        )
        return result.scalars().all()

    async def get_collection_summary(
        self, db: AsyncSession, *, session_year: Optional[str] = None
    ) -> Dict[str, Any]:
        from app.models.metadata import SessionYear, PaymentStatus

        query = select(
            func.sum(FeeRecord.total_amount).label('total_amount'),
            func.sum(FeeRecord.paid_amount).label('paid_amount'),
            func.count(FeeRecord.id).label('total_records'),
            func.count(
                case(
                    (exists().where(
                        and_(
                            PaymentStatus.id == FeeRecord.payment_status_id,
                            PaymentStatus.name == "Paid"
                        )
                    ), 1),
                    else_=None
                )
            ).label('paid_records')
        )

        if session_year:
            query = query.where(
                exists().where(
                    and_(
                        SessionYear.id == FeeRecord.session_year_id,
                        SessionYear.name == session_year
                    )
                )
            )

        result = await db.execute(query)
        summary = result.first()

        total_amount = float(summary.total_amount or 0)
        paid_amount = float(summary.paid_amount or 0)

        return {
            'total_amount': total_amount,
            'paid_amount': paid_amount,
            'pending_amount': total_amount - paid_amount,
            'total_records': summary.total_records or 0,
            'paid_records': summary.paid_records or 0,
            'collection_rate': (paid_amount / total_amount * 100) if total_amount > 0 else 0
        }

    async def update_payment_status(
        self, db: AsyncSession, *, fee_record: FeeRecord, payment_amount: float
    ) -> FeeRecord:
        fee_record.paid_amount += payment_amount
        fee_record.balance_amount = fee_record.total_amount - fee_record.paid_amount
        
        if fee_record.balance_amount <= 0:
            fee_record.payment_status_id = 2  # PAID
            fee_record.balance_amount = 0
        elif fee_record.paid_amount > 0:
            fee_record.payment_status_id = 3  # PARTIAL
        
        db.add(fee_record)
        await db.commit()
        await db.refresh(fee_record)
        return fee_record

    async def get_pending_fees_by_student(
        self, db: AsyncSession, *, student_id: int
    ) -> List[FeeRecord]:
        """Get all pending fee records for a student ordered by due date"""
        result = await db.execute(
            select(FeeRecord)
            .where(
                and_(
                    FeeRecord.student_id == student_id,
                    FeeRecord.balance_amount > 0
                )
            )
            .order_by(FeeRecord.due_date.asc())
        )
        return result.scalars().all()


class CRUDFeePayment(CRUDBase[FeePayment, FeePaymentCreate, FeePaymentUpdate]):
    async def get_by_fee_record(
        self, db: AsyncSession, *, fee_record_id: int
    ) -> List[FeePayment]:
        result = await db.execute(
            select(FeePayment)
            .where(FeePayment.fee_record_id == fee_record_id)
            .order_by(FeePayment.created_at.desc())
        )
        return result.scalars().all()

    async def create_payment(
        self, db: AsyncSession, *, obj_in: FeePaymentCreate, fee_record: FeeRecord
    ) -> FeePayment:
        # Create payment record
        payment = await self.create(db, obj_in=obj_in)
        
        # Update fee record payment status
        fee_record.paid_amount += obj_in.amount
        fee_record.balance_amount = fee_record.total_amount - fee_record.paid_amount
        
        if fee_record.balance_amount <= 0:
            fee_record.payment_status_id = 2  # PAID
            fee_record.balance_amount = 0
        elif fee_record.paid_amount > 0:
            fee_record.payment_status_id = 3  # PARTIAL
        
        fee_record.payment_method = obj_in.payment_method
        fee_record.transaction_id = obj_in.transaction_id
        fee_record.payment_date = obj_in.payment_date
        
        db.add(fee_record)
        await db.commit()
        await db.refresh(fee_record)
        await db.refresh(payment)
        
        return payment

    async def get_student_payment_history(
        self, db: AsyncSession, *, student_id: int, session_year: Optional[str] = None
    ) -> List[FeePayment]:
        """Get all payments made by a student"""
        query = select(FeePayment).join(FeeRecord).where(FeeRecord.student_id == student_id)

        if session_year:
            query = query.where(FeeRecord.session_year.has(name=session_year))

        query = query.order_by(FeePayment.payment_date.desc())

        result = await db.execute(query)
        return result.scalars().all()

    async def reverse_payment_full(
        self,
        db: AsyncSession,
        *,
        payment_id: int,
        reason_id: int,
        details: Optional[str],
        user_id: int
    ) -> Dict[str, Any]:
        """
        Reverse an entire payment with all its allocations

        Args:
            payment_id: ID of the payment to reverse
            reason_id: Reversal reason ID from reversal_reasons table
            details: Additional details
            user_id: ID of user performing the reversal

        Returns:
            Dictionary with reversal details

        Raises:
            ValueError: If payment cannot be reversed
        """
        # Get the original payment with all relationships
        result = await db.execute(
            select(FeePayment)
            .options(selectinload(FeePayment.fee_record))
            .where(FeePayment.id == payment_id)
        )
        original_payment = result.scalar_one_or_none()

        if not original_payment:
            raise ValueError(f"Payment with ID {payment_id} not found")

        # Validation checks
        if original_payment.is_reversal:
            raise ValueError("Cannot reverse a reversal payment")

        if original_payment.reversed_by_payment_id is not None:
            raise ValueError("Payment has already been reversed")

        # Get all allocations for this payment
        allocations_result = await db.execute(
            select(MonthlyPaymentAllocation)
            .where(MonthlyPaymentAllocation.fee_payment_id == payment_id)
        )
        allocations = allocations_result.scalars().all()

        # Create reversal payment with negative amount
        reversal_payment_data = {
            "fee_record_id": original_payment.fee_record_id,
            "amount": -original_payment.amount,  # Negative amount
            "payment_method_id": original_payment.payment_method_id,
            "payment_date": date.today(),
            "transaction_id": f"REV-{original_payment.transaction_id or original_payment.id}",
            "remarks": f"REVERSAL. {details or ''}",
            "is_reversal": True,
            "reverses_payment_id": payment_id,
            "reversal_reason_id": reason_id,
            "reversal_type": "FULL",
            "created_by": user_id
        }

        reversal_payment = FeePayment(**reversal_payment_data)
        db.add(reversal_payment)
        await db.flush()  # Get the ID

        # Update original payment to mark it as reversed
        original_payment.reversed_by_payment_id = reversal_payment.id

        # Create negative allocations and update monthly tracking
        affected_months = []
        for allocation in allocations:
            # Get monthly tracking record
            monthly_result = await db.execute(
                select(MonthlyFeeTracking)
                .where(MonthlyFeeTracking.id == allocation.monthly_tracking_id)
            )
            monthly_tracking = monthly_result.scalar_one_or_none()

            if monthly_tracking:
                # Create negative allocation
                reversal_allocation = MonthlyPaymentAllocation(
                    fee_payment_id=reversal_payment.id,
                    monthly_tracking_id=allocation.monthly_tracking_id,
                    allocated_amount=-allocation.allocated_amount,
                    is_reversal=True,
                    reverses_allocation_id=allocation.id,
                    created_by=user_id
                )
                db.add(reversal_allocation)

                # Update monthly tracking paid_amount
                monthly_tracking.paid_amount = Decimal(str(monthly_tracking.paid_amount)) - Decimal(str(allocation.allocated_amount))

                # Recalculate payment status
                if monthly_tracking.paid_amount <= 0:
                    monthly_tracking.payment_status_id = 1  # PENDING
                elif monthly_tracking.paid_amount >= monthly_tracking.monthly_amount:
                    monthly_tracking.payment_status_id = 2  # PAID
                else:
                    monthly_tracking.payment_status_id = 3  # PARTIAL

                monthly_tracking.updated_at = datetime.now()

                affected_months.append({
                    "month": monthly_tracking.month_name,
                    "year": monthly_tracking.academic_year,
                    "reversed_amount": float(allocation.allocated_amount),
                    "new_paid_amount": float(monthly_tracking.paid_amount),
                    "new_status": "Pending" if monthly_tracking.payment_status_id == 1 else ("Paid" if monthly_tracking.payment_status_id == 2 else "Partial")
                })

        # Update fee record totals
        fee_record = original_payment.fee_record
        fee_record.paid_amount = Decimal(str(fee_record.paid_amount)) - Decimal(str(original_payment.amount))
        fee_record.balance_amount = fee_record.total_amount - fee_record.paid_amount

        # Recalculate fee record payment status
        if fee_record.paid_amount <= 0:
            fee_record.payment_status_id = 1  # PENDING
        elif fee_record.balance_amount <= 0:
            fee_record.payment_status_id = 2  # PAID
        else:
            fee_record.payment_status_id = 3  # PARTIAL

        fee_record.updated_at = datetime.now()

        # Create audit log entry
        audit_log = FeePaymentAuditLog(
            payment_id=payment_id,
            action="REVERSED_FULL",
            performed_by=user_id,
            reason=f"Reason ID: {reason_id}. {details or ''}",
            old_values={
                "amount": float(original_payment.amount),
                "fee_record_paid_amount": float(fee_record.paid_amount + Decimal(str(original_payment.amount))),
                "fee_record_balance_amount": float(fee_record.balance_amount - Decimal(str(original_payment.amount)))
            },
            new_values={
                "reversal_payment_id": reversal_payment.id,
                "fee_record_paid_amount": float(fee_record.paid_amount),
                "fee_record_balance_amount": float(fee_record.balance_amount)
            }
        )
        db.add(audit_log)

        # Commit all changes
        await db.commit()
        await db.refresh(reversal_payment)
        await db.refresh(fee_record)

        return {
            "success": True,
            "message": "Payment reversed successfully",
            "original_payment_id": payment_id,
            "reversal_payment_id": reversal_payment.id,
            "reversal_amount": float(original_payment.amount),
            "reversal_type": "FULL",
            "student_id": fee_record.student_id,  # Add student_id for alert creation
            "affected_months": affected_months,
            "fee_record_updated": {
                "id": fee_record.id,
                "paid_amount": float(fee_record.paid_amount),
                "balance_amount": float(fee_record.balance_amount),
                "payment_status_id": fee_record.payment_status_id
            }
        }

    async def reverse_payment_partial(
        self,
        db: AsyncSession,
        *,
        payment_id: int,
        allocation_ids: List[int],
        reason_id: int,
        details: Optional[str],
        user_id: int
    ) -> Dict[str, Any]:
        """
        Reverse specific month allocations of a payment

        Args:
            payment_id: ID of the payment to partially reverse
            allocation_ids: List of allocation IDs to reverse
            reason_id: Reversal reason ID from reversal_reasons table
            details: Additional details
            user_id: ID of user performing the reversal

        Returns:
            Dictionary with reversal details

        Raises:
            ValueError: If payment or allocations cannot be reversed
        """
        # Get the original payment
        result = await db.execute(
            select(FeePayment)
            .options(selectinload(FeePayment.fee_record))
            .where(FeePayment.id == payment_id)
        )
        original_payment = result.scalar_one_or_none()

        if not original_payment:
            raise ValueError(f"Payment with ID {payment_id} not found")

        # Validation checks
        if original_payment.is_reversal:
            raise ValueError("Cannot reverse a reversal payment")

        # Get specified allocations
        allocations_result = await db.execute(
            select(MonthlyPaymentAllocation)
            .where(
                and_(
                    MonthlyPaymentAllocation.fee_payment_id == payment_id,
                    MonthlyPaymentAllocation.id.in_(allocation_ids)
                )
            )
        )
        allocations = allocations_result.scalars().all()

        if len(allocations) != len(allocation_ids):
            raise ValueError("Some allocation IDs are invalid or do not belong to this payment")

        # Check if any allocations are already reversed
        for allocation in allocations:
            if allocation.is_reversal:
                raise ValueError(f"Allocation {allocation.id} is already a reversal")

            # Check if this allocation has been reversed
            reversed_check = await db.execute(
                select(MonthlyPaymentAllocation)
                .where(MonthlyPaymentAllocation.reverses_allocation_id == allocation.id)
            )
            if reversed_check.scalar_one_or_none():
                raise ValueError(f"Allocation {allocation.id} has already been reversed")

        # Get all allocations to check if this is a full reversal
        all_allocations_result = await db.execute(
            select(MonthlyPaymentAllocation)
            .where(MonthlyPaymentAllocation.fee_payment_id == payment_id)
        )
        all_allocations = all_allocations_result.scalars().all()

        if len(allocations) == len(all_allocations):
            raise ValueError("Cannot use partial reversal for all allocations. Use full reversal instead.")

        # Calculate total reversal amount
        total_reversal_amount = sum(Decimal(str(alloc.allocated_amount)) for alloc in allocations)

        # Create reversal payment with negative amount
        reversal_payment_data = {
            "fee_record_id": original_payment.fee_record_id,
            "amount": -total_reversal_amount,  # Negative amount
            "payment_method_id": original_payment.payment_method_id,
            "payment_date": date.today(),
            "transaction_id": f"REV-PARTIAL-{original_payment.transaction_id or original_payment.id}",
            "remarks": f"PARTIAL REVERSAL. {details or ''}",
            "is_reversal": True,
            "reverses_payment_id": payment_id,
            "reversal_reason_id": reason_id,
            "reversal_type": "PARTIAL",
            "created_by": user_id
        }

        reversal_payment = FeePayment(**reversal_payment_data)
        db.add(reversal_payment)
        await db.flush()  # Get the ID

        # Note: We don't update original_payment.reversed_by_payment_id for partial reversals
        # This allows tracking multiple partial reversals

        # Create negative allocations and update monthly tracking
        affected_months = []
        for allocation in allocations:
            # Get monthly tracking record
            monthly_result = await db.execute(
                select(MonthlyFeeTracking)
                .where(MonthlyFeeTracking.id == allocation.monthly_tracking_id)
            )
            monthly_tracking = monthly_result.scalar_one_or_none()

            if monthly_tracking:
                # Create negative allocation
                reversal_allocation = MonthlyPaymentAllocation(
                    fee_payment_id=reversal_payment.id,
                    monthly_tracking_id=allocation.monthly_tracking_id,
                    allocated_amount=-allocation.allocated_amount,
                    is_reversal=True,
                    reverses_allocation_id=allocation.id,
                    created_by=user_id
                )
                db.add(reversal_allocation)

                # Update monthly tracking paid_amount
                monthly_tracking.paid_amount = Decimal(str(monthly_tracking.paid_amount)) - Decimal(str(allocation.allocated_amount))

                # Recalculate payment status
                if monthly_tracking.paid_amount <= 0:
                    monthly_tracking.payment_status_id = 1  # PENDING
                elif monthly_tracking.paid_amount >= monthly_tracking.monthly_amount:
                    monthly_tracking.payment_status_id = 2  # PAID
                else:
                    monthly_tracking.payment_status_id = 3  # PARTIAL

                monthly_tracking.updated_at = datetime.now()

                affected_months.append({
                    "month": monthly_tracking.month_name,
                    "year": monthly_tracking.academic_year,
                    "reversed_amount": float(allocation.allocated_amount),
                    "new_paid_amount": float(monthly_tracking.paid_amount),
                    "new_status": "Pending" if monthly_tracking.payment_status_id == 1 else ("Paid" if monthly_tracking.payment_status_id == 2 else "Partial")
                })

        # Update fee record totals
        fee_record = original_payment.fee_record
        fee_record.paid_amount = Decimal(str(fee_record.paid_amount)) - total_reversal_amount
        fee_record.balance_amount = fee_record.total_amount - fee_record.paid_amount

        # Recalculate fee record payment status
        if fee_record.paid_amount <= 0:
            fee_record.payment_status_id = 1  # PENDING
        elif fee_record.balance_amount <= 0:
            fee_record.payment_status_id = 2  # PAID
        else:
            fee_record.payment_status_id = 3  # PARTIAL

        fee_record.updated_at = datetime.now()

        # Create audit log entry
        audit_log = FeePaymentAuditLog(
            payment_id=payment_id,
            action="REVERSED_PARTIAL",
            performed_by=user_id,
            reason=f"Reason ID: {reason_id}. {details or ''}",
            old_values={
                "allocation_ids": allocation_ids,
                "total_reversal_amount": float(total_reversal_amount),
                "fee_record_paid_amount": float(fee_record.paid_amount + total_reversal_amount),
                "fee_record_balance_amount": float(fee_record.balance_amount - total_reversal_amount)
            },
            new_values={
                "reversal_payment_id": reversal_payment.id,
                "fee_record_paid_amount": float(fee_record.paid_amount),
                "fee_record_balance_amount": float(fee_record.balance_amount)
            }
        )
        db.add(audit_log)

        # Commit all changes
        await db.commit()
        await db.refresh(reversal_payment)
        await db.refresh(fee_record)

        return {
            "success": True,
            "message": "Payment partially reversed successfully",
            "original_payment_id": payment_id,
            "reversal_payment_id": reversal_payment.id,
            "reversal_amount": float(total_reversal_amount),
            "reversal_type": "PARTIAL",
            "student_id": fee_record.student_id,  # Add student_id for alert creation
            "affected_months": affected_months,
            "fee_record_updated": {
                "id": fee_record.id,
                "paid_amount": float(fee_record.paid_amount),
                "balance_amount": float(fee_record.balance_amount),
                "payment_status_id": fee_record.payment_status_id
            }
        }

# Create instances
fee_structure_crud = CRUDFeeStructure(FeeStructure)
fee_record_crud = CRUDFeeRecord(FeeRecord)
fee_payment_crud = CRUDFeePayment(FeePayment)
