"""
Admin Dashboard Endpoints
Aggregates statistics from multiple services for dashboard overview
"""
from typing import Optional, Tuple
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, func, select, text
from datetime import datetime, timedelta, date
import logging
import traceback

from app.core.database import get_db
from app.crud import fee_record_crud, student_crud, teacher_crud
from app.crud.crud_expense import expense_crud
from app.crud.crud_leave import leave_request_crud
from app.crud.crud_inventory_stock import crud_inventory_stock
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.metadata import SessionYear
from app.models.expense import Expense as ExpenseModel
from app.models.fee import FeeRecord as FeeRecordModel, FeePayment as FeePaymentModel

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_session_year_details(
    db: AsyncSession,
    session_year_id: Optional[int] = None
) -> Tuple[int, str, Optional[date], Optional[date]]:
    """
    Get session year details from database.
    If session_year_id is None, fetches the current session (is_current=True).

    Returns: (session_year_id, session_year_name, start_date, end_date)
    """
    if session_year_id is None:
        # Fetch current session year (where is_current = True)
        query = select(SessionYear).where(
            and_(SessionYear.is_current == True, SessionYear.is_active == True)
        )
    else:
        # Fetch specific session year
        query = select(SessionYear).where(SessionYear.id == session_year_id)

    result = await db.execute(query)
    session = result.scalar_one_or_none()

    if session:
        return (session.id, session.name, session.start_date, session.end_date)

    # Fallback if no session found (should not happen in normal operation)
    logger.warning(f"Session year not found for id={session_year_id}, using defaults")
    return (4, "2025-26", None, None)


@router.get("/admin-dashboard-stats")
async def get_admin_dashboard_stats(
    session_year_id: Optional[int] = None,  # None = use current session (is_current=True)
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get comprehensive dashboard statistics for admin dashboard overview
    Includes students, teachers, fees, leave requests, and expenses data

    Session filtering:
    - Students: Filtered by session_year_id (📅)
    - Fees: Filtered by session_year_id (📅)
    - Leave Requests: Filtered by session date range (📅)
    - Expenses: Filtered by session date range (📅)
    - Teachers: Not filtered - all time data (🌐)
    - Inventory: Not filtered - operational data (🌐)
    """
    # Get session year details from database (uses is_current=True if session_year_id is None)
    session_year_id, session_year_name, session_start_date, session_end_date = await get_session_year_details(
        db, session_year_id
    )

    logger.info(f"=== Starting get_admin_dashboard_stats ===")
    logger.info(f"Session: id={session_year_id}, name={session_year_name}, start={session_start_date}, end={session_end_date}")

    try:
        # Get current date for time-based calculations
        logger.info("Calculating date ranges...")
        current_date = datetime.now().date()
        current_month_start = current_date.replace(day=1)
        last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        current_week_start = current_date - timedelta(days=current_date.weekday())
        logger.info(f"Date ranges: current_date={current_date}, current_month_start={current_month_start}, current_week_start={current_week_start}")

        # Initialize response data with defaults
        response_data = {
            "session_info": {
                "id": session_year_id,
                "name": session_year_name,
                "start_date": session_start_date.isoformat() if session_start_date else None,
                "end_date": session_end_date.isoformat() if session_end_date else None
            },
            "students": {"total": 0, "added_this_month": 0, "change_text": "+0 this month", "is_session_filtered": True},
            "teachers": {"total": 0, "added_this_month": 0, "change_text": "+0 this month", "is_session_filtered": False},
            "fees": {"pending_amount": 0, "collected_this_week": 0, "change_text": "-₹0 this week", "total_collected": 0, "collection_rate": 0, "is_session_filtered": True},
            "leave_requests": {"total": 0, "pending": 0, "change_text": "0 pending approval", "is_session_filtered": True},
            "expenses": {"current_month": 0, "last_month": 0, "change": 0, "change_text": "+₹0 from last month", "is_session_filtered": True},
            "revenue_growth": {"percentage": 0, "current_quarter": 0, "last_quarter": 0, "change_text": "+0.0% from last quarter", "is_session_filtered": True}
        }

        # 1. Get student statistics (SESSION FILTERED 📅)
        try:
            logger.info("Section 1: Fetching student statistics (session filtered)...")

            # Get total students for the selected session year
            total_students_query = select(func.count(Student.id)).where(
                and_(
                    Student.is_active == True,
                    or_(Student.is_deleted == False, Student.is_deleted.is_(None)),
                    Student.session_year_id == session_year_id
                )
            )
            total_students_result = await db.execute(total_students_query)
            total_students = total_students_result.scalar() or 0
            logger.info(f"Total students for session {session_year_name}: {total_students}")

            # Calculate students added this month for the session
            students_this_month_query = select(func.count(Student.id)).where(
                and_(
                    Student.is_active == True,
                    or_(Student.is_deleted == False, Student.is_deleted.is_(None)),
                    Student.session_year_id == session_year_id,
                    Student.created_at >= current_month_start
                )
            )
            students_this_month_result = await db.execute(students_this_month_query)
            students_this_month = students_this_month_result.scalar() or 0
            logger.info(f"Students added this month: {students_this_month}")

            response_data["students"] = {
                "total": total_students,
                "added_this_month": students_this_month,
                "change_text": f"+{students_this_month} this month",
                "is_session_filtered": True
            }
            logger.info("✓ Section 1 completed successfully")
        except Exception as e:
            logger.error(f"✗ Section 1 FAILED - Student statistics error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            response_data["students"]["error"] = str(e)

        # 2. Get teacher statistics (NOT SESSION FILTERED 🌐)
        try:
            logger.info("Section 2: Fetching teacher statistics (all time)...")
            teacher_stats = await teacher_crud.get_dashboard_stats(db)
            logger.info(f"Teacher stats retrieved: {teacher_stats}")

            # Calculate teachers added this month
            logger.info("Calculating teachers added this month...")
            teachers_this_month_query = select(func.count(Teacher.id)).where(
                and_(
                    Teacher.is_active == True,
                    or_(Teacher.is_deleted == False, Teacher.is_deleted.is_(None)),
                    Teacher.created_at >= current_month_start
                )
            )
            teachers_this_month_result = await db.execute(teachers_this_month_query)
            teachers_this_month = teachers_this_month_result.scalar() or 0
            logger.info(f"Teachers added this month: {teachers_this_month}")

            response_data["teachers"] = {
                "total": teacher_stats['total_teachers'],
                "added_this_month": teachers_this_month,
                "change_text": f"+{teachers_this_month} this month",
                "is_session_filtered": False  # Teachers are not session-specific
            }
            logger.info("✓ Section 2 completed successfully")
        except Exception as e:
            logger.error(f"✗ Section 2 FAILED - Teacher statistics error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            response_data["teachers"]["error"] = str(e)

        # 3. Get fee statistics for the session year (SESSION FILTERED 📅)
        try:
            logger.info("Section 3: Fetching fee statistics (session filtered)...")
            # Use session_year_name from database instead of hardcoded mapping
            logger.info(f"Using session year: {session_year_name}")

            logger.info("Fetching fee collection summary...")
            fee_summary = await fee_record_crud.get_collection_summary(db, session_year=session_year_name)
            logger.info(f"Fee summary retrieved: {fee_summary}")

            # Get fees collected this week
            logger.info("Calculating fees collected this week...")
            fees_this_week_query = select(func.sum(FeePaymentModel.amount)).join(
                FeeRecordModel
            ).where(
                and_(
                    FeePaymentModel.payment_date >= current_week_start,
                    FeeRecordModel.session_year_id == session_year_id
                )
            )
            fees_this_week_result = await db.execute(fees_this_week_query)
            fees_collected_this_week = float(fees_this_week_result.scalar() or 0)
            logger.info(f"Fees collected this week: {fees_collected_this_week}")

            response_data["fees"] = {
                "pending_amount": fee_summary['pending_amount'],
                "collected_this_week": fees_collected_this_week,
                "change_text": f"-₹{fees_collected_this_week:,.0f} this week",
                "total_collected": fee_summary['paid_amount'],
                "collection_rate": fee_summary['collection_rate'],
                "is_session_filtered": True
            }
            logger.info("✓ Section 3 completed successfully")
        except Exception as e:
            logger.error(f"✗ Section 3 FAILED - Fee statistics error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            response_data["fees"]["error"] = str(e)

        # 4. Get leave request statistics (SESSION FILTERED 📅 by session_year_id)
        try:
            logger.info("Section 4: Fetching leave request statistics (session filtered by session_year_id)...")

            # Build leave query with session_year_id filter
            if session_year_id:
                leave_query = text("""
                    SELECT
                        COUNT(*) as total_requests,
                        COUNT(CASE WHEN leave_status_id = 1 THEN 1 END) as pending_requests,
                        COUNT(CASE WHEN leave_status_id = 2 THEN 1 END) as approved_requests,
                        COUNT(CASE WHEN leave_status_id = 3 THEN 1 END) as rejected_requests
                    FROM sunrise.leave_requests
                    WHERE session_year_id = :session_year_id
                """)
                leave_result = await db.execute(
                    leave_query,
                    {"session_year_id": session_year_id}
                )
                leave_row = leave_result.fetchone()
                leave_stats = {
                    'total_requests': leave_row.total_requests or 0,
                    'pending_requests': leave_row.pending_requests or 0,
                    'approved_requests': leave_row.approved_requests or 0,
                    'rejected_requests': leave_row.rejected_requests or 0
                }
            else:
                # Fallback to all-time stats if no session_year_id available
                leave_stats = await leave_request_crud.get_leave_statistics(db)

            logger.info(f"Leave stats retrieved: {leave_stats}")

            response_data["leave_requests"] = {
                "total": leave_stats.get('total_requests', 0),
                "pending": leave_stats.get('pending_requests', 0),
                "change_text": f"{leave_stats.get('pending_requests', 0)} pending approval",
                "is_session_filtered": True
            }
            logger.info("✓ Section 4 completed successfully")
        except Exception as e:
            logger.error(f"✗ Section 4 FAILED - Leave statistics error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            response_data["leave_requests"]["error"] = str(e)

        # 5. Calculate expenses (SESSION FILTERED 📅 by session_year_id)
        try:
            logger.info("Section 5: Calculating expense statistics (session filtered by session_year_id)...")

            if session_year_id:
                # Get total expenses for the session using session_year_id
                logger.info(f"Fetching expenses for session_year_id: {session_year_id}")
                session_expenses_query = select(func.sum(ExpenseModel.amount)).where(
                    and_(
                        ExpenseModel.session_year_id == session_year_id,
                        ExpenseModel.is_deleted != True,
                        ExpenseModel.expense_status_id.in_([2, 4])  # Approved or Paid
                    )
                )
                session_expenses_result = await db.execute(session_expenses_query)
                session_total_expenses = float(session_expenses_result.scalar() or 0)

                # Get current month expenses within session
                current_month_expenses_query = select(func.sum(ExpenseModel.amount)).where(
                    and_(
                        ExpenseModel.expense_date >= current_month_start,
                        ExpenseModel.expense_date <= current_date,
                        ExpenseModel.session_year_id == session_year_id,
                        ExpenseModel.is_deleted != True,
                        ExpenseModel.expense_status_id.in_([2, 4])
                    )
                )
                current_month_expenses_result = await db.execute(current_month_expenses_query)
                current_month_expenses = float(current_month_expenses_result.scalar() or 0)

                # Get last month expenses within session
                last_month_expenses_query = select(func.sum(ExpenseModel.amount)).where(
                    and_(
                        ExpenseModel.expense_date >= last_month_start,
                        ExpenseModel.expense_date < current_month_start,
                        ExpenseModel.session_year_id == session_year_id,
                        ExpenseModel.is_deleted != True,
                        ExpenseModel.expense_status_id.in_([2, 4])
                    )
                )
                last_month_expenses_result = await db.execute(last_month_expenses_query)
                last_month_expenses = float(last_month_expenses_result.scalar() or 0)
            else:
                # Fallback to all-time if no session dates
                current_month_expenses_query = select(func.sum(ExpenseModel.amount)).where(
                    and_(
                        ExpenseModel.expense_date >= current_month_start,
                        ExpenseModel.expense_date <= current_date,
                        ExpenseModel.is_deleted != True,
                        ExpenseModel.expense_status_id.in_([2, 4])
                    )
                )
                current_month_expenses_result = await db.execute(current_month_expenses_query)
                current_month_expenses = float(current_month_expenses_result.scalar() or 0)

                last_month_expenses_query = select(func.sum(ExpenseModel.amount)).where(
                    and_(
                        ExpenseModel.expense_date >= last_month_start,
                        ExpenseModel.expense_date < current_month_start,
                        ExpenseModel.is_deleted != True,
                        ExpenseModel.expense_status_id.in_([2, 4])
                    )
                )
                last_month_expenses_result = await db.execute(last_month_expenses_query)
                last_month_expenses = float(last_month_expenses_result.scalar() or 0)

            logger.info(f"Current month expenses: {current_month_expenses}")
            logger.info(f"Last month expenses: {last_month_expenses}")

            # Calculate expense change
            expense_change = current_month_expenses - last_month_expenses
            logger.info(f"Expense change: {expense_change}")

            response_data["expenses"] = {
                "current_month": current_month_expenses,
                "last_month": last_month_expenses,
                "change": expense_change,
                "change_text": f"+₹{expense_change:,.0f} from last month" if expense_change >= 0 else f"-₹{abs(expense_change):,.0f} from last month",
                "is_session_filtered": True
            }
            logger.info("✓ Section 5 completed successfully")
        except Exception as e:
            logger.error(f"✗ Section 5 FAILED - Expense statistics error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            response_data["expenses"]["error"] = str(e)

        # 6. Calculate revenue growth (fees collected vs last quarter)
        try:
            logger.info("Section 6: Calculating revenue growth...")
            # Get current quarter fees
            current_quarter_start = current_date.replace(month=((current_date.month - 1) // 3) * 3 + 1, day=1)
            last_quarter_start = (current_quarter_start - timedelta(days=90)).replace(day=1)
            logger.info(f"Quarter ranges: current_quarter_start={current_quarter_start}, last_quarter_start={last_quarter_start}")

            logger.info("Fetching current quarter fees...")
            current_quarter_fees_query = select(func.sum(FeePaymentModel.amount)).join(
                FeeRecordModel
            ).where(
                and_(
                    FeePaymentModel.payment_date >= current_quarter_start,
                    FeeRecordModel.session_year_id == session_year_id
                )
            )
            current_quarter_fees_result = await db.execute(current_quarter_fees_query)
            current_quarter_fees = float(current_quarter_fees_result.scalar() or 0)
            logger.info(f"Current quarter fees: {current_quarter_fees}")

            logger.info("Fetching last quarter fees...")
            last_quarter_fees_query = select(func.sum(FeePaymentModel.amount)).join(
                FeeRecordModel
            ).where(
                and_(
                    FeePaymentModel.payment_date >= last_quarter_start,
                    FeePaymentModel.payment_date < current_quarter_start,
                    FeeRecordModel.session_year_id == session_year_id
                )
            )
            last_quarter_fees_result = await db.execute(last_quarter_fees_query)
            last_quarter_fees = float(last_quarter_fees_result.scalar() or 0)
            logger.info(f"Last quarter fees: {last_quarter_fees}")

            # Calculate revenue growth percentage
            revenue_growth = 0.0
            if last_quarter_fees > 0:
                revenue_growth = ((current_quarter_fees - last_quarter_fees) / last_quarter_fees) * 100
            logger.info(f"Revenue growth: {revenue_growth}%")

            response_data["revenue_growth"] = {
                "percentage": round(revenue_growth, 1),
                "current_quarter": current_quarter_fees,
                "last_quarter": last_quarter_fees,
                "change_text": f"+{revenue_growth:.1f}% from last quarter" if revenue_growth >= 0 else f"{revenue_growth:.1f}% from last quarter",
                "is_session_filtered": True
            }
            logger.info("✓ Section 6 completed successfully")
        except Exception as e:
            logger.error(f"✗ Section 6 FAILED - Revenue growth error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            response_data["revenue_growth"]["error"] = str(e)

        # Section 7: Inventory Stock Alerts (NOT SESSION FILTERED 🌐)
        logger.info("--- Section 7: Inventory Stock Alerts (operational data) ---")
        try:
            low_stock_items = await crud_inventory_stock.get_low_stock_alerts(db)
            critical_count = sum(1 for item in low_stock_items if item.current_quantity == 0)
            warning_count = len(low_stock_items) - critical_count

            response_data["inventory_stock_alerts"] = {
                "total_alerts": len(low_stock_items),
                "critical_count": critical_count,
                "warning_count": warning_count,
                "alerts": [
                    {
                        "item_name": item.item_type.description,
                        "size": item.size_type.name if item.size_type else "N/A",
                        "current_quantity": item.current_quantity,
                        "minimum_threshold": item.minimum_threshold,
                        "alert_level": "CRITICAL" if item.current_quantity == 0 else "WARNING"
                    }
                    for item in low_stock_items[:10]  # Limit to top 10 for dashboard
                ],
                "is_session_filtered": False  # Inventory is operational data
            }
            logger.info(f"Stock alerts: {len(low_stock_items)} total, {critical_count} critical, {warning_count} warning")
            logger.info("✓ Section 7 completed successfully")
        except Exception as e:
            logger.error(f"✗ Section 7 FAILED - Inventory stock alerts error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            response_data["inventory_stock_alerts"] = {
                "total_alerts": 0,
                "critical_count": 0,
                "warning_count": 0,
                "alerts": [],
                "error": str(e),
                "is_session_filtered": False
            }

        logger.info("=== get_admin_dashboard_stats completed successfully ===")
        logger.info(f"Final response data: {response_data}")
        return response_data

    except Exception as e:
        logger.error(f"=== CRITICAL ERROR in get_admin_dashboard_stats ===")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to fetch admin dashboard statistics",
                "message": str(e),
                "traceback": traceback.format_exc()
            }
        )


@router.get("/admin-dashboard-enhanced-stats")
async def get_admin_dashboard_enhanced_stats(
    session_year_id: Optional[int] = None,  # None = use current session (is_current=True)
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get enhanced dashboard statistics with detailed breakdowns for charts and visualizations
    Includes: student class breakdown, fee collection monthly trends, expense category breakdown,
    leave type breakdown, teacher department breakdown, and transport service statistics

    Session filtering:
    - Students: Filtered by session_year_id (📅)
    - Fees: Filtered by session_year_id (📅)
    - Leave Requests: Filtered by session date range (📅)
    - Expenses: Filtered by session date range (📅)
    - Teachers: Not filtered - all time data (🌐)
    - Transport: Filtered by session_year_id (📅)
    """
    # Get session year details from database (uses is_current=True if session_year_id is None)
    session_year_id, session_year_name, session_start_date, session_end_date = await get_session_year_details(
        db, session_year_id
    )

    logger.info(f"=== Starting get_admin_dashboard_enhanced_stats ===")
    logger.info(f"Session: id={session_year_id}, name={session_year_name}, start={session_start_date}, end={session_end_date}")

    try:
        # Get current date for time-based calculations
        current_date = datetime.now().date()
        current_month_start = current_date.replace(day=1)

        response_data = {
            "session_info": {
                "id": session_year_id,
                "name": session_year_name,
                "start_date": session_start_date.isoformat() if session_start_date else None,
                "end_date": session_end_date.isoformat() if session_end_date else None
            }
        }

        # 1. Student Management - Detailed Statistics (SESSION FILTERED 📅)
        try:
            # Get class-wise breakdown for the selected session (excluding soft deleted)
            class_breakdown_query = text("""
                SELECT
                    c.description as class_name,
                    COUNT(s.id) as total_students,
                    COUNT(CASE WHEN s.gender_id = 1 THEN 1 END) as male_count,
                    COUNT(CASE WHEN s.gender_id = 2 THEN 1 END) as female_count
                FROM sunrise.students s
                LEFT JOIN sunrise.classes c ON s.class_id = c.id
                WHERE s.is_active = TRUE
                    AND (s.is_deleted = FALSE OR s.is_deleted IS NULL)
                    AND s.session_year_id = :session_year_id
                GROUP BY c.id, c.description
                ORDER BY c.id
            """)
            class_result = await db.execute(class_breakdown_query, {"session_year_id": session_year_id})
            class_breakdown = [
                {
                    'class_name': row.class_name or 'Not Assigned',
                    'total': row.total_students,
                    'male': row.male_count,
                    'female': row.female_count
                }
                for row in class_result
            ]

            # Get total and active/inactive counts for the session (excluding soft deleted)
            # Note: total_students counts only active students (is_active=TRUE) to match the basic stats
            student_stats_query = text("""
                SELECT
                    COUNT(CASE WHEN is_active = TRUE THEN 1 END) as total_students,
                    COUNT(CASE WHEN is_active = TRUE THEN 1 END) as active_students,
                    COUNT(CASE WHEN is_active = FALSE THEN 1 END) as inactive_students,
                    COUNT(CASE WHEN is_active = TRUE AND created_at >= :month_start THEN 1 END) as recent_enrollments
                FROM sunrise.students
                WHERE (is_deleted = FALSE OR is_deleted IS NULL)
                    AND session_year_id = :session_year_id
            """)
            student_stats_result = await db.execute(
                student_stats_query,
                {"month_start": current_month_start, "session_year_id": session_year_id}
            )
            student_stats = student_stats_result.fetchone()

            response_data['student_management'] = {
                'total_students': student_stats.total_students,
                'active_students': student_stats.active_students,
                'inactive_students': student_stats.inactive_students,
                'recent_enrollments': student_stats.recent_enrollments,
                'class_breakdown': class_breakdown,
                'is_session_filtered': True
            }
        except Exception as e:
            logger.error(f"Error fetching student statistics: {str(e)}")
            response_data['student_management'] = {'error': str(e), 'is_session_filtered': True}

        # 2. Fee Management - Detailed Statistics (SESSION FILTERED 📅)
        try:
            # Get collection summary using session_year_name from database
            fee_summary = await fee_record_crud.get_collection_summary(db, session_year=session_year_name)

            # Get monthly collection trends (last 12 months)
            monthly_trends_query = text("""
                SELECT
                    TO_CHAR(fp.payment_date, 'Mon YYYY') as month,
                    EXTRACT(YEAR FROM fp.payment_date) as year,
                    EXTRACT(MONTH FROM fp.payment_date) as month_num,
                    SUM(fp.amount) as total_collected,
                    COUNT(DISTINCT fp.fee_record_id) as payment_count
                FROM sunrise.fee_payments fp
                JOIN sunrise.fee_records fr ON fp.fee_record_id = fr.id
                WHERE fp.payment_date >= :start_date
                    AND fr.session_year_id = :session_year_id
                GROUP BY EXTRACT(YEAR FROM fp.payment_date), EXTRACT(MONTH FROM fp.payment_date), TO_CHAR(fp.payment_date, 'Mon YYYY')
                ORDER BY year, month_num
            """)
            monthly_result = await db.execute(
                monthly_trends_query,
                {
                    "start_date": current_date - timedelta(days=365),
                    "session_year_id": session_year_id
                }
            )
            monthly_trends = [
                {
                    'month': row.month,
                    'amount': float(row.total_collected),
                    'count': row.payment_count
                }
                for row in monthly_result
            ]

            response_data['fee_management'] = {
                'total_collected': float(fee_summary['paid_amount']),
                'pending_fees': float(fee_summary['pending_amount']),
                'collection_rate': float(fee_summary['collection_rate']),
                'total_records': fee_summary['total_records'],
                'paid_records': fee_summary['paid_records'],
                'monthly_trends': monthly_trends,
                'is_session_filtered': True
            }
        except Exception as e:
            logger.error(f"Error fetching fee statistics: {str(e)}")
            response_data['fee_management'] = {'error': str(e), 'is_session_filtered': True}

        # 3. Leave Management - Detailed Statistics (SESSION FILTERED 📅 by session_year_id)
        try:
            # Build leave query with session_year_id filter
            if session_year_id:
                leave_stats_query = text("""
                    SELECT
                        COUNT(*) as total_requests,
                        COUNT(CASE WHEN leave_status_id = 1 THEN 1 END) as pending_requests,
                        COUNT(CASE WHEN leave_status_id = 2 THEN 1 END) as approved_requests,
                        COUNT(CASE WHEN leave_status_id = 3 THEN 1 END) as rejected_requests
                    FROM sunrise.leave_requests
                    WHERE session_year_id = :session_year_id
                """)
                leave_stats_result = await db.execute(
                    leave_stats_query,
                    {"session_year_id": session_year_id}
                )
                leave_row = leave_stats_result.fetchone()
                leave_stats = {
                    'total_requests': leave_row.total_requests or 0,
                    'pending_requests': leave_row.pending_requests or 0,
                    'approved_requests': leave_row.approved_requests or 0,
                    'rejected_requests': leave_row.rejected_requests or 0
                }

                # Get leave type breakdown for the session period
                leave_type_query = text("""
                    SELECT
                        lt.description as leave_type,
                        COUNT(lr.id) as count,
                        COUNT(CASE WHEN lr.leave_status_id = 2 THEN 1 END) as approved,
                        COUNT(CASE WHEN lr.leave_status_id = 3 THEN 1 END) as rejected,
                        COUNT(CASE WHEN lr.leave_status_id = 1 THEN 1 END) as pending
                    FROM sunrise.leave_requests lr
                    LEFT JOIN sunrise.leave_types lt ON lr.leave_type_id = lt.id
                    WHERE lr.session_year_id = :session_year_id
                    GROUP BY lt.id, lt.description
                    ORDER BY count DESC
                """)
                leave_type_result = await db.execute(
                    leave_type_query,
                    {"session_year_id": session_year_id}
                )
            else:
                # Fallback to all-time stats if no session dates available
                leave_stats = await leave_request_crud.get_leave_statistics(db)
                leave_type_query = text("""
                    SELECT
                        lt.description as leave_type,
                        COUNT(lr.id) as count,
                        COUNT(CASE WHEN lr.leave_status_id = 2 THEN 1 END) as approved,
                        COUNT(CASE WHEN lr.leave_status_id = 3 THEN 1 END) as rejected,
                        COUNT(CASE WHEN lr.leave_status_id = 1 THEN 1 END) as pending
                    FROM sunrise.leave_requests lr
                    LEFT JOIN sunrise.leave_types lt ON lr.leave_type_id = lt.id
                    GROUP BY lt.id, lt.description
                    ORDER BY count DESC
                """)
                leave_type_result = await db.execute(leave_type_query)

            leave_type_breakdown = [
                {
                    'type': row.leave_type or 'Not Specified',
                    'total': row.count,
                    'approved': row.approved,
                    'rejected': row.rejected,
                    'pending': row.pending
                }
                for row in leave_type_result
            ]

            response_data['leave_management'] = {
                'total_requests': leave_stats.get('total_requests', 0),
                'pending_approvals': leave_stats.get('pending_requests', 0),
                'approved_count': leave_stats.get('approved_requests', 0),
                'rejected_count': leave_stats.get('rejected_requests', 0),
                'leave_type_breakdown': leave_type_breakdown,
                'is_session_filtered': True
            }
        except Exception as e:
            logger.error(f"Error fetching leave statistics: {str(e)}")
            response_data['leave_management'] = {'error': str(e), 'is_session_filtered': True}

        # 4. Expense Management - Detailed Statistics (SESSION FILTERED 📅 by session_year_id)
        try:
            # Get expense statistics for the session period
            if session_year_id:
                expense_stats_query = text("""
                    SELECT
                        COALESCE(SUM(total_amount), 0) as total_amount,
                        COUNT(CASE WHEN expense_status_id = 1 THEN 1 END) as pending_expenses
                    FROM sunrise.expenses
                    WHERE session_year_id = :session_year_id
                        AND is_deleted = FALSE
                """)
                expense_stats_result = await db.execute(
                    expense_stats_query,
                    {"session_year_id": session_year_id}
                )
                expense_row = expense_stats_result.fetchone()

                # Get category breakdown for session period
                category_query = text("""
                    SELECT
                        ec.description as category,
                        COALESCE(SUM(e.total_amount), 0) as amount
                    FROM sunrise.expenses e
                    LEFT JOIN sunrise.expense_categories ec ON e.expense_category_id = ec.id
                    WHERE e.session_year_id = :session_year_id
                        AND e.is_deleted = FALSE
                        AND e.expense_status_id IN (2, 4)
                    GROUP BY ec.id, ec.description
                    ORDER BY amount DESC
                """)
                category_result = await db.execute(
                    category_query,
                    {"session_year_id": session_year_id}
                )
                category_breakdown = [
                    {'category': row.category or 'Uncategorized', 'amount': float(row.amount)}
                    for row in category_result
                ]

                expense_stats = {
                    'total_amount': float(expense_row.total_amount or 0),
                    'pending_expenses': expense_row.pending_expenses or 0,
                    'category_breakdown': category_breakdown
                }

                # Get monthly spending trends within session period
                expense_monthly_query = text("""
                    SELECT
                        TO_CHAR(e.expense_date, 'Mon YYYY') as month,
                        EXTRACT(YEAR FROM e.expense_date) as year,
                        EXTRACT(MONTH FROM e.expense_date) as month_num,
                        SUM(e.total_amount) as total_amount,
                        COUNT(e.id) as expense_count
                    FROM sunrise.expenses e
                    WHERE e.session_year_id = :session_year_id
                        AND e.is_deleted = FALSE
                        AND e.expense_status_id IN (2, 4)
                    GROUP BY EXTRACT(YEAR FROM e.expense_date), EXTRACT(MONTH FROM e.expense_date), TO_CHAR(e.expense_date, 'Mon YYYY')
                    ORDER BY year, month_num
                """)
                expense_monthly_result = await db.execute(
                    expense_monthly_query,
                    {"session_year_id": session_year_id}
                )
            else:
                # Fallback to all-time stats
                expense_stats = await expense_crud.get_expense_statistics(db)
                expense_monthly_query = text("""
                    SELECT
                        TO_CHAR(e.expense_date, 'Mon YYYY') as month,
                        EXTRACT(YEAR FROM e.expense_date) as year,
                        EXTRACT(MONTH FROM e.expense_date) as month_num,
                        SUM(e.total_amount) as total_amount,
                        COUNT(e.id) as expense_count
                    FROM sunrise.expenses e
                    WHERE e.expense_date >= :start_date
                        AND e.is_deleted = FALSE
                        AND e.expense_status_id IN (2, 4)
                    GROUP BY EXTRACT(YEAR FROM e.expense_date), EXTRACT(MONTH FROM e.expense_date), TO_CHAR(e.expense_date, 'Mon YYYY')
                    ORDER BY year, month_num
                """)
                expense_monthly_result = await db.execute(
                    expense_monthly_query,
                    {"start_date": current_date - timedelta(days=365)}
                )

            expense_monthly_trends = [
                {
                    'month': row.month,
                    'amount': float(row.total_amount),
                    'count': row.expense_count
                }
                for row in expense_monthly_result
            ]

            response_data['expense_management'] = {
                'total_expenses': float(expense_stats['total_amount']),
                'pending_approvals': expense_stats['pending_expenses'],
                'category_breakdown': expense_stats['category_breakdown'],
                'monthly_trends': expense_monthly_trends,
                'is_session_filtered': True
            }
        except Exception as e:
            logger.error(f"Error fetching expense statistics: {str(e)}")
            response_data['expense_management'] = {'error': str(e), 'is_session_filtered': True}

        # 5. Staff Management - Detailed Statistics (NOT SESSION FILTERED 🌐)
        try:
            teacher_stats = await teacher_crud.get_dashboard_stats(db)

            response_data['staff_management'] = {
                'total_staff': teacher_stats['total_teachers'],
                'active_staff': teacher_stats['active_teachers'],
                'inactive_staff': teacher_stats['total_teachers'] - teacher_stats['active_teachers'],
                'department_breakdown': teacher_stats['departments'],
                'qualification_breakdown': teacher_stats['qualification_breakdown'],
                'is_session_filtered': False  # Staff is not session-specific
            }
        except Exception as e:
            logger.error(f"Error fetching staff statistics: {str(e)}")
            response_data['staff_management'] = {'error': str(e), 'is_session_filtered': False}

        # 6. Transport Service - Detailed Statistics (SESSION FILTERED 📅)
        try:
            # Get transport enrollment statistics
            transport_stats_query = text("""
                SELECT
                    COUNT(DISTINCT ste.id) as total_enrollments,
                    COUNT(DISTINCT ste.student_id) as students_using_transport,
                    COUNT(DISTINCT tt.id) as transport_types,
                    COALESCE(SUM(CASE WHEN tmt.payment_status_id = 1 THEN tmt.monthly_amount - tmt.paid_amount ELSE 0 END), 0) as pending_transport_fees,
                    COALESCE(SUM(tmt.paid_amount), 0) as collected_transport_fees
                FROM sunrise.student_transport_enrollment ste
                LEFT JOIN sunrise.transport_types tt ON ste.transport_type_id = tt.id
                LEFT JOIN sunrise.transport_monthly_tracking tmt ON ste.id = tmt.enrollment_id
                WHERE ste.session_year_id = :session_year_id
                    AND ste.is_active = TRUE
            """)
            transport_stats_result = await db.execute(
                transport_stats_query,
                {"session_year_id": session_year_id}
            )
            transport_stats = transport_stats_result.fetchone()

            # Get transport type breakdown (Van, E-Rickshaw counts)
            transport_type_query = text("""
                SELECT
                    tt.name as transport_type_name,
                    tt.description as transport_type,
                    COUNT(ste.id) as enrollment_count
                FROM sunrise.student_transport_enrollment ste
                LEFT JOIN sunrise.transport_types tt ON ste.transport_type_id = tt.id
                WHERE ste.session_year_id = :session_year_id
                    AND ste.is_active = TRUE
                GROUP BY tt.id, tt.name, tt.description
                ORDER BY enrollment_count DESC
            """)
            transport_type_result = await db.execute(
                transport_type_query,
                {"session_year_id": session_year_id}
            )
            transport_type_breakdown = [
                {
                    'name': row.transport_type_name or 'Not Specified',
                    'type': row.transport_type or 'Not Specified',
                    'count': row.enrollment_count
                }
                for row in transport_type_result
            ]

            # Get monthly transport fee collection trends
            transport_monthly_query = text("""
                SELECT
                    tmt.month_name,
                    tmt.academic_month,
                    COALESCE(SUM(tmt.paid_amount), 0) as collected_amount,
                    COALESCE(SUM(tmt.monthly_amount), 0) as total_amount
                FROM sunrise.transport_monthly_tracking tmt
                JOIN sunrise.student_transport_enrollment ste ON tmt.enrollment_id = ste.id
                WHERE tmt.session_year_id = :session_year_id
                    AND ste.is_active = TRUE
                GROUP BY tmt.month_name, tmt.academic_month
                ORDER BY tmt.academic_month
            """)
            transport_monthly_result = await db.execute(
                transport_monthly_query,
                {"session_year_id": session_year_id}
            )
            transport_monthly_trends = [
                {
                    'month': row.month_name,
                    'collected': float(row.collected_amount),
                    'total': float(row.total_amount)
                }
                for row in transport_monthly_result
            ]

            response_data['transport_service'] = {
                'students_using_transport': transport_stats.students_using_transport or 0,
                'pending_fees': float(transport_stats.pending_transport_fees or 0),
                'collected_fees': float(transport_stats.collected_transport_fees or 0),
                'transport_type_breakdown': transport_type_breakdown,
                'monthly_trends': transport_monthly_trends,
                'is_session_filtered': True
            }
        except Exception as e:
            logger.error(f"Error fetching transport statistics: {str(e)}")
            response_data['transport_service'] = {'error': str(e), 'is_session_filtered': True}

        logger.info("=== get_admin_dashboard_enhanced_stats completed successfully ===")
        return response_data

    except Exception as e:
        logger.error(f"Critical error in get_admin_dashboard_enhanced_stats: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch enhanced dashboard statistics: {str(e)}"
        )
