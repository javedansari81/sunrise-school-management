from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_, or_, func, desc, extract, text
from datetime import date, datetime

from app.crud.base import CRUDBase
from app.models.expense import Expense, Vendor, Budget
from app.models.user import User
from app.models.metadata import ExpenseCategory, ExpenseStatus, PaymentMethod, PaymentStatus, SessionYear
from app.schemas.expense import (
    ExpenseCreate, ExpenseUpdate, ExpenseFilters, ExpenseWithDetails
)


class CRUDExpense(CRUDBase[Expense, ExpenseCreate, ExpenseUpdate]):
    """CRUD operations for Expense with metadata-driven architecture and soft delete support"""

    async def get(self, db: AsyncSession, id: Any) -> Optional[Expense]:
        """Override to exclude soft-deleted records"""
        result = await db.execute(
            select(Expense)
            .where(
                Expense.id == id,
                (Expense.is_deleted == False) | (Expense.is_deleted.is_(None))
            )
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Expense]:
        """Override to exclude soft-deleted records"""
        result = await db.execute(
            select(Expense)
            .where(Expense.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .order_by(Expense.created_at.desc())
        )
        return result.scalars().all()

    async def remove(self, db: AsyncSession, *, id: int) -> Expense:
        """Override to perform soft delete instead of hard delete"""
        from datetime import datetime

        print(f"🔧 CRUDExpense.remove() called for expense ID: {id}")

        try:
            # Get the record without soft delete filtering for deletion
            result = await db.execute(
                select(Expense).where(Expense.id == id)
            )
            obj = result.scalar_one_or_none()

            print(f"🔍 Found expense object: {obj}")
            if obj:
                print(f"🔍 Before soft delete - is_deleted: {obj.is_deleted}, deleted_date: {obj.deleted_date}")

                # Check if already deleted
                if obj.is_deleted:
                    print(f"⚠️ Expense {id} is already soft deleted")
                    return obj

                # Soft delete: set flags and timestamp
                obj.is_deleted = True
                obj.deleted_date = datetime.utcnow()

                print(f"🔍 After setting flags - is_deleted: {obj.is_deleted}, deleted_date: {obj.deleted_date}")

                # Use merge instead of add to handle potential session conflicts
                db.add(obj)
                print(f"🔧 Added object to session, committing...")

                await db.commit()
                print(f"🔧 Commit completed, refreshing object...")

                await db.refresh(obj)
                print(f"🗑️ Soft deleted expense {id}: is_deleted={obj.is_deleted}, deleted_date={obj.deleted_date}")

                # Verify the change was persisted
                verify_result = await db.execute(
                    select(Expense).where(Expense.id == id)
                )
                verify_obj = verify_result.scalar_one_or_none()
                if verify_obj:
                    print(f"✅ Verification - DB shows is_deleted: {verify_obj.is_deleted}, deleted_date: {verify_obj.deleted_date}")
                else:
                    print(f"❌ Verification failed - could not find expense {id} in DB")

            else:
                print(f"❌ No expense found with ID {id}")

            return obj

        except Exception as e:
            print(f"❌ Error in CRUDExpense.remove(): {str(e)}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            raise

    async def soft_delete_expense(self, db: AsyncSession, *, expense_id: int) -> Optional[Expense]:
        """Dedicated method for soft deleting expenses (bypasses base class)"""
        from datetime import datetime
        from sqlalchemy import update

        print(f"🔧 soft_delete_expense() called for expense ID: {expense_id}")

        try:
            # First, get the current expense to verify it exists and is not already deleted
            result = await db.execute(
                select(Expense).where(Expense.id == expense_id)
            )
            expense = result.scalar_one_or_none()

            if not expense:
                print(f"❌ Expense {expense_id} not found")
                return None

            if expense.is_deleted:
                print(f"⚠️ Expense {expense_id} is already deleted")
                return expense

            print(f"🔍 Found expense: {expense.id}, current is_deleted: {expense.is_deleted}")

            # Use UPDATE statement for more reliable transaction handling
            delete_time = datetime.utcnow()

            update_stmt = (
                update(Expense)
                .where(Expense.id == expense_id)
                .values(
                    is_deleted=True,
                    deleted_date=delete_time
                )
            )

            print(f"🔧 Executing UPDATE statement...")
            await db.execute(update_stmt)

            print(f"🔧 Committing transaction...")
            await db.commit()

            # Fetch the updated record to verify
            verify_result = await db.execute(
                select(Expense).where(Expense.id == expense_id)
            )
            updated_expense = verify_result.scalar_one_or_none()

            if updated_expense:
                print(f"✅ Soft delete successful: is_deleted={updated_expense.is_deleted}, deleted_date={updated_expense.deleted_date}")
                return updated_expense
            else:
                print(f"❌ Could not verify soft delete")
                return None

        except Exception as e:
            print(f"❌ Error in soft_delete_expense(): {str(e)}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            raise

    async def create(self, db: AsyncSession, *, obj_in: ExpenseCreate, requested_by: int) -> Expense:
        """Create a new expense record"""
        # Set default status to Pending (ID = 1)
        db_obj = Expense(
            **obj_in.dict(),
            expense_status_id=1,  # Pending status
            payment_status_id=1,  # Pending payment status
            requested_by=requested_by,
            created_at=datetime.utcnow()
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_with_details(self, db: AsyncSession, id: int) -> Optional[ExpenseWithDetails]:
        """Get expense with all related details"""
        query = """
        SELECT
            e.*,
            ec.name as expense_category_name,
            es.name as expense_status_name,
            es.color_code as expense_status_color,
            pm.name as payment_method_name,
            ps.name as payment_status_name,
            ps.color_code as payment_status_color,
            sy.name as session_year_name,
            u1.first_name || ' ' || u1.last_name as requester_name,
            u2.first_name || ' ' || u2.last_name as approver_name
        FROM expenses e
        LEFT JOIN expense_categories ec ON e.expense_category_id = ec.id
        LEFT JOIN expense_statuses es ON e.expense_status_id = es.id
        LEFT JOIN payment_methods pm ON e.payment_method_id = pm.id
        LEFT JOIN payment_statuses ps ON e.payment_status_id = ps.id
        LEFT JOIN session_years sy ON e.session_year_id = sy.id
        LEFT JOIN users u1 ON e.requested_by = u1.id
        LEFT JOIN users u2 ON e.approved_by = u2.id
        WHERE e.id = :expense_id
        """

        result = await db.execute(text(query), {"expense_id": id})
        row = result.fetchone()

        if not row:
            return None

        # Convert row to dictionary
        try:
            if hasattr(row, '_asdict'):
                row_dict = row._asdict()
            else:
                row_dict = dict(zip(result.keys(), row))

            return ExpenseWithDetails(**row_dict)
        except Exception as e:
            print(f"Error converting row to ExpenseWithDetails: {e}")
            return None

    async def get_multi_with_filters(
        self,
        db: AsyncSession,
        *,
        filters: ExpenseFilters,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[ExpenseWithDetails], int]:
        """Get expenses with filters and pagination"""

        # Build WHERE conditions
        where_conditions = []
        params = {}

        if filters.expense_category_id:
            where_conditions.append("e.expense_category_id = :expense_category_id")
            params["expense_category_id"] = filters.expense_category_id

        if filters.expense_status_id:
            where_conditions.append("e.expense_status_id = :expense_status_id")
            params["expense_status_id"] = filters.expense_status_id

        if filters.payment_status_id:
            where_conditions.append("e.payment_status_id = :payment_status_id")
            params["payment_status_id"] = filters.payment_status_id

        if filters.payment_method_id:
            where_conditions.append("e.payment_method_id = :payment_method_id")
            params["payment_method_id"] = filters.payment_method_id

        if filters.from_date:
            where_conditions.append("e.expense_date >= :from_date")
            params["from_date"] = filters.from_date

        if filters.to_date:
            where_conditions.append("e.expense_date <= :to_date")
            params["to_date"] = filters.to_date

        if filters.vendor_name:
            where_conditions.append("e.vendor_name ILIKE :vendor_name")
            params["vendor_name"] = f"%{filters.vendor_name}%"

        if filters.requested_by:
            where_conditions.append("e.requested_by = :requested_by")
            params["requested_by"] = filters.requested_by

        if filters.min_amount:
            where_conditions.append("e.total_amount >= :min_amount")
            params["min_amount"] = filters.min_amount

        if filters.max_amount:
            where_conditions.append("e.total_amount <= :max_amount")
            params["max_amount"] = filters.max_amount

        if filters.session_year_id:
            where_conditions.append("e.session_year_id = :session_year_id")
            params["session_year_id"] = filters.session_year_id

        if filters.priority:
            where_conditions.append("e.priority = :priority")
            params["priority"] = filters.priority

        if filters.is_emergency is not None:
            where_conditions.append("e.is_emergency = :is_emergency")
            params["is_emergency"] = filters.is_emergency

        if filters.is_recurring is not None:
            where_conditions.append("e.is_recurring = :is_recurring")
            params["is_recurring"] = filters.is_recurring

        # Always filter out soft-deleted records
        where_conditions.append("e.is_deleted = FALSE")

        where_clause = "WHERE " + " AND ".join(where_conditions)

        # Count query
        count_query = f"""
        SELECT COUNT(DISTINCT e.id)
        FROM expenses e
        {where_clause}
        """

        count_result = await db.execute(text(count_query), params)
        total = count_result.scalar()

        # Main query with details
        main_query = f"""
        SELECT
            e.*,
            ec.name as expense_category_name,
            es.name as expense_status_name,
            es.color_code as expense_status_color,
            pm.name as payment_method_name,
            ps.name as payment_status_name,
            ps.color_code as payment_status_color,
            sy.name as session_year_name,
            u1.first_name || ' ' || u1.last_name as requester_name,
            u2.first_name || ' ' || u2.last_name as approver_name
        FROM expenses e
        LEFT JOIN expense_categories ec ON e.expense_category_id = ec.id
        LEFT JOIN expense_statuses es ON e.expense_status_id = es.id
        LEFT JOIN payment_methods pm ON e.payment_method_id = pm.id
        LEFT JOIN payment_statuses ps ON e.payment_status_id = ps.id
        LEFT JOIN session_years sy ON e.session_year_id = sy.id
        LEFT JOIN users u1 ON e.requested_by = u1.id
        LEFT JOIN users u2 ON e.approved_by = u2.id
        {where_clause}
        ORDER BY e.created_at DESC
        LIMIT :limit OFFSET :skip
        """

        params.update({"limit": limit, "skip": skip})
        result = await db.execute(text(main_query), params)
        rows = result.fetchall()

        expenses = []
        for row in rows:
            try:
                if hasattr(row, '_asdict'):
                    row_dict = row._asdict()
                else:
                    row_dict = dict(zip(result.keys(), row))
                expenses.append(ExpenseWithDetails(**row_dict))
            except Exception as e:
                print(f"Error converting row: {e}")
                continue

        return expenses, total

    async def get_pending_expenses(self, db: AsyncSession) -> List[ExpenseWithDetails]:
        """Get all pending expense requests"""
        query = """
        SELECT
            e.*,
            ec.name as expense_category_name,
            es.name as expense_status_name,
            es.color_code as expense_status_color,
            pm.name as payment_method_name,
            ps.name as payment_status_name,
            ps.color_code as payment_status_color,
            sy.name as session_year_name,
            u1.first_name || ' ' || u1.last_name as requester_name,
            u2.first_name || ' ' || u2.last_name as approver_name
        FROM expenses e
        LEFT JOIN expense_categories ec ON e.expense_category_id = ec.id
        LEFT JOIN expense_statuses es ON e.expense_status_id = es.id
        LEFT JOIN payment_methods pm ON e.payment_method_id = pm.id
        LEFT JOIN payment_statuses ps ON e.payment_status_id = ps.id
        LEFT JOIN session_years sy ON e.session_year_id = sy.id
        LEFT JOIN users u1 ON e.requested_by = u1.id
        LEFT JOIN users u2 ON e.approved_by = u2.id
        WHERE e.expense_status_id = 1
        ORDER BY e.created_at ASC
        """

        result = await db.execute(text(query))
        rows = result.fetchall()

        expenses = []
        for row in rows:
            try:
                if hasattr(row, '_asdict'):
                    row_dict = row._asdict()
                else:
                    row_dict = dict(zip(result.keys(), row))
                expenses.append(ExpenseWithDetails(**row_dict))
            except Exception as e:
                print(f"Error converting row: {e}")
                continue
        return expenses

    async def get_by_requester(
        self,
        db: AsyncSession,
        *,
        requester_id: int,
        limit: int = 50
    ) -> List[ExpenseWithDetails]:
        """Get expenses by requester"""
        query = """
        SELECT
            e.*,
            ec.name as expense_category_name,
            es.name as expense_status_name,
            es.color_code as expense_status_color,
            pm.name as payment_method_name,
            ps.name as payment_status_name,
            ps.color_code as payment_status_color,
            sy.name as session_year_name,
            u1.first_name || ' ' || u1.last_name as requester_name,
            u2.first_name || ' ' || u2.last_name as approver_name
        FROM expenses e
        LEFT JOIN expense_categories ec ON e.expense_category_id = ec.id
        LEFT JOIN expense_statuses es ON e.expense_status_id = es.id
        LEFT JOIN payment_methods pm ON e.payment_method_id = pm.id
        LEFT JOIN payment_statuses ps ON e.payment_status_id = ps.id
        LEFT JOIN session_years sy ON e.session_year_id = sy.id
        LEFT JOIN users u1 ON e.requested_by = u1.id
        LEFT JOIN users u2 ON e.approved_by = u2.id
        WHERE e.requested_by = :requester_id
        ORDER BY e.created_at DESC
        LIMIT :limit
        """

        result = await db.execute(text(query), {
            "requester_id": requester_id,
            "limit": limit
        })
        rows = result.fetchall()

        expenses = []
        for row in rows:
            try:
                if hasattr(row, '_asdict'):
                    row_dict = row._asdict()
                else:
                    row_dict = dict(zip(result.keys(), row))
                expenses.append(ExpenseWithDetails(**row_dict))
            except Exception as e:
                print(f"Error converting row: {e}")
                continue
        return expenses

    async def approve_expense(
        self,
        db: AsyncSession,
        *,
        expense: Expense,
        approver_id: int,
        expense_status_id: int,
        approval_comments: Optional[str] = None
    ) -> Expense:
        """Approve or reject an expense request"""
        expense.expense_status_id = expense_status_id
        expense.approved_by = approver_id
        expense.approved_at = datetime.utcnow()

        if approval_comments:
            expense.approval_comments = approval_comments

        db.add(expense)
        await db.commit()
        await db.refresh(expense)
        return expense

    async def get_expense_statistics(
        self, db: AsyncSession, *, year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get comprehensive expense statistics"""
        # Build WHERE clause with soft delete filtering
        where_conditions = ["e.is_deleted = FALSE"]

        if year:
            where_conditions.append(f"EXTRACT(year FROM e.expense_date) = {year}")

        where_clause = "WHERE " + " AND ".join(where_conditions)

        query = f"""
        SELECT
            -- Total expenses excludes rejected expenses (status_id = 3)
            COUNT(CASE WHEN e.expense_status_id != 3 THEN 1 END) as total_expenses,
            COUNT(CASE WHEN e.expense_status_id = 2 THEN 1 END) as approved_expenses,
            COUNT(CASE WHEN e.expense_status_id = 3 THEN 1 END) as rejected_expenses,
            COUNT(CASE WHEN e.expense_status_id = 1 THEN 1 END) as pending_expenses,
            -- Total amount excludes rejected expenses
            SUM(CASE WHEN e.expense_status_id != 3 THEN e.total_amount ELSE 0 END) as total_amount,
            SUM(CASE WHEN e.expense_status_id = 2 THEN e.total_amount ELSE 0 END) as approved_amount,
            SUM(CASE WHEN e.expense_status_id = 3 THEN e.total_amount ELSE 0 END) as rejected_amount,
            SUM(CASE WHEN e.expense_status_id = 1 THEN e.total_amount ELSE 0 END) as pending_amount
        FROM expenses e
        {where_clause}
        """

        print(f"🔍 Executing statistics query: {query}")
        result = await db.execute(text(query))
        stats = result.fetchone()
        print(f"📊 Raw query result: {stats}")

        if not stats:
            print("⚠️ No statistics data returned from query")
            return {
                'total_expenses': 0,
                'approved_expenses': 0,
                'rejected_expenses': 0,
                'pending_expenses': 0,
                'total_amount': 0,
                'approved_amount': 0,
                'rejected_amount': 0,
                'pending_amount': 0,
                'category_breakdown': [],
                'payment_method_breakdown': []
            }

        # Get category breakdown (excluding rejected expenses)
        category_where_conditions = where_conditions + ["e.expense_status_id != 3"]
        category_where_clause = "WHERE " + " AND ".join(category_where_conditions)

        category_query = f"""
        SELECT
            ec.name as category_name,
            COUNT(e.id) as count,
            SUM(e.total_amount) as amount
        FROM expenses e
        JOIN expense_categories ec ON e.expense_category_id = ec.id
        {category_where_clause}
        GROUP BY ec.id, ec.name
        ORDER BY amount DESC
        """

        category_result = await db.execute(text(category_query))
        category_breakdown = [
            {
                'category': row.category_name,
                'count': row.count,
                'amount': float(row.amount) if row.amount else 0
            }
            for row in category_result
        ]

        # Get payment method breakdown (excluding rejected expenses)
        payment_where_conditions = where_conditions + ["e.expense_status_id != 3"]
        payment_where_clause = "WHERE " + " AND ".join(payment_where_conditions)

        payment_query = f"""
        SELECT
            pm.name as payment_method_name,
            COUNT(e.id) as count,
            SUM(e.total_amount) as amount
        FROM expenses e
        JOIN payment_methods pm ON e.payment_method_id = pm.id
        {payment_where_clause}
        GROUP BY pm.id, pm.name
        ORDER BY amount DESC
        """

        payment_result = await db.execute(text(payment_query))
        payment_breakdown = [
            {
                'payment_method': row.payment_method_name,
                'count': row.count,
                'amount': float(row.amount) if row.amount else 0
            }
            for row in payment_result
        ]

        final_stats = {
            'total_expenses': stats.total_expenses or 0,
            'approved_expenses': stats.approved_expenses or 0,
            'rejected_expenses': stats.rejected_expenses or 0,
            'pending_expenses': stats.pending_expenses or 0,
            'total_amount': float(stats.total_amount) if stats.total_amount else 0,
            'approved_amount': float(stats.approved_amount) if stats.approved_amount else 0,
            'rejected_amount': float(stats.rejected_amount) if stats.rejected_amount else 0,
            'pending_amount': float(stats.pending_amount) if stats.pending_amount else 0,
            'category_breakdown': category_breakdown,
            'payment_method_breakdown': payment_breakdown
        }

        print(f"📈 Final statistics result: {final_stats}")
        return final_stats

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


class CRUDVendor(CRUDBase[Vendor, dict, dict]):
    """CRUD operations for Vendor"""

    async def get_active_vendors(self, db: AsyncSession) -> List[Vendor]:
        """Get all active vendors"""
        result = await db.execute(
            select(Vendor)
            .where(Vendor.is_active == True)
            .order_by(Vendor.vendor_name)
        )
        return result.scalars().all()

    async def get_by_category(
        self,
        db: AsyncSession,
        *,
        category_id: int
    ) -> List[Vendor]:
        """Get vendors by category"""
        result = await db.execute(
            select(Vendor)
            .where(
                and_(
                    Vendor.is_active == True,
                    Vendor.vendor_categories.contains([category_id])
                )
            )
        )
        return result.scalars().all()


# Create instances
expense_crud = CRUDExpense(Expense)
vendor_crud = CRUDVendor(Vendor)
