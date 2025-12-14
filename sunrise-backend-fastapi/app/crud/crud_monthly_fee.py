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
    ) -> Optional[StudentMonthlyFeeHistory]:
        """
        Get detailed monthly fee history for a student
        Returns None if student not found or monthly tracking not enabled
        """

        # Get student and class info
        student_query = await db.execute(
            select(Student)
            .options(joinedload(Student.class_ref))
            .where(Student.id == student_id)
        )
        student = student_query.scalar_one_or_none()

        if not student:
            # Return None instead of raising exception for better error handling
            return None

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
            # Return None instead of raising exception for better error handling
            return None
            
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
                paid_months += 1  # Count partial payments as paid months
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
            admission_number=student.admission_number,
            roll_number=student.roll_number,
            class_name=student.class_ref.description if student.class_ref else "",
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
        payment_status_id: Optional[int] = None,
        search: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[EnhancedStudentFeeSummary]:
        """Get enhanced student fee summary by querying underlying tables with direct class_id and payment_status_id filtering"""

        # Build the query by joining underlying tables directly
        base_query = """
            SELECT
                s.id as student_id,
                s.admission_number,
                s.first_name || ' ' || s.last_name as student_name,
                s.roll_number,
                s.father_name,
                s.phone as mobile_number,
                c.name as class_name,
                sy.name as session_year,
                fr.id as fee_record_id,
                fr.total_amount as annual_fee,
                fr.paid_amount as total_paid,
                fr.balance_amount as total_balance,
                COALESCE(monthly_stats.total_months_tracked, 0) as total_months_tracked,
                COALESCE(monthly_stats.paid_months, 0) as paid_months,
                COALESCE(monthly_stats.pending_months, 0) as pending_months,
                COALESCE(monthly_stats.overdue_months, 0) as overdue_months,
                COALESCE(monthly_stats.monthly_total, 0) as monthly_total,
                COALESCE(monthly_stats.monthly_paid, 0) as monthly_paid,
                COALESCE(monthly_stats.monthly_balance, 0) as monthly_balance,
                CASE
                    WHEN fr.total_amount > 0 THEN
                        ROUND((fr.paid_amount * 100.0 / fr.total_amount), 2)
                    ELSE 0
                END as collection_percentage,
                CASE
                    WHEN monthly_stats.total_months_tracked > 0 THEN true
                    ELSE false
                END as has_monthly_tracking,
                CASE
                    WHEN ste.id IS NOT NULL AND ste.is_active = true AND ste.discontinue_date IS NULL THEN true
                    ELSE false
                END as has_transport_enrollment,
                ste.id as transport_enrollment_id
            FROM students s
            LEFT JOIN classes c ON s.class_id = c.id
            LEFT JOIN session_years sy ON s.session_year_id = sy.id
            LEFT JOIN fee_records fr ON s.id = fr.student_id AND s.session_year_id = fr.session_year_id
            LEFT JOIN (
                SELECT
                    mft.student_id,
                    mft.session_year_id,
                    COUNT(*) as total_months_tracked,
                    COUNT(CASE WHEN ps.name = 'PAID' THEN 1 END) as paid_months,
                    COUNT(CASE WHEN ps.name = 'PENDING' THEN 1 END) as pending_months,
                    COUNT(CASE WHEN ps.name = 'OVERDUE' THEN 1 END) as overdue_months,
                    SUM(mft.monthly_amount) as monthly_total,
                    SUM(mft.paid_amount) as monthly_paid,
                    SUM(mft.balance_amount) as monthly_balance
                FROM monthly_fee_tracking mft
                LEFT JOIN payment_statuses ps ON mft.payment_status_id = ps.id
                WHERE ps.is_active = true
                GROUP BY mft.student_id, mft.session_year_id
            ) monthly_stats ON s.id = monthly_stats.student_id AND s.session_year_id = monthly_stats.session_year_id
            LEFT JOIN student_transport_enrollment ste
                ON s.id = ste.student_id
                AND s.session_year_id = ste.session_year_id
                AND ste.is_active = true
                AND ste.discontinue_date IS NULL
            WHERE s.is_active = true
              AND (s.is_deleted = FALSE OR s.is_deleted IS NULL)
              AND c.is_active = true
              AND sy.is_active = true
              AND s.session_year_id = :session_year_id
        """

        params = {"session_year_id": session_year_id}

        # Add class filter if provided - filter directly by class_id
        if class_id:
            base_query += " AND s.class_id = :class_id"
            params["class_id"] = class_id

        # Add payment status filter if provided - filter by fee_records payment_status_id
        if payment_status_id:
            base_query += " AND fr.payment_status_id = :payment_status_id"
            params["payment_status_id"] = payment_status_id

        # Add search filter if provided
        if search:
            base_query += " AND (s.first_name || ' ' || s.last_name ILIKE :search OR s.admission_number ILIKE :search)"
            params["search"] = f"%{search}%"

        # Add ordering and pagination
        base_query += " ORDER BY s.first_name || ' ' || s.last_name LIMIT :limit OFFSET :offset"
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

            # Transport enrollment status
            has_transport_enrollment = bool(row.has_transport_enrollment) if hasattr(row, 'has_transport_enrollment') else False
            transport_enrollment_id = row.transport_enrollment_id if hasattr(row, 'transport_enrollment_id') else None

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
                has_monthly_tracking=has_monthly_tracking,
                has_transport_enrollment=has_transport_enrollment,
                transport_enrollment_id=transport_enrollment_id
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
                            WHEN LEAST(paid_amount + :amount, monthly_amount) >= monthly_amount THEN 2
                            WHEN LEAST(paid_amount + :amount, monthly_amount) > 0 THEN 3
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
