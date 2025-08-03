from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from decimal import Decimal
import math

from app.core.database import get_db
from app.crud.crud_expense import expense_crud, vendor_crud
from app.crud import user_crud
from app.schemas.expense import (
    Expense, ExpenseCreate, ExpenseUpdate, ExpenseWithDetails,
    ExpenseApproval, ExpenseFilters, ExpenseListResponse, ExpenseReport,
    ExpenseDashboard, Vendor, VendorCreate, VendorUpdate
)
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=ExpenseListResponse)
async def get_expenses(
    expense_category_id: Optional[int] = None,
    expense_status_id: Optional[int] = None,
    payment_status_id: Optional[int] = None,
    payment_method_id: Optional[int] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    vendor_name: Optional[str] = None,
    requested_by: Optional[int] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    session_year_id: Optional[int] = None,
    priority: Optional[str] = None,
    is_emergency: Optional[bool] = None,
    is_recurring: Optional[bool] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get expenses with comprehensive filters using metadata-driven architecture
    """
    filters = ExpenseFilters(
        expense_category_id=expense_category_id,
        expense_status_id=expense_status_id,
        payment_status_id=payment_status_id,
        payment_method_id=payment_method_id,
        from_date=from_date,
        to_date=to_date,
        vendor_name=vendor_name,
        requested_by=requested_by,
        min_amount=min_amount,
        max_amount=max_amount,
        session_year_id=session_year_id,
        priority=priority,
        is_emergency=is_emergency,
        is_recurring=is_recurring
    )

    skip = (page - 1) * per_page
    expenses, total = await expense_crud.get_multi_with_filters(
        db, filters=filters, skip=skip, limit=per_page
    )

    # Get summary statistics
    summary = await expense_crud.get_expense_statistics(db)

    total_pages = math.ceil(total / per_page)

    return ExpenseListResponse(
        expenses=expenses,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        summary=summary
    )


@router.post("/", response_model=Expense)
async def create_expense(
    expense_data: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new expense record
    """
    try:
        # Log the incoming data for debugging
        print(f"🔍 Creating expense with data: {expense_data.dict()}")
        print(f"👤 User: {current_user.id} ({current_user.email})")

        # Validate total amount (allow for small rounding differences)
        expected_total = expense_data.amount + expense_data.tax_amount
        if abs(expense_data.total_amount - expected_total) > 0.01:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Total amount ({expense_data.total_amount}) must equal amount ({expense_data.amount}) plus tax amount ({expense_data.tax_amount}). Expected: {expected_total}"
            )

        expense = await expense_crud.create(
            db, obj_in=expense_data, requested_by=current_user.id
        )
        print(f"✅ Expense created successfully with ID: {expense.id}")
        return expense

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"❌ Error creating expense: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create expense: {str(e)}"
        )


@router.get("/{expense_id}", response_model=ExpenseWithDetails)
async def get_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get specific expense details with all related information
    """
    expense = await expense_crud.get_with_details(db, id=expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    return expense


@router.put("/{expense_id}", response_model=Expense)
async def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an expense record (only allowed for pending expenses)
    """
    expense = await expense_crud.get(db, id=expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    # Only allow updates for pending expenses
    if expense.expense_status_id != 1:  # Not pending
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only update pending expenses"
        )

    # Only allow the requester to update their own expense
    if expense.requested_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only update your own expenses"
        )

    updated_expense = await expense_crud.update(db, db_obj=expense, obj_in=expense_data)
    return updated_expense


@router.put("/{expense_id}", response_model=Expense)
async def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update expense record (only if pending or by requester)
    """
    expense = await expense_crud.get(db, id=expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    # Only allow updates if status is pending or user is the requester
    if expense.expense_status_id != 1 and expense.requested_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update expense that is not pending or not requested by you"
        )

    # Validate total amount if provided
    amount = expense_data.amount or expense.amount
    tax_amount = expense_data.tax_amount or expense.tax_amount
    total_amount = expense_data.total_amount or expense.total_amount

    if expense_data.amount or expense_data.tax_amount or expense_data.total_amount:
        if total_amount != amount + tax_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Total amount must equal amount plus tax amount"
            )

    updated_expense = await expense_crud.update(
        db, db_obj=expense, obj_in=expense_data
    )
    return updated_expense


@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Soft delete expense record (sets is_deleted = TRUE and deleted_date = NOW())
    """
    try:
        print(f"🗑️ Attempting to soft delete expense {expense_id} by user {current_user.id} ({current_user.email})")

        # Get expense without soft delete filtering to allow deletion of any existing record
        from sqlalchemy import select
        result = await db.execute(select(Expense).where(Expense.id == expense_id))
        expense = result.scalar_one_or_none()

        if not expense:
            print(f"❌ Expense {expense_id} not found in database")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )

        # Check if already deleted
        if expense.is_deleted:
            print(f"⚠️ Expense {expense_id} is already deleted (deleted_date: {expense.deleted_date})")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Expense is already deleted"
            )

        print(f"📋 Found active expense: ID={expense.id}, Status={expense.expense_status_id}, Requester={expense.requested_by}, Amount=₹{expense.total_amount}")

        # Authorization check: Admin users or the original requester can delete
        is_admin = current_user.user_type_id == 1  # Assuming 1 is admin user type
        is_requester = expense.requested_by == current_user.id

        if not (is_admin or is_requester):
            print(f"❌ User {current_user.id} not authorized to delete expense {expense_id} (not admin and not requester)")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own expenses unless you are an admin"
            )

        print(f"✅ User authorized to delete expense {expense_id} (admin: {is_admin}, requester: {is_requester})")

        # Debug: Check expense state before deletion
        print(f"🔍 Before deletion - is_deleted: {expense.is_deleted}, deleted_date: {expense.deleted_date}")

        # Perform soft delete using dedicated method
        print(f"🔧 Calling expense_crud.soft_delete_expense() for expense {expense_id}")
        deleted_expense = await expense_crud.soft_delete_expense(db, expense_id=expense_id)
        print(f"🔍 After soft_delete_expense() - returned object: {deleted_expense}")

        if deleted_expense:
            print(f"🔍 After deletion - is_deleted: {deleted_expense.is_deleted}, deleted_date: {deleted_expense.deleted_date}")

        if deleted_expense and deleted_expense.is_deleted:
            print(f"🗑️ Expense {expense_id} soft deleted successfully at {deleted_expense.deleted_date}")
            return {
                "message": "Expense deleted successfully",
                "expense_id": expense_id,
                "deleted_date": deleted_expense.deleted_date.isoformat() if deleted_expense.deleted_date else None
            }
        else:
            print(f"❌ Failed to soft delete expense {expense_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete expense"
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Unexpected error deleting expense {expense_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete expense: {str(e)}"
        )


@router.patch("/{expense_id}/approve", response_model=Expense)
async def approve_expense(
    expense_id: int,
    approval_data: ExpenseApproval,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Approve or reject an expense
    """
    expense = await expense_crud.get(db, id=expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    # Only allow approval/rejection if status is pending
    if expense.expense_status_id != 1:  # Not pending
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expense is not pending"
        )

    updated_expense = await expense_crud.approve_expense(
        db,
        expense=expense,
        approver_id=current_user.id,
        expense_status_id=approval_data.expense_status_id,
        approval_comments=approval_data.approval_comments
    )

    return updated_expense


@router.get("/categories")
async def get_expense_categories():
    """
    Get all expense categories
    """
    return {
        "categories": [category.value for category in ExpenseCategoryEnum]
    }


@router.get("/pending")
async def get_pending_expenses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all pending expenses for approval
    """
    pending_expenses = await expense_crud.get_pending_expenses(db)

    # Convert to response format with user details
    pending_list = []
    for expense in pending_expenses:
        expense_dict = {
            **expense.__dict__,
            "requester_name": f"{expense.requester.first_name} {expense.requester.last_name}"
        }
        pending_list.append(expense_dict)

    return {
        "pending_expenses": pending_list,
        "total_pending": len(pending_list)
    }


@router.get("/my-expenses")
async def get_my_expenses(
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get expenses requested by current user
    """
    my_expenses = await expense_crud.get_by_requester(
        db, requester_id=current_user.id, limit=limit
    )

    return {
        "my_expenses": my_expenses,
        "total": len(my_expenses)
    }


@router.get("/reports/monthly")
async def get_monthly_expense_report(
    year: int = Query(..., description="Year for the report"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get monthly expense report
    """
    # Get monthly trend
    monthly_trend = await expense_crud.get_monthly_expense_trend(db, year=year)

    # Get overall statistics for the year
    stats = await expense_crud.get_expense_statistics(db, year=year)

    return {
        "year": year,
        "monthly_breakdown": monthly_trend,
        "summary": {
            "total_expenses": stats['total_expenses'],
            "total_amount": stats['total_amount'],
            "approved_amount": stats['approved_amount'],
            "pending_amount": stats['pending_amount'],
            "pending_count": stats['pending_count']
        },
        "category_breakdown": stats['category_breakdown']
    }


@router.get("/reports/yearly")
async def get_yearly_expense_report(
    year: Optional[int] = Query(None, description="Year for the report"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get yearly expense report
    """
    # Get overall statistics
    stats = await expense_crud.get_expense_statistics(db, year=year)

    # Get vendor-wise breakdown
    vendor_breakdown = await expense_crud.get_vendor_wise_expenses(db, year=year)

    monthly_breakdown = []
    if year:
        monthly_breakdown = await expense_crud.get_monthly_expense_trend(db, year=year)

    return {
        "year": year or "All Time",
        "summary": {
            "total_expenses": stats['total_expenses'],
            "total_amount": stats['total_amount'],
            "approved_amount": stats['approved_amount'],
            "pending_amount": stats['pending_amount'],
            "pending_count": stats['pending_count']
        },
        "monthly_breakdown": monthly_breakdown,
        "category_breakdown": stats['category_breakdown'],
        "vendor_breakdown": vendor_breakdown
    }


@router.get("/debug")
async def debug_expense_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Debug endpoint to check expense data consistency"""
    try:
        from sqlalchemy import text

        # Get total count
        count_result = await db.execute(text("SELECT COUNT(*) as count FROM expenses"))
        total_count = count_result.fetchone()

        # Get all expenses with soft delete info
        all_expenses_result = await db.execute(text("""
            SELECT id, description, total_amount, expense_status_id, expense_date,
                   is_deleted, deleted_date
            FROM expenses
            ORDER BY expense_date DESC
        """))
        all_expenses = [dict(row._mapping) for row in all_expenses_result.fetchall()]

        # Get active expenses count
        active_count_result = await db.execute(text("SELECT COUNT(*) as count FROM expenses WHERE is_deleted = FALSE"))
        active_count = active_count_result.fetchone()

        # Get deleted expenses count
        deleted_count_result = await db.execute(text("SELECT COUNT(*) as count FROM expenses WHERE is_deleted = TRUE"))
        deleted_count = deleted_count_result.fetchone()

        # Get statistics
        stats = await expense_crud.get_expense_statistics(db)

        return {
            "total_count": total_count.count if total_count else 0,
            "active_count": active_count.count if active_count else 0,
            "deleted_count": deleted_count.count if deleted_count else 0,
            "all_expenses": all_expenses,
            "statistics": stats,
            "debug_info": {
                "user_id": current_user.id,
                "user_email": current_user.email
            }
        }
    except Exception as e:
        print(f"❌ Debug endpoint error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug failed: {str(e)}"
        )


@router.post("/debug/test-soft-delete/{expense_id}")
async def test_soft_delete(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Debug endpoint to test soft delete functionality directly"""
    try:
        print(f"🧪 Testing soft delete for expense {expense_id}")

        # Test the dedicated soft delete method
        result = await expense_crud.soft_delete_expense(db, expense_id=expense_id)

        return {
            "message": "Soft delete test completed",
            "expense_id": expense_id,
            "result": {
                "found": result is not None,
                "is_deleted": result.is_deleted if result else None,
                "deleted_date": result.deleted_date.isoformat() if result and result.deleted_date else None
            }
        }
    except Exception as e:
        print(f"❌ Test soft delete error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test failed: {str(e)}"
        )


@router.post("/debug/manual-update/{expense_id}")
async def manual_update_test(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Debug endpoint to test manual database update"""
    try:
        from datetime import datetime
        from sqlalchemy import text

        print(f"🧪 Manual update test for expense {expense_id}")

        # Check current state
        check_result = await db.execute(
            text("SELECT id, description, is_deleted, deleted_date FROM expenses WHERE id = :id"),
            {"id": expense_id}
        )
        current_state = check_result.fetchone()
        print(f"🔍 Current state: {dict(current_state._mapping) if current_state else 'Not found'}")

        if not current_state:
            return {"error": "Expense not found", "expense_id": expense_id}

        # Try manual update using raw SQL
        delete_time = datetime.utcnow()
        print(f"🔧 Attempting manual update with timestamp: {delete_time}")

        update_result = await db.execute(
            text("UPDATE expenses SET is_deleted = TRUE, deleted_date = :delete_time WHERE id = :id"),
            {"id": expense_id, "delete_time": delete_time}
        )

        print(f"🔧 Update result rowcount: {update_result.rowcount}")

        # Commit the transaction
        await db.commit()
        print(f"🔧 Transaction committed")

        # Check the result
        verify_result = await db.execute(
            text("SELECT id, description, is_deleted, deleted_date FROM expenses WHERE id = :id"),
            {"id": expense_id}
        )
        final_state = verify_result.fetchone()
        print(f"✅ Final state: {dict(final_state._mapping) if final_state else 'Not found'}")

        return {
            "message": "Manual update test completed",
            "expense_id": expense_id,
            "before": dict(current_state._mapping) if current_state else None,
            "after": dict(final_state._mapping) if final_state else None,
            "rows_affected": update_result.rowcount
        }

    except Exception as e:
        print(f"❌ Manual update test error: {str(e)}")
        import traceback
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Manual update test failed: {str(e)}"
        )


@router.post("/debug/simple-test/{expense_id}")
async def simple_database_test(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Simple test to check database connectivity and basic operations"""
    try:
        from sqlalchemy import text
        from datetime import datetime

        print(f"🧪 Simple database test for expense {expense_id}")

        # Test 1: Check if we can read the expense
        print("🔍 Test 1: Reading expense...")
        read_result = await db.execute(
            text("SELECT id, description, is_deleted, deleted_date FROM expenses WHERE id = :id"),
            {"id": expense_id}
        )
        current_record = read_result.fetchone()
        print(f"📋 Current record: {dict(current_record._mapping) if current_record else 'Not found'}")

        if not current_record:
            return {"error": "Expense not found", "expense_id": expense_id}

        # Test 2: Try a simple UPDATE without transaction
        print("🔧 Test 2: Simple UPDATE...")
        now = datetime.utcnow()

        # Use a simple UPDATE statement
        update_result = await db.execute(
            text("UPDATE expenses SET is_deleted = :is_deleted, deleted_date = :deleted_date WHERE id = :id"),
            {
                "id": expense_id,
                "is_deleted": True,
                "deleted_date": now
            }
        )
        print(f"📊 Update result - rows affected: {update_result.rowcount}")

        # Test 3: Check if the update is visible before commit
        print("🔍 Test 3: Check before commit...")
        check_before_commit = await db.execute(
            text("SELECT id, description, is_deleted, deleted_date FROM expenses WHERE id = :id"),
            {"id": expense_id}
        )
        before_commit_record = check_before_commit.fetchone()
        print(f"📋 Before commit: {dict(before_commit_record._mapping) if before_commit_record else 'Not found'}")

        # Test 4: Commit and check again
        print("🔧 Test 4: Committing...")
        await db.commit()
        print("✅ Commit completed")

        # Test 5: Final verification
        print("🔍 Test 5: Final verification...")
        final_result = await db.execute(
            text("SELECT id, description, is_deleted, deleted_date FROM expenses WHERE id = :id"),
            {"id": expense_id}
        )
        final_record = final_result.fetchone()
        print(f"📋 Final record: {dict(final_record._mapping) if final_record else 'Not found'}")

        return {
            "message": "Simple database test completed",
            "expense_id": expense_id,
            "tests": {
                "initial_record": dict(current_record._mapping) if current_record else None,
                "rows_affected": update_result.rowcount,
                "before_commit": dict(before_commit_record._mapping) if before_commit_record else None,
                "final_record": dict(final_record._mapping) if final_record else None
            }
        }

    except Exception as e:
        print(f"❌ Simple database test error: {str(e)}")
        import traceback
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simple test failed: {str(e)}"
        )


@router.get("/statistics")
async def get_expense_statistics(
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get expense statistics for the frontend summary cards
    """
    try:
        print(f"🔍 Getting expense statistics for year: {year}")

        # First, let's check if there are any expenses at all
        from sqlalchemy import text
        count_result = await db.execute(text("SELECT COUNT(*) as count FROM expenses"))
        total_count = count_result.fetchone()
        print(f"📋 Total expenses in database: {total_count.count if total_count else 0}")

        # Check a sample of expenses
        sample_result = await db.execute(text("SELECT id, description, total_amount, expense_status_id FROM expenses LIMIT 5"))
        sample_expenses = sample_result.fetchall()
        print(f"📝 Sample expenses: {[dict(row._mapping) for row in sample_expenses]}")

        stats = await expense_crud.get_expense_statistics(db, year=year)
        print(f"📊 Statistics retrieved: {stats}")
        return stats
    except Exception as e:
        print(f"❌ Error getting expense statistics: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get expense statistics: {str(e)}"
        )


@router.get("/dashboard", response_model=ExpenseDashboard)
async def get_expense_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get expense management dashboard data
    """
    # Get overall statistics
    stats = await expense_crud.get_expense_statistics(db)

    # Get recent expenses
    recent_expenses = await expense_crud.get_recent_expenses(db, limit=10)

    # Convert recent expenses to response format
    recent_list = []
    for expense in recent_expenses:
        expense_dict = {
            **expense.__dict__,
            "requester_name": f"{expense.requester.first_name} {expense.requester.last_name}",
            "approver_name": f"{expense.approver.first_name} {expense.approver.last_name}" if expense.approver else None
        }
        recent_list.append(expense_dict)

    return ExpenseDashboard(
        total_expenses=stats['total_amount'],
        pending_approvals=stats['pending_expenses'],  # Fixed: was 'pending_count'
        monthly_budget_utilization=0.0,  # TODO: Calculate budget utilization
        top_categories=stats['category_breakdown'][:5],  # Top 5 categories
        recent_expenses=recent_list,
        monthly_trend=[],  # TODO: Add monthly trend
        urgent_expenses=[]  # TODO: Add urgent expenses
    )
