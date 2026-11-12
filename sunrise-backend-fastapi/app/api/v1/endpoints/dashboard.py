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
from app.crud import student_crud, teacher_crud
from app.crud.crud_expense import expense_crud
from app.crud.crud_leave import leave_request_crud
from app.crud.crud_inventory_stock import crud_inventory_stock
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.metadata import SessionYear
from app.models.expense import Expense as ExpenseModel
from app.modules.fees.constants import FeeHeadCategory
from app.modules.fees.service import summary as fee_summary_service
from app.modules.transport.service import summary as transport_summary_service
from app.models.student_session_history import StudentSessionHistory

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_session_year_details(
    db: AsyncSession,
    session_year_id: Optional[int] = None
) -> Tuple[int, str, Optional[date], Optional[date], bool]:
    """
    Get session year details from database.
    If session_year_id is None, fetches the current session (is_current=True).

    Returns: (session_year_id, session_year_name, start_date, end_date, is_current)
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
        return (session.id, session.name, session.start_date, session.end_date, session.is_current)

    # Unknown here: either no current session yet, or another school's session year
    raise HTTPException(status_code=404, detail="Session year not found")


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
    session_year_id, session_year_name, session_start_date, session_end_date, is_current_session = await get_session_year_details(
        db, session_year_id
    )

    logger.info(f"=== Starting get_admin_dashboard_stats ===")
    logger.info(f"Session: id={session_year_id}, name={session_year_name}, start={session_start_date}, end={session_end_date}, is_current={is_current_session}")

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

            # Check if this is the current session or a past session
            if is_current_session:
                # Current session: Query from students table directly
                logger.info(f"Querying current session students from students table")
                total_students_query = select(func.count(Student.id)).where(
                    and_(
                        Student.is_active == True,
                        or_(Student.is_deleted == False, Student.is_deleted.is_(None)),
                        Student.session_year_id == session_year_id
                    )
                )
                total_students_result = await db.execute(total_students_query)
                total_students = total_students_result.scalar() or 0

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
            else:
                # Past session: Query from BOTH student_session_history AND students table
                # to include students who were promoted AND students who were never promoted
                # NOTE: For historical sessions, we do NOT filter by is_deleted because:
                # - Students were part of that session when it was active
                # - They may have been deleted in a later session (e.g., left school)
                # - Historical data should reflect who was enrolled during that session
                logger.info(f"Querying past session students from student_session_history AND students table")

                # Count students from history (those who were promoted)
                # DO NOT filter by is_deleted - these students were part of the historical session
                history_students_query = select(
                    func.count(func.distinct(StudentSessionHistory.student_id))
                ).where(
                    StudentSessionHistory.session_year_id == session_year_id
                )
                history_students_result = await db.execute(history_students_query)
                history_students = history_students_result.scalar() or 0

                # Count students still in students table with this session (never promoted)
                # EXCLUDE students who are already in history to avoid double counting
                # DO NOT filter by is_deleted for historical sessions
                remaining_students_query = select(func.count(Student.id)).where(
                    and_(
                        Student.session_year_id == session_year_id,
                        # Exclude students already in history
                        ~Student.id.in_(
                            select(StudentSessionHistory.student_id).where(
                                StudentSessionHistory.session_year_id == session_year_id
                            )
                        )
                    )
                )
                remaining_students_result = await db.execute(remaining_students_query)
                remaining_students = remaining_students_result.scalar() or 0

                # Total = students in history + students still in that session (not in history)
                total_students = history_students + remaining_students

                logger.info(f"Past session breakdown: {history_students} from history + {remaining_students} remaining (not in history) = {total_students} total")

                # For past sessions, "added this month" doesn't make sense, so set to 0
                students_this_month = 0

            logger.info(f"Total students for session {session_year_name}: {total_students}")
            logger.info(f"Students added this month: {students_this_month}")

            response_data["students"] = {
                "total": total_students,
                "added_this_month": students_this_month,
                "change_text": f"+{students_this_month} this month" if is_current_session else "Historical data",
                "is_session_filtered": True,
                "is_historical": not is_current_session
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
            fee_summary = await fee_summary_service.session_summary(db, session_year_id)
            logger.info(f"Fee summary retrieved: {fee_summary}")

            # Get fees collected this week (net of reversals)
            logger.info("Calculating fees collected this week...")
            fees_collected_this_week = float(await fee_summary_service.collected(
                db, session_year_id=session_year_id, date_from=current_week_start
            ))
            logger.info(f"Fees collected this week: {fees_collected_this_week}")

            response_data["fees"] = {
                "pending_amount": float(fee_summary['pending']),
                "collected_this_week": fees_collected_this_week,
                "change_text": f"-₹{fees_collected_this_week:,.0f} this week",
                "total_collected": float(fee_summary['paid']),
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
                    FROM leave_requests
                    WHERE school_id = :school_id AND session_year_id = :session_year_id
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
            current_quarter_fees = float(await fee_summary_service.collected(
                db, session_year_id=session_year_id, date_from=current_quarter_start
            ))
            logger.info(f"Current quarter fees: {current_quarter_fees}")

            logger.info("Fetching last quarter fees...")
            last_quarter_fees = float(await fee_summary_service.collected(
                db, session_year_id=session_year_id,
                date_from=last_quarter_start, date_to=current_quarter_start - timedelta(days=1)
            ))
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
            from app.services.school_settings import shop_enabled

            # No School Shop, no stock to warn about
            low_stock_items = await crud_inventory_stock.get_low_stock_alerts(db) if await shop_enabled(db) else []
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
    session_year_id, session_year_name, session_start_date, session_end_date, is_current_session = await get_session_year_details(
        db, session_year_id
    )

    logger.info(f"=== Starting get_admin_dashboard_enhanced_stats ===")
    logger.info(f"Session: id={session_year_id}, name={session_year_name}, start={session_start_date}, end={session_end_date}, is_current={is_current_session}")

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
            if is_current_session:
                # Current session: Query from students table
                logger.info("Querying current session student details from students table")
                class_breakdown_query = text("""
                    SELECT
                        c.description as class_name,
                        COUNT(s.id) as total_students,
                        COUNT(CASE WHEN s.gender_id = 1 THEN 1 END) as male_count,
                        COUNT(CASE WHEN s.gender_id = 2 THEN 1 END) as female_count
                    FROM students s
                    LEFT JOIN classes c ON s.class_id = c.id
                    WHERE s.school_id = :school_id
                        AND s.is_active = TRUE
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
                student_stats_query = text("""
                    SELECT
                        COUNT(CASE WHEN is_active = TRUE THEN 1 END) as total_students,
                        COUNT(CASE WHEN is_active = TRUE THEN 1 END) as active_students,
                        COUNT(CASE WHEN is_active = FALSE THEN 1 END) as inactive_students,
                        COUNT(CASE WHEN is_active = TRUE AND created_at >= :month_start THEN 1 END) as recent_enrollments
                    FROM students
                    WHERE school_id = :school_id
                        AND (is_deleted = FALSE OR is_deleted IS NULL)
                        AND session_year_id = :session_year_id
                """)
                student_stats_result = await db.execute(
                    student_stats_query,
                    {"month_start": current_month_start, "session_year_id": session_year_id}
                )
                student_stats = student_stats_result.fetchone()
            else:
                # Past session: Query from BOTH student_session_history AND students table
                # to include students who were promoted AND students who were never promoted
                # NOTE: For historical sessions, we do NOT filter by is_deleted because:
                # - Students were part of that session when it was active
                # - They may have been deleted in a later session (e.g., left school)
                # - Historical data should reflect who was enrolled during that session
                logger.info("Querying past session student details from student_session_history AND students table")

                # Class breakdown using UNION ALL to combine history + remaining students
                # DO NOT filter by is_deleted for historical sessions
                class_breakdown_query = text("""
                    SELECT
                        class_name,
                        SUM(total_students) as total_students,
                        SUM(male_count) as male_count,
                        SUM(female_count) as female_count
                    FROM (
                        -- Students from history (promoted) - no is_deleted filter for historical data
                        SELECT
                            c.description as class_name,
                            COUNT(DISTINCT ssh.student_id) as total_students,
                            COUNT(DISTINCT CASE WHEN s.gender_id = 1 THEN ssh.student_id END) as male_count,
                            COUNT(DISTINCT CASE WHEN s.gender_id = 2 THEN ssh.student_id END) as female_count
                        FROM student_session_history ssh
                        LEFT JOIN classes c ON ssh.class_id = c.id
                        LEFT JOIN students s ON ssh.student_id = s.id
                        WHERE ssh.school_id = :school_id AND ssh.session_year_id = :session_year_id
                        GROUP BY c.id, c.description

                        UNION ALL

                        -- Students still in students table (not promoted) - no is_deleted filter for historical data
                        SELECT
                            c.description as class_name,
                            COUNT(s.id) as total_students,
                            COUNT(CASE WHEN s.gender_id = 1 THEN 1 END) as male_count,
                            COUNT(CASE WHEN s.gender_id = 2 THEN 1 END) as female_count
                        FROM students s
                        LEFT JOIN classes c ON s.class_id = c.id
                        WHERE s.school_id = :school_id AND s.session_year_id = :session_year_id
                            AND s.id NOT IN (
                                SELECT student_id
                                FROM student_session_history
                                WHERE school_id = :school_id AND session_year_id = :session_year_id
                            )
                        GROUP BY c.id, c.description
                    ) combined
                    GROUP BY class_name
                    ORDER BY class_name
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

                # Total student count: history + remaining students (no is_deleted filter for historical)
                # For historical sessions: all students were "active" during that session
                # Active/Inactive doesn't make sense for past sessions, so we set:
                # - active_students = total_students (all were active during that session)
                # - inactive_students = 0
                student_stats_query = text("""
                    SELECT
                        (
                            -- Count from history (no is_deleted filter for historical data)
                            SELECT COUNT(DISTINCT ssh.student_id)
                            FROM student_session_history ssh
                            WHERE ssh.school_id = :school_id AND ssh.session_year_id = :session_year_id
                        ) + (
                            -- Count from students table (exclude students already in history)
                            SELECT COUNT(s.id)
                            FROM students s
                            WHERE s.school_id = :school_id AND s.session_year_id = :session_year_id
                                AND s.id NOT IN (
                                    SELECT student_id
                                    FROM student_session_history
                                    WHERE school_id = :school_id AND session_year_id = :session_year_id
                                )
                        ) as total_students
                """)
                student_stats_result = await db.execute(
                    student_stats_query,
                    {"session_year_id": session_year_id}
                )
                total_students_row = student_stats_result.fetchone()
                total_students_count = total_students_row.total_students if total_students_row else 0

                # Create a named tuple-like object for consistency with the current session branch
                class StudentStatsResult:
                    def __init__(self, total, active, inactive, recent):
                        self.total_students = total
                        self.active_students = active
                        self.inactive_students = inactive
                        self.recent_enrollments = recent

                # For historical sessions: all were active, none inactive
                student_stats = StudentStatsResult(
                    total=total_students_count,
                    active=total_students_count,  # All were active during that session
                    inactive=0,  # No inactive for historical
                    recent=0
                )

            response_data['student_management'] = {
                'total_students': student_stats.total_students,
                'active_students': student_stats.active_students,
                'inactive_students': student_stats.inactive_students,
                'recent_enrollments': student_stats.recent_enrollments,
                'class_breakdown': class_breakdown,
                'is_session_filtered': True,
                'is_historical': not is_current_session
            }
        except Exception as e:
            logger.error(f"Error fetching student statistics: {str(e)}")
            response_data['student_management'] = {'error': str(e), 'is_session_filtered': True}

        # 2. Fee Management - Detailed Statistics (SESSION FILTERED 📅)
        try:
            fee_summary = await fee_summary_service.session_summary(db, session_year_id)

            # Collections per calendar month of payment, oldest first (April to March for an April session)
            monthly_trends = [
                {'month': row['month'], 'amount': float(row['amount']), 'count': row['count']}
                for row in await fee_summary_service.monthly_collections(db, session_year_id)
            ]

            response_data['fee_management'] = {
                'total_collected': float(fee_summary['paid']),
                'pending_fees': float(fee_summary['pending']),
                'collection_rate': float(fee_summary['collection_rate']),
                'total_records': fee_summary['students'],
                'paid_records': fee_summary['students_paid'],
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
                    FROM leave_requests
                    WHERE school_id = :school_id AND session_year_id = :session_year_id
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
                    FROM leave_requests lr
                    LEFT JOIN leave_types lt ON lr.leave_type_id = lt.id
                    WHERE lr.school_id = :school_id AND lr.session_year_id = :session_year_id
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
                    FROM leave_requests lr
                    LEFT JOIN leave_types lt ON lr.leave_type_id = lt.id
                    WHERE lr.school_id = :school_id
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
                    FROM expenses
                    WHERE school_id = :school_id AND session_year_id = :session_year_id
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
                    FROM expenses e
                    LEFT JOIN expense_categories ec ON e.expense_category_id = ec.id
                    WHERE e.school_id = :school_id AND e.session_year_id = :session_year_id
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
                    FROM expenses e
                    WHERE e.school_id = :school_id AND e.session_year_id = :session_year_id
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
                    FROM expenses e
                    WHERE e.school_id = :school_id AND e.expense_date >= :start_date
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
            transport = await transport_summary_service.session_summary(db, session_year_id)
            transport_fees = await fee_summary_service.session_summary(
                db, session_year_id, head_category=FeeHeadCategory.TRANSPORT.value
            )
            transport_type_breakdown = [
                {'name': t['name'], 'type': t['description'], 'count': t['riders']}
                for t in transport['by_type']
            ]
            transport_monthly_trends = [
                {'month': row['month'], 'collected': float(row['collected']), 'total': float(row['total'])}
                for row in await fee_summary_service.monthly_dues(
                    db, session_year_id, head_category=FeeHeadCategory.TRANSPORT.value
                )
            ]

            collected_fees = float(transport_fees['paid'])
            pending_fees = float(transport_fees['pending'])
            total_fees = collected_fees + pending_fees
            collection_percentage = (collected_fees / total_fees * 100) if total_fees > 0 else 0

            response_data['transport_service'] = {
                'students_using_transport': transport['students_riding'],
                'total_enrollments': transport['total_assignments'],
                'pending_fees': pending_fees,
                'collected_fees': collected_fees,
                'total_fees': total_fees,
                'collection_percentage': round(collection_percentage, 2),
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
