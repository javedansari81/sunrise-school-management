"""
CRUD operations for Transport Management
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.orm import selectinload
from datetime import date, datetime
from decimal import Decimal
import calendar

from app.models.transport import (
    TransportType, TransportDistanceSlab, StudentTransportEnrollment,
    TransportMonthlyTracking, TransportPayment
)
from app.models.student import Student
from app.models.metadata import SessionYear, Class, PaymentStatus
from app.schemas.transport import (
    StudentTransportEnrollmentCreate, StudentTransportEnrollmentUpdate,
    TransportMonthlyTrackingCreate, TransportMonthlyTrackingUpdate,
    TransportPaymentCreate, EnhancedStudentTransportSummary,
    StudentTransportMonthlyHistory, TransportMonthlyTrackingResponse
)


class CRUDTransportEnrollment:
    """CRUD operations for student transport enrollment"""
    
    async def create_enrollment(
        self,
        db: AsyncSession,
        enrollment_data: StudentTransportEnrollmentCreate
    ) -> StudentTransportEnrollment:
        """Create new transport enrollment"""
        enrollment = StudentTransportEnrollment(**enrollment_data.model_dump())
        db.add(enrollment)
        await db.commit()
        await db.refresh(enrollment)
        return enrollment
    
    async def get_enrollment_by_id(
        self,
        db: AsyncSession,
        enrollment_id: int
    ) -> Optional[StudentTransportEnrollment]:
        """Get enrollment by ID"""
        result = await db.execute(
            select(StudentTransportEnrollment)
            .where(StudentTransportEnrollment.id == enrollment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_active_enrollment(
        self,
        db: AsyncSession,
        student_id: int,
        session_year_id: int
    ) -> Optional[StudentTransportEnrollment]:
        """Get active enrollment for student in session"""
        result = await db.execute(
            select(StudentTransportEnrollment)
            .where(
                and_(
                    StudentTransportEnrollment.student_id == student_id,
                    StudentTransportEnrollment.session_year_id == session_year_id,
                    StudentTransportEnrollment.is_active == True,
                    StudentTransportEnrollment.discontinue_date.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def update_enrollment(
        self,
        db: AsyncSession,
        enrollment_id: int,
        enrollment_data: StudentTransportEnrollmentUpdate
    ) -> Optional[StudentTransportEnrollment]:
        """Update enrollment"""
        enrollment = await self.get_enrollment_by_id(db, enrollment_id)
        if not enrollment:
            return None
        
        update_data = enrollment_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(enrollment, field, value)
        
        enrollment.updated_at = datetime.now()
        await db.commit()
        await db.refresh(enrollment)
        return enrollment
    
    async def discontinue_enrollment(
        self,
        db: AsyncSession,
        enrollment_id: int,
        discontinue_date: date
    ) -> Optional[StudentTransportEnrollment]:
        """Discontinue transport enrollment"""
        enrollment = await self.get_enrollment_by_id(db, enrollment_id)
        if not enrollment:
            return None
        
        enrollment.discontinue_date = discontinue_date
        enrollment.is_active = False
        enrollment.updated_at = datetime.now()
        
        await db.commit()
        await db.refresh(enrollment)
        return enrollment
    
    async def get_enhanced_transport_summary(
        self,
        db: AsyncSession,
        session_year: str,
        class_id: Optional[int] = None,
        is_enrolled: Optional[bool] = None
    ) -> List[EnhancedStudentTransportSummary]:
        """Get enhanced transport summary using database view"""
        
        query = """
            SELECT
                student_id, admission_number, student_name, class_name, session_year,
                enrollment_id, transport_type_id, transport_type_name,
                enrollment_date, discontinue_date, is_enrolled,
                distance_km, monthly_fee, pickup_location, drop_location,
                total_months_tracked, enabled_months, paid_months, pending_months, overdue_months,
                total_amount, total_paid, total_balance, collection_percentage,
                has_monthly_tracking
            FROM enhanced_student_transport_status
            WHERE session_year = :session_year
        """
        
        params = {"session_year": session_year}
        
        if class_id is not None:
            query += " AND class_id = :class_id"
            params["class_id"] = class_id
        
        if is_enrolled is not None:
            query += " AND is_enrolled = :is_enrolled"
            params["is_enrolled"] = is_enrolled
        
        query += " ORDER BY student_name"
        
        result = await db.execute(text(query), params)
        rows = result.fetchall()
        
        summaries = []
        for row in rows:
            summary = EnhancedStudentTransportSummary(
                student_id=row.student_id,
                admission_number=row.admission_number,
                student_name=row.student_name,
                class_name=row.class_name,
                session_year=row.session_year,
                enrollment_id=row.enrollment_id,
                transport_type_id=row.transport_type_id,
                transport_type_name=row.transport_type_name,
                enrollment_date=row.enrollment_date,
                discontinue_date=row.discontinue_date,
                is_enrolled=row.is_enrolled or False,
                distance_km=row.distance_km,
                monthly_fee=row.monthly_fee,
                pickup_location=row.pickup_location,
                drop_location=row.drop_location,
                total_months_tracked=row.total_months_tracked or 0,
                enabled_months=row.enabled_months or 0,
                paid_months=row.paid_months or 0,
                pending_months=row.pending_months or 0,
                overdue_months=row.overdue_months or 0,
                total_amount=row.total_amount or Decimal('0.0'),
                total_paid=row.total_paid or Decimal('0.0'),
                total_balance=row.total_balance or Decimal('0.0'),
                collection_percentage=row.collection_percentage or Decimal('0.0'),
                has_monthly_tracking=row.has_monthly_tracking or False
            )
            summaries.append(summary)
        
        return summaries


class CRUDTransportMonthlyTracking:
    """CRUD operations for transport monthly tracking"""
    
    async def enable_monthly_tracking(
        self,
        db: AsyncSession,
        enrollment_id: int,
        start_month: int = 4,
        start_year: int = 2025
    ) -> int:
        """Enable monthly tracking using database function"""
        result = await db.execute(
            text("SELECT enable_transport_monthly_tracking(:enrollment_id, :start_month, :start_year)"),
            {
                "enrollment_id": enrollment_id,
                "start_month": start_month,
                "start_year": start_year
            }
        )
        
        records_created = result.scalar()
        await db.commit()
        
        return records_created
    
    async def get_monthly_history(
        self,
        db: AsyncSession,
        student_id: int,
        session_year_id: int
    ) -> Optional[StudentTransportMonthlyHistory]:
        """
        Get monthly transport history for a student
        Shows complete payment history across all enrollments (including discontinued ones)
        """

        # Get ALL enrollments for this student in this session (including discontinued)
        # Order by enrollment_date DESC to get the most recent enrollment first
        enrollment_result = await db.execute(
            select(StudentTransportEnrollment)
            .options(selectinload(StudentTransportEnrollment.transport_type))
            .where(
                and_(
                    StudentTransportEnrollment.student_id == student_id,
                    StudentTransportEnrollment.session_year_id == session_year_id
                )
            )
            .order_by(StudentTransportEnrollment.enrollment_date.desc())
        )
        enrollments = enrollment_result.scalars().all()

        if not enrollments:
            return None

        # Use the most recent enrollment for header information
        current_enrollment = enrollments[0]
        
        # Get student info
        student_result = await db.execute(
            select(Student)
            .options(selectinload(Student.class_ref), selectinload(Student.session_year))
            .where(Student.id == student_id)
        )
        student = student_result.scalar_one_or_none()

        if not student:
            return None

        # Get monthly tracking records for ALL enrollments (to show complete history)
        # This includes records from discontinued enrollments
        enrollment_ids = [e.id for e in enrollments]
        monthly_records_result = await db.execute(
            select(TransportMonthlyTracking)
            .options(selectinload(TransportMonthlyTracking.payment_status))
            .where(TransportMonthlyTracking.enrollment_id.in_(enrollment_ids))
            .order_by(TransportMonthlyTracking.academic_year, TransportMonthlyTracking.academic_month)
        )
        monthly_records = monthly_records_result.scalars().all()
        
        # Build monthly history
        monthly_history = []
        total_paid = Decimal('0.0')
        total_balance = Decimal('0.0')
        paid_months = 0
        pending_months = 0
        overdue_months = 0
        enabled_months = 0
        
        for record in monthly_records:
            if record.is_service_enabled:
                enabled_months += 1
                
                # Calculate balance
                balance = max(Decimal('0.0'), Decimal(str(record.monthly_amount)) - Decimal(str(record.paid_amount)))
                
                # Determine status
                status_name = record.payment_status.description if record.payment_status else "Unknown"
                status_color = record.payment_status.color_code if record.payment_status else "#757575"
                
                # Check if overdue
                is_overdue = False
                days_overdue = None
                if record.due_date < date.today() and balance > 0:
                    is_overdue = True
                    days_overdue = (date.today() - record.due_date).days
                    overdue_months += 1
                elif balance == 0:
                    paid_months += 1
                else:
                    pending_months += 1
                
                total_paid += Decimal(str(record.paid_amount))
                total_balance += balance
                
                monthly_status = TransportMonthlyTrackingResponse(
                    id=record.id,
                    enrollment_id=record.enrollment_id,
                    student_id=record.student_id,
                    session_year_id=record.session_year_id,
                    academic_month=record.academic_month,
                    academic_year=record.academic_year,
                    month_name=record.month_name,
                    is_service_enabled=record.is_service_enabled,
                    monthly_amount=Decimal(str(record.monthly_amount)),
                    paid_amount=Decimal(str(record.paid_amount)),
                    balance_amount=balance,
                    due_date=record.due_date,
                    payment_status_id=record.payment_status_id,
                    status_name=status_name,
                    late_fee=Decimal(str(record.late_fee)),
                    discount_amount=Decimal(str(record.discount_amount)),
                    remarks=record.remarks,
                    created_at=record.created_at,
                    updated_at=record.updated_at
                )
                monthly_history.append(monthly_status)
        
        # Calculate collection percentage based on total expected amount
        # Sum up monthly amounts from all enabled months
        total_expected = sum(Decimal(str(record.monthly_amount)) for record in monthly_records if record.is_service_enabled)
        collection_percentage = (total_paid / total_expected * 100) if total_expected > 0 else Decimal('0.0')

        return StudentTransportMonthlyHistory(
            student_id=student.id,
            student_name=f"{student.first_name} {student.last_name}",
            class_name=student.class_ref.description if student.class_ref else "",
            session_year=student.session_year.name if student.session_year else "",
            transport_type_name=current_enrollment.transport_type.description if current_enrollment.transport_type else "",
            monthly_fee_amount=current_enrollment.monthly_fee,
            monthly_history=monthly_history,
            total_months=len(monthly_records),
            enabled_months=enabled_months,
            paid_months=paid_months,
            pending_months=pending_months,
            overdue_months=overdue_months,
            total_paid=total_paid,
            total_balance=total_balance,
            collection_percentage=collection_percentage
        )


# Create instances
transport_enrollment_crud = CRUDTransportEnrollment()
transport_monthly_tracking_crud = CRUDTransportMonthlyTracking()

