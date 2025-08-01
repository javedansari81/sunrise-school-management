from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_, or_, func, extract, case, exists
from datetime import date, datetime

from app.crud.base import CRUDBase
from app.models.fee import FeeStructure, FeeRecord, FeePayment
from app.models.student import Student
from app.models.user import User
from app.models.metadata import SessionYear, PaymentStatus
from app.schemas.fee import (
    FeeStructureCreate, FeeStructureUpdate,
    FeeRecordCreate, FeeRecordUpdate,
    FeePaymentCreate, FeePaymentUpdate,
    FeeFilters, PaymentStatusEnum, SessionYearEnum
)


class CRUDFeeStructure(CRUDBase[FeeStructure, FeeStructureCreate, FeeStructureUpdate]):
    async def get_by_class_and_session(
        self, db: AsyncSession, *, class_name: str, session_year: str
    ) -> Optional[FeeStructure]:
        result = await db.execute(
            select(FeeStructure).where(
                and_(
                    FeeStructure.class_name == class_name,
                    FeeStructure.session_year.has(name=session_year)
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_all_structures(self, db: AsyncSession) -> List[FeeStructure]:
        result = await db.execute(select(FeeStructure).order_by(FeeStructure.class_name))
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
        
        if filters.class_name:
            conditions.append(Student.class_ref.has(name=filters.class_name))
            query = query.join(Student)
        
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
            # Join is already handled by joinedload, so we don't need to add it again

        if conditions:
            query = query.where(and_(*conditions))

        # Add sorting
        sort_column = FeeRecord.due_date  # default
        if sort_by == "student_name":
            sort_column = func.concat(Student.first_name, ' ', Student.last_name)
            # Join is already handled by joinedload
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
        query = select(FeeRecord).where(FeeRecord.student_id == student_id)
        
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
            fee_record.payment_status_id = PaymentStatusEnum.VALUE.PAID
            fee_record.balance_amount = 0
        elif fee_record.paid_amount > 0:
            fee_record.payment_status_id = PaymentStatusEnum.VALUE.PARTIAL
        
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
            fee_record.payment_status_id = PaymentStatusEnum.VALUE.PAID
            fee_record.balance_amount = 0
        elif fee_record.paid_amount > 0:
            fee_record.payment_status_id = PaymentStatusEnum.VALUE.PARTIAL
        
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

# Create instances
fee_structure_crud = CRUDFeeStructure(FeeStructure)
fee_record_crud = CRUDFeeRecord(FeeRecord)
fee_payment_crud = CRUDFeePayment(FeePayment)
