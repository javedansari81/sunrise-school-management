from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_, or_, func, desc, extract
from datetime import date, datetime

from app.crud.base import CRUDBase
from app.models.expense import Expense
from app.models.user import User
from app.schemas.expense import (
    ExpenseCreate, ExpenseUpdate, ExpenseFilters,
    ExpenseStatusEnum, ExpenseCategoryEnum
)


class CRUDExpense(CRUDBase[Expense, ExpenseCreate, ExpenseUpdate]):
    async def get_with_users(self, db: AsyncSession, id: int) -> Optional[Expense]:
        result = await db.execute(
            select(Expense)
            .options(
                joinedload(Expense.requester),
                joinedload(Expense.approver)
            )
            .where(Expense.id == id)
        )
        return result.scalar_one_or_none()

    async def get_multi_with_filters(
        self,
        db: AsyncSession,
        *,
        filters: ExpenseFilters,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Expense], int]:
        query = select(Expense).options(
            joinedload(Expense.requester),
            joinedload(Expense.approver)
        )
        
        # Apply filters
        conditions = []
        
        if filters.category:
            conditions.append(Expense.category == filters.category)
        
        if filters.status:
            conditions.append(Expense.status == filters.status)
        
        if filters.from_date:
            conditions.append(Expense.expense_date >= filters.from_date)
        
        if filters.to_date:
            conditions.append(Expense.expense_date <= filters.to_date)
        
        if filters.vendor_name:
            conditions.append(Expense.vendor_name.ilike(f"%{filters.vendor_name}%"))
        
        if filters.requested_by:
            conditions.append(Expense.requested_by == filters.requested_by)
        
        if filters.min_amount:
            conditions.append(Expense.total_amount >= filters.min_amount)
        
        if filters.max_amount:
            conditions.append(Expense.total_amount <= filters.max_amount)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count(Expense.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.order_by(desc(Expense.created_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        
        return result.scalars().all(), total

    async def create_expense(
        self, db: AsyncSession, *, obj_in: ExpenseCreate, requested_by: int
    ) -> Expense:
        obj_in_data = obj_in.dict()
        obj_in_data['requested_by'] = requested_by
        obj_in_data['status'] = ExpenseStatusEnum.PENDING
        
        db_obj = Expense(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_pending_expenses(self, db: AsyncSession) -> List[Expense]:
        result = await db.execute(
            select(Expense)
            .options(
                joinedload(Expense.requester),
                joinedload(Expense.approver)
            )
            .where(Expense.status == ExpenseStatusEnum.PENDING)
            .order_by(Expense.created_at)
        )
        return result.scalars().all()

    async def get_by_requester(
        self, db: AsyncSession, *, requester_id: int, limit: int = 50
    ) -> List[Expense]:
        result = await db.execute(
            select(Expense)
            .options(joinedload(Expense.approver))
            .where(Expense.requested_by == requester_id)
            .order_by(desc(Expense.created_at))
            .limit(limit)
        )
        return result.scalars().all()

    async def approve_expense(
        self,
        db: AsyncSession,
        *,
        expense: Expense,
        approver_id: int,
        status: ExpenseStatusEnum,
        rejection_reason: Optional[str] = None
    ) -> Expense:
        expense.status = status
        expense.approved_by = approver_id
        expense.approved_at = datetime.utcnow()
        
        if rejection_reason:
            expense.rejection_reason = rejection_reason
        
        db.add(expense)
        await db.commit()
        await db.refresh(expense)
        return expense

    async def get_expense_statistics(
        self, db: AsyncSession, *, year: Optional[int] = None
    ) -> Dict[str, Any]:
        query = select(
            func.count(Expense.id).label('total_expenses'),
            func.sum(Expense.total_amount).label('total_amount'),
            func.sum(
                func.case(
                    (Expense.status == ExpenseStatusEnum.APPROVED, Expense.total_amount),
                    else_=0
                )
            ).label('approved_amount'),
            func.sum(
                func.case(
                    (Expense.status == ExpenseStatusEnum.PENDING, Expense.total_amount),
                    else_=0
                )
            ).label('pending_amount'),
            func.count(
                func.case(
                    (Expense.status == ExpenseStatusEnum.PENDING, 1),
                    else_=None
                )
            ).label('pending_count')
        )
        
        if year:
            query = query.where(extract('year', Expense.expense_date) == year)
        
        result = await db.execute(query)
        stats = result.first()
        
        # Get category breakdown
        category_query = select(
            Expense.category,
            func.count(Expense.id).label('count'),
            func.sum(Expense.total_amount).label('total_amount')
        )
        
        if year:
            category_query = category_query.where(extract('year', Expense.expense_date) == year)
        
        category_query = category_query.group_by(Expense.category)
        category_result = await db.execute(category_query)
        
        category_breakdown = [
            {
                'category': row.category,
                'count': row.count,
                'total_amount': float(row.total_amount or 0)
            }
            for row in category_result
        ]
        
        return {
            'total_expenses': stats.total_expenses or 0,
            'total_amount': float(stats.total_amount or 0),
            'approved_amount': float(stats.approved_amount or 0),
            'pending_amount': float(stats.pending_amount or 0),
            'pending_count': stats.pending_count or 0,
            'category_breakdown': category_breakdown
        }

    async def get_monthly_expense_trend(
        self, db: AsyncSession, *, year: int
    ) -> List[Dict[str, Any]]:
        result = await db.execute(
            select(
                extract('month', Expense.expense_date).label('month'),
                func.count(Expense.id).label('count'),
                func.sum(Expense.total_amount).label('total_amount')
            )
            .where(extract('year', Expense.expense_date) == year)
            .group_by(extract('month', Expense.expense_date))
            .order_by(extract('month', Expense.expense_date))
        )
        
        return [
            {
                'month': int(row.month),
                'count': row.count,
                'total_amount': float(row.total_amount or 0)
            }
            for row in result
        ]

    async def get_vendor_wise_expenses(
        self, db: AsyncSession, *, year: Optional[int] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        query = select(
            Expense.vendor_name,
            func.count(Expense.id).label('count'),
            func.sum(Expense.total_amount).label('total_amount')
        ).where(Expense.vendor_name.isnot(None))
        
        if year:
            query = query.where(extract('year', Expense.expense_date) == year)
        
        query = (
            query.group_by(Expense.vendor_name)
            .order_by(desc(func.sum(Expense.total_amount)))
            .limit(limit)
        )
        
        result = await db.execute(query)
        
        return [
            {
                'vendor_name': row.vendor_name,
                'count': row.count,
                'total_amount': float(row.total_amount or 0)
            }
            for row in result
        ]

    async def get_recent_expenses(
        self, db: AsyncSession, *, limit: int = 10
    ) -> List[Expense]:
        result = await db.execute(
            select(Expense)
            .options(
                joinedload(Expense.requester),
                joinedload(Expense.approver)
            )
            .order_by(desc(Expense.created_at))
            .limit(limit)
        )
        return result.scalars().all()

    async def search_expenses(
        self, db: AsyncSession, *, search_term: str, limit: int = 20
    ) -> List[Expense]:
        search_conditions = [
            Expense.title.ilike(f"%{search_term}%"),
            Expense.description.ilike(f"%{search_term}%"),
            Expense.vendor_name.ilike(f"%{search_term}%"),
            Expense.invoice_number.ilike(f"%{search_term}%")
        ]
        
        result = await db.execute(
            select(Expense)
            .options(
                joinedload(Expense.requester),
                joinedload(Expense.approver)
            )
            .where(or_(*search_conditions))
            .order_by(desc(Expense.created_at))
            .limit(limit)
        )
        return result.scalars().all()


# Create instance
expense_crud = CRUDExpense(Expense)
