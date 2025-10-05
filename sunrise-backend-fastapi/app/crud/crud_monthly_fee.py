from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_, or_, func, extract, case, exists, text
from datetime import date, datetime

from app.crud.base import CRUDBase
from app.models.fee import MonthlyFeeTracking, MonthlyPaymentAllocation, FeeRecord, FeePayment
from app.models.student import Student
from app.models.metadata import SessionYear, PaymentStatus, Class
from app.schemas.fee import (
    MonthlyFeeTrackingCreate, MonthlyFeeTrackingUpdate,
    MonthlyFeeStatus, StudentMonthlyFeeHistory, EnhancedStudentFeeSummary
)


class CRUDMonthlyFeeTracking(CRUDBase[MonthlyFeeTracking, MonthlyFeeTrackingCreate, MonthlyFeeTrackingUpdate]):
    
    async def get_by_fee_record(
        self, 
        db: AsyncSession, 
        fee_record_id: int
    ) -> List[MonthlyFeeTracking]:
        """Get all monthly tracking records for a fee record"""
        result = await db.execute(
            select(MonthlyFeeTracking)
            .where(MonthlyFeeTracking.fee_record_id == fee_record_id)
            .order_by(MonthlyFeeTracking.academic_year, MonthlyFeeTracking.academic_month)
        )
        return result.scalars().all()
    
    async def get_student_monthly_history(
        self,
        db: AsyncSession,
        student_id: int,
        session_year_id: int
    ) -> StudentMonthlyFeeHistory:
        """Get detailed monthly fee history for a student"""
        
        # Get student and class info
        student_query = await db.execute(
            select(Student)
            .options(joinedload(Student.class_ref))
            .where(Student.id == student_id)
        )
        student = student_query.scalar_one_or_none()
        
        if not student:
            raise ValueError(f"Student with ID {student_id} not found")
            
        # Get session year info
        session_query = await db.execute(
            select(SessionYear).where(SessionYear.id == session_year_id)
        )
        session_year = session_query.scalar_one_or_none()
        
        # Get fee record for this student and session
        fee_record_query = await db.execute(
            select(FeeRecord)
            .where(
                and_(
                    FeeRecord.student_id == student_id,
                    FeeRecord.session_year_id == session_year_id,
                    FeeRecord.is_monthly_tracked == True
                )
            )
        )
        fee_record = fee_record_query.scalar_one_or_none()
        
        if not fee_record:
            raise ValueError(f"No monthly tracking enabled for student {student_id} in session {session_year_id}. Please enable monthly tracking first.")
            
        # Get monthly tracking records
        monthly_records_query = await db.execute(
            select(MonthlyFeeTracking)
            .where(MonthlyFeeTracking.fee_record_id == fee_record.id)
            .order_by(MonthlyFeeTracking.academic_year, MonthlyFeeTracking.academic_month)
        )
        monthly_records = monthly_records_query.scalars().all()
        
        # Get actual total payments made by the student (from fee_payments table)
        # This ensures consistency with Payment History dialog
        from app.models.fee import FeePayment
        payments_query = await db.execute(
            select(func.sum(FeePayment.amount))
            .where(FeePayment.fee_record_id == fee_record.id)
        )
        actual_total_paid = payments_query.scalar() or 0

        # Convert to MonthlyFeeStatus objects
        monthly_history = []
        total_paid = float(actual_total_paid)  # Use actual payments for consistency
        total_balance = 0
        paid_months = 0
        overdue_months = 0
        pending_months = 0

        current_date = date.today()
        
        for record in monthly_records:
            # Get payment status name
            status_query = await db.execute(
                select(PaymentStatus.name).where(PaymentStatus.id == record.payment_status_id)
            )
            status_name = status_query.scalar_one_or_none() or "Unknown"

            # Calculate status color and overdue info
            status_color = "#28a745"  # Green for paid
            is_overdue = False
            days_overdue = None

            if record.payment_status_id == 1:  # Pending
                status_color = "#ffc107"  # Yellow
                if record.due_date < current_date:
                    is_overdue = True
                    days_overdue = (current_date - record.due_date).days
                    status_color = "#dc3545"  # Red for overdue
                    overdue_months += 1
                else:
                    pending_months += 1
            elif record.payment_status_id == 2:  # Partial
                status_color = "#fd7e14"  # Orange
            elif record.payment_status_id == 3:  # Paid
                paid_months += 1
            elif record.payment_status_id == 4:  # Overdue
                status_color = "#dc3545"  # Red
                is_overdue = True
                days_overdue = (current_date - record.due_date).days
                overdue_months += 1
            
            # Fix balance calculation to prevent negative values
            # If paid_amount > monthly_amount, show balance as 0 (fully paid)
            corrected_balance = max(0, float(record.monthly_amount) - float(record.paid_amount))

            monthly_status = MonthlyFeeStatus(
                month=record.academic_month,
                year=record.academic_year,
                month_name=record.month_name,
                monthly_amount=float(record.monthly_amount),
                paid_amount=float(record.paid_amount),
                balance_amount=corrected_balance,  # Use corrected balance (no negatives)
                due_date=record.due_date,
                status=status_name,
                status_color=status_color,
                is_overdue=is_overdue,
                days_overdue=days_overdue,
                late_fee=float(record.late_fee),
                discount_amount=float(record.discount_amount)
            )
            monthly_history.append(monthly_status)

            # Don't add individual month payments to total_paid (already calculated above from raw payments)
            # total_paid += float(record.paid_amount)  # OLD: This caused discrepancy
            total_balance += corrected_balance  # Use corrected balance
        
        # Calculate collection percentage
        total_annual_fee = float(fee_record.total_amount)
        collection_percentage = (total_paid / total_annual_fee * 100) if total_annual_fee > 0 else 0
        
        return StudentMonthlyFeeHistory(
            student_id=student.id,
            student_name=f"{student.first_name} {student.last_name}",
            class_name=student.class_ref.display_name if student.class_ref else "",
            session_year=session_year.name if session_year else "",
            monthly_fee_amount=float(monthly_records[0].monthly_amount) if monthly_records else 0,
            total_annual_fee=total_annual_fee,
            monthly_history=monthly_history,
            total_months=len(monthly_records),
            paid_months=paid_months,
            pending_months=pending_months,
            overdue_months=overdue_months,
            total_paid=total_paid,
            total_balance=total_balance,
            collection_percentage=round(collection_percentage, 2)
        )
    
    async def get_enhanced_student_summary(
        self,
        db: AsyncSession,
        session_year_id: int,
        class_id: Optional[int] = None,
        search: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[EnhancedStudentFeeSummary]:
        """Get enhanced student fee summary using the database view"""

        # First get the session year name from ID
        from app.models.metadata import SessionYear
        session_year_result = await db.execute(
            select(SessionYear.name).where(SessionYear.id == session_year_id)
        )
        session_year_name = session_year_result.scalar_one_or_none()

        if not session_year_name:
            return []  # Return empty list if session year not found

        # Build the base query
        base_query = """
            SELECT
                student_id, admission_number, student_name, class_name, session_year,
                fee_record_id, annual_fee, total_paid, total_balance,
                total_months_tracked, paid_months, pending_months, overdue_months,
                monthly_total, monthly_paid, monthly_balance, collection_percentage,
                has_monthly_tracking
            FROM enhanced_student_fee_status
            WHERE session_year = :session_year
        """

        params = {"session_year": session_year_name}

        # Add class filter if provided
        if class_id:
            # Get class name from class_id
            from app.models.metadata import Class
            class_result = await db.execute(
                select(Class.display_name).where(Class.id == class_id)
            )
            class_name = class_result.scalar_one_or_none()
            if class_name:
                base_query += " AND class_name = :class_name"
                params["class_name"] = class_name

        # Add search filter if provided
        if search:
            base_query += " AND (student_name ILIKE :search OR admission_number ILIKE :search)"
            params["search"] = f"%{search}%"

        # Add ordering and pagination
        base_query += " ORDER BY student_name LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset

        # Execute the query
        query = text(base_query)
        result = await db.execute(query, params)
        rows = result.fetchall()
        
        summaries = []
        for row in rows:
            # Use collection_percentage and has_monthly_tracking from the view
            collection_percentage = float(row.collection_percentage) if row.collection_percentage else 0.0
            has_monthly_tracking = bool(row.has_monthly_tracking) if hasattr(row, 'has_monthly_tracking') else (row.total_months_tracked > 0)

            summary = EnhancedStudentFeeSummary(
                student_id=row.student_id,
                admission_number=row.admission_number,
                student_name=row.student_name,
                class_name=row.class_name,
                session_year=row.session_year,
                fee_record_id=row.fee_record_id,
                annual_fee=float(row.annual_fee) if row.annual_fee else None,
                total_paid=float(row.total_paid) if row.total_paid else None,
                total_balance=float(row.total_balance) if row.total_balance else None,
                total_months_tracked=row.total_months_tracked or 0,
                paid_months=row.paid_months or 0,
                pending_months=row.pending_months or 0,
                overdue_months=row.overdue_months or 0,
                monthly_total=float(row.monthly_total) if row.monthly_total else None,
                monthly_paid=float(row.monthly_paid) if row.monthly_paid else None,
                monthly_balance=float(row.monthly_balance) if row.monthly_balance else None,
                collection_percentage=round(collection_percentage, 2),
                has_monthly_tracking=has_monthly_tracking
            )
            summaries.append(summary)

        return summaries
    
    async def enable_monthly_tracking(
        self,
        db: AsyncSession,
        fee_record_id: int,
        start_month: int = 4,
        start_year: Optional[int] = None
    ) -> int:
        """Enable monthly tracking for a fee record using the database function"""
        
        if start_year is None:
            start_year = datetime.now().year
            
        # Call the database function
        result = await db.execute(
            text("SELECT enable_monthly_tracking_for_record(:fee_record_id, :start_month, :start_year)"),
            {
                "fee_record_id": fee_record_id,
                "start_month": start_month,
                "start_year": start_year
            }
        )
        
        records_created = result.scalar()
        await db.commit()
        
        return records_created


class CRUDMonthlyPaymentAllocation(CRUDBase[MonthlyPaymentAllocation, dict, dict]):
    
    async def allocate_payment_to_months(
        self,
        db: AsyncSession,
        payment_id: int,
        allocations: List[Dict[str, Any]]
    ) -> List[MonthlyPaymentAllocation]:
        """Allocate a payment to specific monthly tracking records"""
        
        created_allocations = []
        
        for allocation in allocations:
            # Check if allocation already exists to prevent duplicates
            existing_allocation = await db.execute(
                select(MonthlyPaymentAllocation).where(
                    MonthlyPaymentAllocation.fee_payment_id == payment_id,
                    MonthlyPaymentAllocation.monthly_tracking_id == allocation["monthly_tracking_id"]
                )
            )
            if existing_allocation.scalar_one_or_none() is None:
                allocation_obj = MonthlyPaymentAllocation(
                    fee_payment_id=payment_id,
                    monthly_tracking_id=allocation["monthly_tracking_id"],
                    allocated_amount=allocation["amount"]
                )
                db.add(allocation_obj)
                created_allocations.append(allocation_obj)
            
            # Update the monthly tracking record with validation
            await db.execute(
                text("""
                    UPDATE monthly_fee_tracking
                    SET
                        paid_amount = LEAST(paid_amount + :amount, monthly_amount),
                        payment_status_id = CASE
                            WHEN LEAST(paid_amount + :amount, monthly_amount) >= monthly_amount THEN 3
                            WHEN LEAST(paid_amount + :amount, monthly_amount) > 0 THEN 2
                            ELSE payment_status_id
                        END,
                        updated_at = NOW()
                    WHERE id = :tracking_id
                """),
                {
                    "amount": allocation["amount"],
                    "tracking_id": allocation["monthly_tracking_id"]
                }
            )
        
        await db.commit()
        return created_allocations


# Create instances
monthly_fee_tracking_crud = CRUDMonthlyFeeTracking(MonthlyFeeTracking)
monthly_payment_allocation_crud = CRUDMonthlyPaymentAllocation(MonthlyPaymentAllocation)
