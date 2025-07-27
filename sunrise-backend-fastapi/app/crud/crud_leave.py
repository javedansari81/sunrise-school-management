from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_, or_, func, desc, extract
from datetime import date, datetime

from app.crud.base import CRUDBase
from app.models.leave import LeaveRequest
from app.models.student import Student
from app.models.user import User
from app.schemas.leave import (
    LeaveRequestCreate, LeaveRequestUpdate, LeaveFilters,
    LeaveStatusEnum, LeaveTypeEnum
)


class CRUDLeaveRequest(CRUDBase[LeaveRequest, LeaveRequestCreate, LeaveRequestUpdate]):
    async def get_with_student(self, db: AsyncSession, id: int) -> Optional[LeaveRequest]:
        result = await db.execute(
            select(LeaveRequest)
            .options(
                joinedload(LeaveRequest.student),
                joinedload(LeaveRequest.approver)
            )
            .where(LeaveRequest.id == id)
        )
        return result.scalar_one_or_none()

    async def get_multi_with_filters(
        self,
        db: AsyncSession,
        *,
        filters: LeaveFilters,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[LeaveRequest], int]:
        query = select(LeaveRequest).options(
            joinedload(LeaveRequest.student),
            joinedload(LeaveRequest.approver)
        )
        
        # Apply filters
        conditions = []
        
        if filters.student_id:
            conditions.append(LeaveRequest.student_id == filters.student_id)
        
        if filters.leave_type:
            conditions.append(LeaveRequest.leave_type == filters.leave_type)
        
        if filters.status:
            conditions.append(LeaveRequest.status == filters.status)
        
        if filters.from_date:
            conditions.append(LeaveRequest.start_date >= filters.from_date)
        
        if filters.to_date:
            conditions.append(LeaveRequest.end_date <= filters.to_date)
        
        if filters.class_name:
            conditions.append(Student.current_class == filters.class_name)
            query = query.join(Student)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count(LeaveRequest.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.order_by(desc(LeaveRequest.created_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        
        return result.scalars().all(), total

    async def get_by_student(
        self, db: AsyncSession, *, student_id: int, limit: int = 50
    ) -> List[LeaveRequest]:
        result = await db.execute(
            select(LeaveRequest)
            .options(joinedload(LeaveRequest.approver))
            .where(LeaveRequest.student_id == student_id)
            .order_by(desc(LeaveRequest.created_at))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_pending_requests(self, db: AsyncSession) -> List[LeaveRequest]:
        result = await db.execute(
            select(LeaveRequest)
            .options(
                joinedload(LeaveRequest.student),
                joinedload(LeaveRequest.approver)
            )
            .where(LeaveRequest.status == LeaveStatusEnum.PENDING)
            .order_by(LeaveRequest.created_at)
        )
        return result.scalars().all()

    async def get_requests_by_date_range(
        self,
        db: AsyncSession,
        *,
        start_date: date,
        end_date: date,
        status: Optional[LeaveStatusEnum] = None
    ) -> List[LeaveRequest]:
        query = select(LeaveRequest).options(
            joinedload(LeaveRequest.student),
            joinedload(LeaveRequest.approver)
        ).where(
            and_(
                LeaveRequest.start_date <= end_date,
                LeaveRequest.end_date >= start_date
            )
        )
        
        if status:
            query = query.where(LeaveRequest.status == status)
        
        result = await db.execute(query.order_by(LeaveRequest.start_date))
        return result.scalars().all()

    async def approve_request(
        self,
        db: AsyncSession,
        *,
        leave_request: LeaveRequest,
        approver_id: int,
        status: LeaveStatusEnum,
        rejection_reason: Optional[str] = None
    ) -> LeaveRequest:
        leave_request.status = status
        leave_request.approved_by = approver_id
        leave_request.approved_at = datetime.utcnow()
        
        if rejection_reason:
            leave_request.rejection_reason = rejection_reason
        
        db.add(leave_request)
        await db.commit()
        await db.refresh(leave_request)
        return leave_request

    async def get_leave_statistics(
        self, db: AsyncSession, *, year: Optional[int] = None
    ) -> Dict[str, Any]:
        query = select(
            func.count(LeaveRequest.id).label('total_requests'),
            func.count(
                func.case(
                    (LeaveRequest.status == LeaveStatusEnum.APPROVED, 1),
                    else_=None
                )
            ).label('approved_requests'),
            func.count(
                func.case(
                    (LeaveRequest.status == LeaveStatusEnum.REJECTED, 1),
                    else_=None
                )
            ).label('rejected_requests'),
            func.count(
                func.case(
                    (LeaveRequest.status == LeaveStatusEnum.PENDING, 1),
                    else_=None
                )
            ).label('pending_requests'),
            func.sum(LeaveRequest.total_days).label('total_days')
        )
        
        if year:
            query = query.where(extract('year', LeaveRequest.start_date) == year)
        
        result = await db.execute(query)
        stats = result.first()
        
        # Get leave type breakdown
        type_query = select(
            LeaveRequest.leave_type,
            func.count(LeaveRequest.id).label('count')
        )
        
        if year:
            type_query = type_query.where(extract('year', LeaveRequest.start_date) == year)
        
        type_query = type_query.group_by(LeaveRequest.leave_type)
        type_result = await db.execute(type_query)
        
        type_breakdown = [
            {'leave_type': row.leave_type, 'count': row.count}
            for row in type_result
        ]
        
        return {
            'total_requests': stats.total_requests or 0,
            'approved_requests': stats.approved_requests or 0,
            'rejected_requests': stats.rejected_requests or 0,
            'pending_requests': stats.pending_requests or 0,
            'total_days': stats.total_days or 0,
            'approval_rate': (stats.approved_requests / stats.total_requests * 100) if stats.total_requests else 0,
            'leave_type_breakdown': type_breakdown
        }

    async def get_monthly_leave_trend(
        self, db: AsyncSession, *, year: int
    ) -> List[Dict[str, Any]]:
        result = await db.execute(
            select(
                extract('month', LeaveRequest.start_date).label('month'),
                func.count(LeaveRequest.id).label('count'),
                func.sum(LeaveRequest.total_days).label('total_days')
            )
            .where(extract('year', LeaveRequest.start_date) == year)
            .group_by(extract('month', LeaveRequest.start_date))
            .order_by(extract('month', LeaveRequest.start_date))
        )
        
        return [
            {
                'month': int(row.month),
                'count': row.count,
                'total_days': row.total_days or 0
            }
            for row in result
        ]

    async def get_class_wise_leave_stats(
        self, db: AsyncSession, *, year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        query = select(
            Student.current_class,
            func.count(LeaveRequest.id).label('total_requests'),
            func.sum(LeaveRequest.total_days).label('total_days')
        ).join(Student)
        
        if year:
            query = query.where(extract('year', LeaveRequest.start_date) == year)
        
        query = query.group_by(Student.current_class).order_by(Student.current_class)
        result = await db.execute(query)
        
        return [
            {
                'class_name': row.current_class,
                'total_requests': row.total_requests,
                'total_days': row.total_days or 0
            }
            for row in result
        ]


# Create instance
leave_request_crud = CRUDLeaveRequest(LeaveRequest)
