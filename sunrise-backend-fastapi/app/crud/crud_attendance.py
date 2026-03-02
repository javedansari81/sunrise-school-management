from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_, or_, func, desc, text
from datetime import date, datetime

from app.crud.base import CRUDBase
from app.models.attendance import AttendanceRecord, AttendanceStatus, AttendancePeriod
from app.models.student import Student
from app.models.user import User
from app.models.metadata import Class, SessionYear
from app.schemas.attendance import (
    AttendanceRecordCreate, AttendanceRecordUpdate, AttendanceFilters,
    BulkAttendanceCreate
)


class CRUDAttendanceRecord(CRUDBase[AttendanceRecord, AttendanceRecordCreate, AttendanceRecordUpdate]):
    """
    CRUD operations for Attendance Records with metadata-driven architecture
    
    Features:
    - Daily attendance tracking with full audit trail
    - Bulk attendance marking for entire classes
    - Flexible filtering by date, class, student, status
    - Student attendance summaries and statistics
    - Integration with leave management system
    """

    async def create(self, db: AsyncSession, *, obj_in: dict, marked_by: int) -> AttendanceRecord:
        """Create a new attendance record"""
        obj_in['marked_by'] = marked_by
        
        db_obj = AttendanceRecord(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        return db_obj

    async def create_bulk(
        self,
        db: AsyncSession,
        *,
        bulk_data: BulkAttendanceCreate,
        marked_by: int
    ) -> Dict[str, Any]:
        """Create multiple attendance records at once"""
        created_count = 0
        updated_count = 0
        errors = []
        
        for item in bulk_data.records:
            try:
                # Check if record already exists
                existing_query = select(AttendanceRecord).where(
                    and_(
                        AttendanceRecord.student_id == item.student_id,
                        AttendanceRecord.attendance_date == bulk_data.attendance_date,
                        AttendanceRecord.attendance_period_id == bulk_data.attendance_period_id
                    )
                )
                result = await db.execute(existing_query)
                existing_record = result.scalar_one_or_none()
                
                if existing_record:
                    # Update existing record
                    existing_record.attendance_status_id = item.attendance_status_id
                    existing_record.check_in_time = item.check_in_time
                    existing_record.remarks = item.remarks
                    existing_record.marked_by = marked_by
                    existing_record.updated_at = datetime.utcnow()
                    updated_count += 1
                else:
                    # Create new record
                    new_record = AttendanceRecord(
                        student_id=item.student_id,
                        class_id=bulk_data.class_id,
                        session_year_id=bulk_data.session_year_id,
                        attendance_date=bulk_data.attendance_date,
                        attendance_status_id=item.attendance_status_id,
                        attendance_period_id=bulk_data.attendance_period_id,
                        check_in_time=item.check_in_time,
                        remarks=item.remarks,
                        marked_by=marked_by
                    )
                    db.add(new_record)
                    created_count += 1
                    
            except Exception as e:
                errors.append({
                    "student_id": item.student_id,
                    "error": str(e)
                })
        
        await db.commit()
        
        return {
            "created": created_count,
            "updated": updated_count,
            "errors": errors,
            "total_processed": created_count + updated_count
        }

    async def get_with_details(self, db: AsyncSession, id: int) -> Optional[Dict[str, Any]]:
        """Get attendance record with all related details"""
        query = """
        SELECT
            ar.*,
            s.first_name || ' ' || s.last_name as student_name,
            s.roll_number as student_roll_number,
            c.description as class_name,
            ast.name as attendance_status_name,
            ast.description as attendance_status_description,
            ast.color_code as attendance_status_color,
            ap.name as attendance_period_name,
            ap.description as attendance_period_description,
            u.first_name || ' ' || u.last_name as marked_by_name,
            sy.name as session_year_name
        FROM attendance_records ar
        LEFT JOIN students s ON ar.student_id = s.id
        LEFT JOIN classes c ON ar.class_id = c.id
        LEFT JOIN attendance_statuses ast ON ar.attendance_status_id = ast.id
        LEFT JOIN attendance_periods ap ON ar.attendance_period_id = ap.id
        LEFT JOIN users u ON ar.marked_by = u.id
        LEFT JOIN session_years sy ON ar.session_year_id = sy.id
        WHERE ar.id = :record_id
        """
        
        result = await db.execute(text(query), {"record_id": id})
        row = result.fetchone()
        
        if not row:
            return None

        return dict(row._mapping)

    async def get_multi_with_filters(
        self,
        db: AsyncSession,
        *,
        filters: AttendanceFilters,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get attendance records with filters and pagination"""

        # Build WHERE conditions
        where_conditions = []
        params = {}

        if filters.student_id:
            where_conditions.append("ar.student_id = :student_id")
            params["student_id"] = filters.student_id

        if filters.class_id:
            where_conditions.append("ar.class_id = :class_id")
            params["class_id"] = filters.class_id

        if filters.attendance_date:
            where_conditions.append("ar.attendance_date = :attendance_date")
            params["attendance_date"] = filters.attendance_date

        if filters.from_date:
            where_conditions.append("ar.attendance_date >= :from_date")
            params["from_date"] = filters.from_date

        if filters.to_date:
            where_conditions.append("ar.attendance_date <= :to_date")
            params["to_date"] = filters.to_date

        if filters.attendance_status_id:
            where_conditions.append("ar.attendance_status_id = :status_id")
            params["status_id"] = filters.attendance_status_id

        if filters.session_year_id:
            where_conditions.append("ar.session_year_id = :session_year_id")
            params["session_year_id"] = filters.session_year_id

        if filters.search:
            where_conditions.append(
                "(s.first_name ILIKE :search OR s.last_name ILIKE :search OR s.roll_number ILIKE :search)"
            )
            params["search"] = f"%{filters.search}%"

        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

        # Main query with joins
        query = f"""
        SELECT
            ar.id,
            ar.student_id,
            ar.class_id,
            ar.session_year_id,
            ar.attendance_date,
            ar.attendance_status_id,
            ar.attendance_period_id,
            ar.check_in_time,
            ar.check_out_time,
            ar.remarks,
            ar.marked_by,
            ar.leave_request_id,
            ar.created_at,
            ar.updated_at,
            s.first_name || ' ' || s.last_name as student_name,
            s.roll_number as student_roll_number,
            c.description as class_name,
            ast.name as attendance_status_name,
            ast.description as attendance_status_description,
            ast.color_code as attendance_status_color,
            ap.description as attendance_period_name,
            u.first_name || ' ' || u.last_name as marked_by_name
        FROM attendance_records ar
        LEFT JOIN students s ON ar.student_id = s.id
        LEFT JOIN classes c ON ar.class_id = c.id
        LEFT JOIN attendance_statuses ast ON ar.attendance_status_id = ast.id
        LEFT JOIN attendance_periods ap ON ar.attendance_period_id = ap.id
        LEFT JOIN users u ON ar.marked_by = u.id
        WHERE {where_clause}
        ORDER BY ar.attendance_date DESC, s.roll_number ASC
        LIMIT :limit OFFSET :skip
        """

        params["limit"] = limit
        params["skip"] = skip

        result = await db.execute(text(query), params)
        records = [dict(row._mapping) for row in result.fetchall()]

        # Count query
        count_query = f"""
        SELECT COUNT(*) as total
        FROM attendance_records ar
        LEFT JOIN students s ON ar.student_id = s.id
        WHERE {where_clause}
        """

        count_result = await db.execute(text(count_query), params)
        total = count_result.scalar()

        return records, total

    async def get_student_summary(
        self,
        db: AsyncSession,
        *,
        student_id: int,
        session_year_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Optional[Dict[str, Any]]:
        """Get attendance summary for a student"""

        where_conditions = [
            "ar.student_id = :student_id",
            "ar.session_year_id = :session_year_id"
        ]
        params = {
            "student_id": student_id,
            "session_year_id": session_year_id
        }

        if from_date:
            where_conditions.append("ar.attendance_date >= :from_date")
            params["from_date"] = from_date

        if to_date:
            where_conditions.append("ar.attendance_date <= :to_date")
            params["to_date"] = to_date

        where_clause = " AND ".join(where_conditions)

        query = f"""
        SELECT
            ar.student_id,
            s.first_name || ' ' || s.last_name as student_name,
            s.roll_number as student_roll_number,
            c.description as class_name,
            sy.name as session_year,
            COUNT(*) as total_school_days,
            COUNT(CASE WHEN ast.name = 'PRESENT' THEN 1 END) as days_present,
            COUNT(CASE WHEN ast.name = 'ABSENT' THEN 1 END) as days_absent,
            COUNT(CASE WHEN ast.name = 'LATE' THEN 1 END) as days_late,
            COUNT(CASE WHEN ast.name = 'HALF_DAY' THEN 1 END) as days_half_day,
            COUNT(CASE WHEN ast.name = 'EXCUSED' OR ast.name = 'LEAVE' THEN 1 END) as days_excused,
            ROUND(
                (COUNT(CASE WHEN ast.name = 'PRESENT' THEN 1 END) * 100.0 /
                NULLIF(COUNT(CASE WHEN ast.affects_attendance_percentage = TRUE THEN 1 END), 0)), 2
            ) as attendance_percentage,
            MIN(ar.attendance_date) as from_date,
            MAX(ar.attendance_date) as to_date
        FROM attendance_records ar
        LEFT JOIN students s ON ar.student_id = s.id
        LEFT JOIN classes c ON s.class_id = c.id
        LEFT JOIN session_years sy ON ar.session_year_id = sy.id
        LEFT JOIN attendance_statuses ast ON ar.attendance_status_id = ast.id
        WHERE {where_clause}
        GROUP BY ar.student_id, s.first_name, s.last_name, s.roll_number, c.description, sy.name
        """

        result = await db.execute(text(query), params)
        row = result.fetchone()

        if not row:
            return None

        return dict(row._mapping)

    async def get_class_attendance_by_date(
        self,
        db: AsyncSession,
        *,
        class_id: int,
        attendance_date: date,
        session_year_id: int
    ) -> List[Dict[str, Any]]:
        """Get attendance for entire class on specific date"""

        query = """
        SELECT
            s.id as student_id,
            s.first_name || ' ' || s.last_name as student_name,
            s.roll_number as student_roll_number,
            ar.id as attendance_record_id,
            ar.attendance_status_id,
            ast.description as attendance_status_description,
            ast.color_code as attendance_status_color,
            ar.check_in_time,
            ar.remarks
        FROM students s
        LEFT JOIN attendance_records ar ON s.id = ar.student_id
            AND ar.attendance_date = :attendance_date
            AND ar.session_year_id = :session_year_id
        LEFT JOIN attendance_statuses ast ON ar.attendance_status_id = ast.id
        WHERE s.class_id = :class_id
            AND s.session_year_id = :session_year_id
            AND s.is_active = TRUE
            AND (s.is_deleted = FALSE OR s.is_deleted IS NULL)
        ORDER BY s.roll_number ASC
        """

        result = await db.execute(text(query), {
            "class_id": class_id,
            "attendance_date": attendance_date,
            "session_year_id": session_year_id
        })

        return [dict(row._mapping) for row in result.fetchall()]

    async def get_attendance_statistics(
        self,
        db: AsyncSession,
        *,
        filters: AttendanceFilters
    ) -> Dict[str, Any]:
        """Get attendance statistics based on filters"""

        where_conditions = []
        params = {}

        if filters.class_id:
            where_conditions.append("ar.class_id = :class_id")
            params["class_id"] = filters.class_id

        if filters.from_date:
            where_conditions.append("ar.attendance_date >= :from_date")
            params["from_date"] = filters.from_date

        if filters.to_date:
            where_conditions.append("ar.attendance_date <= :to_date")
            params["to_date"] = filters.to_date

        if filters.session_year_id:
            where_conditions.append("ar.session_year_id = :session_year_id")
            params["session_year_id"] = filters.session_year_id

        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

        query = f"""
        SELECT
            COUNT(*) as total_records,
            COUNT(CASE WHEN ast.name = 'PRESENT' THEN 1 END) as total_present,
            COUNT(CASE WHEN ast.name = 'ABSENT' THEN 1 END) as total_absent,
            COUNT(CASE WHEN ast.name = 'LATE' THEN 1 END) as total_late,
            COALESCE(
                ROUND(
                    (COUNT(CASE WHEN ast.name = 'PRESENT' THEN 1 END) * 100.0 /
                    NULLIF(COUNT(CASE WHEN ast.affects_attendance_percentage = TRUE THEN 1 END), 0)), 2
                ),
                0.0
            ) as overall_attendance_percentage
        FROM attendance_records ar
        LEFT JOIN attendance_statuses ast ON ar.attendance_status_id = ast.id
        WHERE {where_clause}
        """

        result = await db.execute(text(query), params)
        row = result.fetchone()

        if not row:
            return {
                "total_records": 0,
                "total_present": 0,
                "total_absent": 0,
                "total_late": 0,
                "overall_attendance_percentage": 0.0
            }

        # Convert row to dict and ensure proper handling of None/NULL values
        stats = dict(row._mapping)
        return {
            "total_records": stats.get("total_records") or 0,
            "total_present": stats.get("total_present") or 0,
            "total_absent": stats.get("total_absent") or 0,
            "total_late": stats.get("total_late") or 0,
            "overall_attendance_percentage": float(stats.get("overall_attendance_percentage") or 0.0)
        }

    async def get_consecutive_absences(
        self,
        db: AsyncSession,
        *,
        session_year_id: int,
        min_absent_days: int = 3,
        class_id: Optional[int] = None,
        as_of_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Find students who have been absent for consecutive days without approved leave.

        This query:
        1. Looks at attendance records up to as_of_date (defaults to today)
        2. Finds students marked ABSENT for min_absent_days or more consecutive days
        3. Excludes students who have approved leave requests covering those dates
        4. Returns student details with parent contact information
        """
        from datetime import date as date_type

        if as_of_date is None:
            as_of_date = date_type.today()

        # Build optional class filter
        class_filter = ""
        params = {
            "session_year_id": session_year_id,
            "min_days": min_absent_days,
            "as_of_date": as_of_date,
            "absent_status": "ABSENT"  # Attendance status name for absent
        }

        if class_id:
            class_filter = "AND s.class_id = :class_id"
            params["class_id"] = class_id

        # Query to find students with consecutive absences
        # Uses a window function to identify consecutive absence streaks
        query = f"""
        WITH recent_attendance AS (
            -- Get attendance records for the session, ordered by date desc
            SELECT
                ar.student_id,
                ar.attendance_date,
                ar.attendance_status_id,
                ast.name as status_name,
                ar.leave_request_id
            FROM attendance_records ar
            JOIN attendance_statuses ast ON ar.attendance_status_id = ast.id
            WHERE ar.session_year_id = :session_year_id
              AND ar.attendance_date <= :as_of_date
        ),
        consecutive_absences AS (
            -- Find consecutive absent days for each student (from most recent)
            SELECT
                ra.student_id,
                MIN(ra.attendance_date) as absent_from_date,
                COUNT(*) as consecutive_days
            FROM (
                SELECT
                    student_id,
                    attendance_date,
                    status_name,
                    leave_request_id,
                    -- Create groups for consecutive dates
                    attendance_date - (ROW_NUMBER() OVER (
                        PARTITION BY student_id
                        ORDER BY attendance_date DESC
                    ))::int as grp
                FROM recent_attendance
                WHERE status_name = :absent_status
                  AND leave_request_id IS NULL  -- No leave linked
            ) ra
            -- Only consider the most recent consecutive group (grp with max date)
            WHERE ra.grp = (
                SELECT ra2.attendance_date - (ROW_NUMBER() OVER (
                    PARTITION BY ra2.student_id
                    ORDER BY ra2.attendance_date DESC
                ))::int
                FROM recent_attendance ra2
                WHERE ra2.student_id = ra.student_id
                  AND ra2.status_name = :absent_status
                  AND ra2.leave_request_id IS NULL
                ORDER BY ra2.attendance_date DESC
                LIMIT 1
            )
            GROUP BY ra.student_id, ra.grp
            HAVING COUNT(*) >= :min_days
        ),
        last_present AS (
            -- Find last present date for each student
            SELECT
                ra.student_id,
                MAX(ra.attendance_date) as last_present_date
            FROM recent_attendance ra
            WHERE ra.status_name = 'PRESENT'
            GROUP BY ra.student_id
        ),
        pending_leaves AS (
            -- Check for pending leave requests
            SELECT DISTINCT
                lr.applicant_id as student_id,
                TRUE as has_pending_leave
            FROM leave_requests lr
            JOIN leave_statuses ls ON lr.leave_status_id = ls.id
            WHERE lr.applicant_type = 'student'
              AND ls.name = 'Pending'
              AND lr.start_date <= :as_of_date
              AND lr.end_date >= :as_of_date
        )
        SELECT
            s.id as student_id,
            s.first_name || ' ' || s.last_name as student_name,
            s.roll_number,
            s.class_id,
            c.description as class_name,
            s.section,
            ca.consecutive_days as consecutive_absent_days,
            ca.absent_from_date,
            lp.last_present_date,
            s.father_name,
            s.father_phone,
            s.mother_name,
            s.mother_phone,
            s.guardian_name,
            s.guardian_phone,
            COALESCE(pl.has_pending_leave, FALSE) as has_pending_leave
        FROM consecutive_absences ca
        JOIN students s ON ca.student_id = s.id
        JOIN classes c ON s.class_id = c.id
        LEFT JOIN last_present lp ON s.id = lp.student_id
        LEFT JOIN pending_leaves pl ON s.id = pl.student_id
        WHERE s.is_active = TRUE
          AND (s.is_deleted IS NULL OR s.is_deleted = FALSE)
          {class_filter}
        ORDER BY c.id, ca.consecutive_days DESC, s.roll_number
        """

        result = await db.execute(text(query), params)
        rows = result.fetchall()

        return [dict(row._mapping) for row in rows]


# Create singleton instance
attendance_record_crud = CRUDAttendanceRecord(AttendanceRecord)

