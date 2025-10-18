from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_, or_, func, desc, extract, text
from datetime import date, datetime

from app.crud.base import CRUDBase
from app.models.leave import LeaveRequest, LeaveBalance, LeavePolicy, LeaveApprover
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.user import User
from app.models.metadata import LeaveType, LeaveStatus
from app.schemas.leave import (
    LeaveRequestCreate, LeaveRequestUpdate, LeaveFilters,
    ApplicantTypeEnum, LeaveRequestWithDetails
)


class CRUDLeaveRequest(CRUDBase[LeaveRequest, LeaveRequestCreate, LeaveRequestUpdate]):
    """CRUD operations for Leave Requests with metadata-driven architecture"""

    async def create(self, db: AsyncSession, *, obj_in: dict) -> LeaveRequest:
        """Create a new leave request with automatic total days calculation"""
        # Calculate total days if not provided
        if not obj_in.get('total_days'):
            total_days = (obj_in['end_date'] - obj_in['start_date']).days + 1
            obj_in['total_days'] = total_days

        # Set default status to Pending (ID = 1) if not provided
        if 'leave_status_id' not in obj_in:
            obj_in['leave_status_id'] = 1

        db_obj = LeaveRequest(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        return db_obj

    async def get_with_details(self, db: AsyncSession, id: int) -> Optional[LeaveRequestWithDetails]:
        """Get leave request with all related details"""
        query = """
        SELECT
            lr.*,
            COALESCE(
                CASE
                    WHEN lr.applicant_type = 'student' AND s.id IS NOT NULL THEN
                        'Roll ' || LPAD(COALESCE(s.roll_number::text, '000'), 3, '0') || ': ' || s.first_name || ' ' || s.last_name
                    WHEN lr.applicant_type = 'teacher' AND t.id IS NOT NULL THEN
                        t.first_name || ' ' || t.last_name || ' (' || t.employee_id || ')'
                    ELSE 'Unknown Applicant (ID: ' || lr.applicant_id || ')'
                END
            ) as applicant_name,
            COALESCE(
                CASE
                    WHEN lr.applicant_type = 'student' AND c.id IS NOT NULL THEN c.name
                    WHEN lr.applicant_type = 'teacher' AND t.id IS NOT NULL THEN d.description
                    ELSE 'N/A'
                END,
                'N/A'
            ) as applicant_details,
            COALESCE(lt.name, 'Unknown Leave Type') as leave_type_name,
            COALESCE(ls.name, 'Unknown Status') as leave_status_name,
            ls.color_code as leave_status_color,
            CASE
                WHEN u.id IS NOT NULL THEN u.first_name || ' ' || u.last_name
                ELSE NULL
            END as reviewer_name
        FROM leave_requests lr
        LEFT JOIN students s ON lr.applicant_type = 'student' AND lr.applicant_id = s.id
        LEFT JOIN classes c ON lr.applicant_type = 'student' AND s.class_id = c.id
        LEFT JOIN teachers t ON lr.applicant_type = 'teacher' AND lr.applicant_id = t.id
        LEFT JOIN departments d ON t.department_id = d.id
        LEFT JOIN leave_types lt ON lr.leave_type_id = lt.id
        LEFT JOIN leave_statuses ls ON lr.leave_status_id = ls.id
        LEFT JOIN users u ON lr.approved_by = u.id
        WHERE lr.id = :leave_id
        """

        result = await db.execute(text(query), {"leave_id": id})
        row = result.fetchone()

        if not row:
            return None

        # Convert row to dictionary using _asdict() if available, otherwise manual conversion
        try:
            if hasattr(row, '_asdict'):
                row_dict = row._asdict()
            else:
                # Manual conversion for raw SQL results
                row_dict = dict(zip(result.keys(), row))

            return LeaveRequestWithDetails(**row_dict)
        except Exception as e:
            print(f"Error converting row to LeaveRequestWithDetails: {e}")
            print(f"Row data: {row}")
            print(f"Row type: {type(row)}")
            return None

    async def get_multi_with_filters(
        self,
        db: AsyncSession,
        *,
        filters: LeaveFilters,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[LeaveRequestWithDetails], int]:
        """Get leave requests with filters and pagination"""

        # Build WHERE conditions
        where_conditions = []
        params = {}

        if filters.applicant_id:
            where_conditions.append("lr.applicant_id = :applicant_id")
            params["applicant_id"] = filters.applicant_id

        if filters.applicant_type:
            where_conditions.append("lr.applicant_type = :applicant_type")
            params["applicant_type"] = filters.applicant_type.value

        if filters.leave_type_id:
            where_conditions.append("lr.leave_type_id = :leave_type_id")
            params["leave_type_id"] = filters.leave_type_id

        if filters.leave_status_id:
            where_conditions.append("lr.leave_status_id = :leave_status_id")
            params["leave_status_id"] = filters.leave_status_id

        if filters.from_date:
            where_conditions.append("lr.start_date >= :from_date")
            params["from_date"] = filters.from_date

        if filters.to_date:
            where_conditions.append("lr.end_date <= :to_date")
            params["to_date"] = filters.to_date

        if filters.class_id:
            where_conditions.append("c.id = :class_id")
            params["class_id"] = filters.class_id

        if filters.department:
            where_conditions.append("d.description = :department")
            params["department"] = filters.department

        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

        # Count query
        count_query = f"""
        SELECT COUNT(DISTINCT lr.id)
        FROM leave_requests lr
        LEFT JOIN students s ON lr.applicant_type = 'student' AND lr.applicant_id = s.id
        LEFT JOIN classes c ON lr.applicant_type = 'student' AND s.class_id = c.id
        LEFT JOIN teachers t ON lr.applicant_type = 'teacher' AND lr.applicant_id = t.id
        LEFT JOIN departments d ON t.department_id = d.id
        {where_clause}
        """

        count_result = await db.execute(text(count_query), params)
        total = count_result.scalar()

        # Main query with details
        main_query = f"""
        SELECT
            lr.*,
            COALESCE(
                CASE
                    WHEN lr.applicant_type = 'student' AND s.id IS NOT NULL THEN
                        'Roll ' || LPAD(COALESCE(s.roll_number::text, '000'), 3, '0') || ': ' || s.first_name || ' ' || s.last_name
                    WHEN lr.applicant_type = 'teacher' AND t.id IS NOT NULL THEN
                        t.first_name || ' ' || t.last_name || ' (' || t.employee_id || ')'
                    ELSE 'Unknown Applicant (ID: ' || lr.applicant_id || ')'
                END
            ) as applicant_name,
            COALESCE(
                CASE
                    WHEN lr.applicant_type = 'student' AND c.id IS NOT NULL THEN c.name
                    WHEN lr.applicant_type = 'teacher' AND t.id IS NOT NULL THEN d.description
                    ELSE 'N/A'
                END,
                'N/A'
            ) as applicant_details,
            CASE
                WHEN lr.applicant_type = 'teacher' AND t.id IS NOT NULL THEN t.employee_id
                ELSE NULL
            END as applicant_employee_id,
            CASE
                WHEN lr.applicant_type = 'student' AND s.id IS NOT NULL THEN s.roll_number
                ELSE NULL
            END as applicant_roll_number,
            CASE
                WHEN lr.applicant_type = 'student' AND c.id IS NOT NULL THEN c.id
                ELSE NULL
            END as applicant_class_id,
            COALESCE(lt.name, 'Unknown Leave Type') as leave_type_name,
            COALESCE(ls.name, 'Unknown Status') as leave_status_name,
            ls.color_code as leave_status_color,
            CASE
                WHEN u.id IS NOT NULL THEN u.first_name || ' ' || u.last_name
                ELSE NULL
            END as reviewer_name
        FROM leave_requests lr
        LEFT JOIN students s ON lr.applicant_type = 'student' AND lr.applicant_id = s.id
        LEFT JOIN classes c ON lr.applicant_type = 'student' AND s.class_id = c.id
        LEFT JOIN teachers t ON lr.applicant_type = 'teacher' AND lr.applicant_id = t.id
        LEFT JOIN departments d ON t.department_id = d.id
        LEFT JOIN leave_types lt ON lr.leave_type_id = lt.id
        LEFT JOIN leave_statuses ls ON lr.leave_status_id = ls.id
        LEFT JOIN users u ON lr.approved_by = u.id
        {where_clause}
        ORDER BY lr.created_at DESC
        LIMIT :limit OFFSET :skip
        """

        params.update({"limit": limit, "skip": skip})
        result = await db.execute(text(main_query), params)
        rows = result.fetchall()

        leaves = []
        for row in rows:
            try:
                if hasattr(row, '_asdict'):
                    row_dict = row._asdict()
                else:
                    row_dict = dict(zip(result.keys(), row))
                leaves.append(LeaveRequestWithDetails(**row_dict))
            except Exception as e:
                print(f"Error converting row: {e}")
                continue

        return leaves, total

    async def get_by_applicant(
        self,
        db: AsyncSession,
        *,
        applicant_id: int,
        applicant_type: ApplicantTypeEnum,
        limit: int = 50
    ) -> List[LeaveRequestWithDetails]:
        """Get leave requests by applicant (student or teacher)"""
        query = """
        SELECT
            lr.*,
            COALESCE(
                CASE
                    WHEN lr.applicant_type = 'student' AND s.id IS NOT NULL THEN s.first_name || ' ' || s.last_name
                    WHEN lr.applicant_type = 'teacher' AND t.id IS NOT NULL THEN t.first_name || ' ' || t.last_name
                    ELSE 'Unknown Applicant (ID: ' || lr.applicant_id || ')'
                END
            ) as applicant_name,
            COALESCE(
                CASE
                    WHEN lr.applicant_type = 'student' AND c.id IS NOT NULL THEN c.name
                    WHEN lr.applicant_type = 'teacher' AND t.id IS NOT NULL THEN d.description
                    ELSE 'N/A'
                END,
                'N/A'
            ) as applicant_details,
            CASE
                WHEN lr.applicant_type = 'teacher' AND t.id IS NOT NULL THEN t.employee_id
                ELSE NULL
            END as applicant_employee_id,
            CASE
                WHEN lr.applicant_type = 'student' AND s.id IS NOT NULL THEN s.roll_number
                ELSE NULL
            END as applicant_roll_number,
            CASE
                WHEN lr.applicant_type = 'student' AND c.id IS NOT NULL THEN c.id
                ELSE NULL
            END as applicant_class_id,
            COALESCE(lt.name, 'Unknown Leave Type') as leave_type_name,
            COALESCE(ls.name, 'Unknown Status') as leave_status_name,
            ls.color_code as leave_status_color,
            CASE
                WHEN u.id IS NOT NULL THEN u.first_name || ' ' || u.last_name
                ELSE NULL
            END as reviewer_name
        FROM leave_requests lr
        LEFT JOIN students s ON lr.applicant_type = 'student' AND lr.applicant_id = s.id
        LEFT JOIN classes c ON lr.applicant_type = 'student' AND s.class_id = c.id
        LEFT JOIN teachers t ON lr.applicant_type = 'teacher' AND lr.applicant_id = t.id
        LEFT JOIN departments d ON t.department_id = d.id
        LEFT JOIN leave_types lt ON lr.leave_type_id = lt.id
        LEFT JOIN leave_statuses ls ON lr.leave_status_id = ls.id
        LEFT JOIN users u ON lr.approved_by = u.id
        WHERE lr.applicant_id = :applicant_id AND lr.applicant_type = :applicant_type
        ORDER BY lr.created_at DESC
        LIMIT :limit
        """

        result = await db.execute(text(query), {
            "applicant_id": applicant_id,
            "applicant_type": applicant_type.value,
            "limit": limit
        })
        rows = result.fetchall()

        leaves = []
        for row in rows:
            try:
                if hasattr(row, '_asdict'):
                    row_dict = row._asdict()
                else:
                    row_dict = dict(zip(result.keys(), row))
                leaves.append(LeaveRequestWithDetails(**row_dict))
            except Exception as e:
                print(f"Error converting row: {e}")
                continue
        return leaves

    async def get_pending_requests(self, db: AsyncSession) -> List[LeaveRequestWithDetails]:
        """Get all pending leave requests"""
        query = """
        SELECT
            lr.*,
            COALESCE(
                CASE
                    WHEN lr.applicant_type = 'student' AND s.id IS NOT NULL THEN
                        'Roll ' || LPAD(COALESCE(s.roll_number::text, '000'), 3, '0') || ': ' || s.first_name || ' ' || s.last_name
                    WHEN lr.applicant_type = 'teacher' AND t.id IS NOT NULL THEN
                        t.first_name || ' ' || t.last_name || ' (' || t.employee_id || ')'
                    ELSE 'Unknown Applicant (ID: ' || lr.applicant_id || ')'
                END
            ) as applicant_name,
            COALESCE(
                CASE
                    WHEN lr.applicant_type = 'student' AND c.id IS NOT NULL THEN c.name
                    WHEN lr.applicant_type = 'teacher' AND t.id IS NOT NULL THEN d.description
                    ELSE 'N/A'
                END,
                'N/A'
            ) as applicant_details,
            COALESCE(lt.name, 'Unknown Leave Type') as leave_type_name,
            COALESCE(ls.name, 'Unknown Status') as leave_status_name,
            ls.color_code as leave_status_color,
            CASE
                WHEN u.id IS NOT NULL THEN u.first_name || ' ' || u.last_name
                ELSE NULL
            END as reviewer_name
        FROM leave_requests lr
        LEFT JOIN students s ON lr.applicant_type = 'student' AND lr.applicant_id = s.id
        LEFT JOIN classes c ON lr.applicant_type = 'student' AND s.class_id = c.id
        LEFT JOIN teachers t ON lr.applicant_type = 'teacher' AND lr.applicant_id = t.id
        LEFT JOIN departments d ON t.department_id = d.id
        LEFT JOIN leave_types lt ON lr.leave_type_id = lt.id
        LEFT JOIN leave_statuses ls ON lr.leave_status_id = ls.id
        LEFT JOIN users u ON lr.approved_by = u.id
        WHERE lr.leave_status_id = 1
        ORDER BY lr.created_at ASC
        """

        result = await db.execute(text(query))
        rows = result.fetchall()

        leaves = []
        for row in rows:
            try:
                if hasattr(row, '_asdict'):
                    row_dict = row._asdict()
                else:
                    row_dict = dict(zip(result.keys(), row))
                leaves.append(LeaveRequestWithDetails(**row_dict))
            except Exception as e:
                print(f"Error converting row: {e}")
                continue
        return leaves

    async def get_student_leaves_by_class_teacher(
        self,
        db: AsyncSession,
        *,
        teacher_id: int,
        leave_status_id: Optional[int] = None,
        leave_type_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[LeaveRequestWithDetails], int]:
        """
        Get student leave requests for a class teacher's assigned class
        Only returns leaves from students in the class where teacher is class teacher
        """
        # Build WHERE conditions
        where_conditions = [
            "lr.applicant_type = 'student'",
            "ct.id = :teacher_id",
            "ct.class_teacher_of_id IS NOT NULL",
            "s.class_id = ct.class_teacher_of_id"
        ]
        params = {"teacher_id": teacher_id}

        if leave_status_id:
            where_conditions.append("lr.leave_status_id = :leave_status_id")
            params["leave_status_id"] = leave_status_id

        if leave_type_id:
            where_conditions.append("lr.leave_type_id = :leave_type_id")
            params["leave_type_id"] = leave_type_id

        where_clause = "WHERE " + " AND ".join(where_conditions)

        # Count query
        count_query = f"""
        SELECT COUNT(DISTINCT lr.id)
        FROM leave_requests lr
        INNER JOIN students s ON lr.applicant_type = 'student' AND lr.applicant_id = s.id
        INNER JOIN teachers ct ON ct.class_teacher_of_id = s.class_id
        {where_clause}
        """

        count_result = await db.execute(text(count_query), params)
        total = count_result.scalar()

        # Main query with details
        main_query = f"""
        SELECT
            lr.*,
            'Roll ' || LPAD(COALESCE(s.roll_number::text, '000'), 3, '0') || ': ' || s.first_name || ' ' || s.last_name as applicant_name,
            COALESCE(c.name, 'N/A') as applicant_details,
            s.roll_number as applicant_roll_number,
            c.id as applicant_class_id,
            COALESCE(lt.name, 'Unknown Leave Type') as leave_type_name,
            COALESCE(ls.name, 'Unknown Status') as leave_status_name,
            ls.color_code as leave_status_color,
            CASE
                WHEN u.id IS NOT NULL THEN u.first_name || ' ' || u.last_name
                ELSE NULL
            END as reviewer_name
        FROM leave_requests lr
        INNER JOIN students s ON lr.applicant_type = 'student' AND lr.applicant_id = s.id
        INNER JOIN classes c ON s.class_id = c.id
        INNER JOIN teachers ct ON ct.class_teacher_of_id = s.class_id
        LEFT JOIN leave_types lt ON lr.leave_type_id = lt.id
        LEFT JOIN leave_statuses ls ON lr.leave_status_id = ls.id
        LEFT JOIN users u ON lr.approved_by = u.id
        {where_clause}
        ORDER BY lr.created_at DESC
        LIMIT :limit OFFSET :skip
        """

        params.update({"limit": limit, "skip": skip})
        result = await db.execute(text(main_query), params)
        rows = result.fetchall()

        leaves = []
        for row in rows:
            try:
                if hasattr(row, '_asdict'):
                    row_dict = row._asdict()
                else:
                    row_dict = dict(zip(result.keys(), row))
                leaves.append(LeaveRequestWithDetails(**row_dict))
            except Exception as e:
                print(f"Error converting row: {e}")
                continue

        return leaves, total

    async def approve_request(
        self,
        db: AsyncSession,
        *,
        leave_request: LeaveRequest,
        reviewer_id: int,
        leave_status_id: int,
        review_comments: Optional[str] = None
    ) -> LeaveRequest:
        """Approve or reject a leave request"""
        leave_request.leave_status_id = leave_status_id
        leave_request.approved_by = reviewer_id
        leave_request.approved_at = datetime.utcnow()

        if review_comments:
            leave_request.approval_comments = review_comments

        db.add(leave_request)
        await db.commit()
        await db.refresh(leave_request)

        return leave_request

    async def get_leave_statistics(
        self, db: AsyncSession, *, year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get comprehensive leave statistics"""
        where_clause = f"WHERE EXTRACT(year FROM lr.start_date) = {year}" if year else ""

        query = f"""
        SELECT
            COUNT(lr.id) as total_requests,
            COUNT(CASE WHEN lr.leave_status_id = 2 THEN 1 END) as approved_requests,
            COUNT(CASE WHEN lr.leave_status_id = 3 THEN 1 END) as rejected_requests,
            COUNT(CASE WHEN lr.leave_status_id = 1 THEN 1 END) as pending_requests,
            SUM(lr.total_days) as total_days
        FROM sunrise.leave_requests lr
        {where_clause}
        """

        result = await db.execute(text(query))
        stats = result.fetchone()

        # Get leave type breakdown
        type_query = f"""
        SELECT
            lt.name as leave_type_name,
            COUNT(lr.id) as count
        FROM sunrise.leave_requests lr
        JOIN sunrise.leave_types lt ON lr.leave_type_id = lt.id
        {where_clause}
        GROUP BY lt.id, lt.name
        ORDER BY count DESC
        """

        type_result = await db.execute(text(type_query))
        type_breakdown = [
            {'leave_type': row.leave_type_name, 'count': row.count}
            for row in type_result
        ]

        # Get applicant type breakdown
        applicant_query = f"""
        SELECT
            lr.applicant_type,
            COUNT(lr.id) as count
        FROM sunrise.leave_requests lr
        {where_clause}
        GROUP BY lr.applicant_type
        """

        applicant_result = await db.execute(text(applicant_query))
        applicant_breakdown = [
            {'applicant_type': row.applicant_type, 'count': row.count}
            for row in applicant_result
        ]

        return {
            'total_requests': stats.total_requests or 0,
            'approved_requests': stats.approved_requests or 0,
            'rejected_requests': stats.rejected_requests or 0,
            'pending_requests': stats.pending_requests or 0,
            'total_days': stats.total_days or 0,
            'approval_rate': (stats.approved_requests / stats.total_requests * 100) if stats.total_requests else 0,
            'leave_type_breakdown': type_breakdown,
            'applicant_type_breakdown': applicant_breakdown
        }

    async def get_monthly_leave_trend(
        self, db: AsyncSession, *, year: int
    ) -> List[Dict[str, Any]]:
        """Get monthly leave trend for a specific year"""
        query = """
        SELECT
            EXTRACT(month FROM lr.start_date) as month,
            COUNT(lr.id) as count,
            SUM(lr.total_days) as total_days,
            COUNT(CASE WHEN lr.leave_status_id = 2 THEN 1 END) as approved_count,
            COUNT(CASE WHEN lr.leave_status_id = 3 THEN 1 END) as rejected_count,
            COUNT(CASE WHEN lr.leave_status_id = 1 THEN 1 END) as pending_count
        FROM leave_requests lr
        WHERE EXTRACT(year FROM lr.start_date) = :year
        GROUP BY EXTRACT(month FROM lr.start_date)
        ORDER BY EXTRACT(month FROM lr.start_date)
        """

        result = await db.execute(text(query), {"year": year})

        return [
            {
                'month': int(row.month),
                'count': row.count,
                'total_days': int(row.total_days or 0),
                'approved_count': row.approved_count,
                'rejected_count': row.rejected_count,
                'pending_count': row.pending_count
            }
            for row in result
        ]

    async def get_class_wise_leave_stats(
        self, db: AsyncSession, *, year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get class-wise leave statistics for students"""
        where_clause = "AND EXTRACT(year FROM lr.start_date) = :year" if year else ""
        params = {"year": year} if year else {}

        query = f"""
        SELECT
            COALESCE(c.name, 'N/A') as class_name,
            COUNT(lr.id) as total_requests,
            COUNT(CASE WHEN lr.leave_status_id = 2 THEN 1 END) as approved_requests,
            COUNT(CASE WHEN lr.leave_status_id = 3 THEN 1 END) as rejected_requests,
            COUNT(CASE WHEN lr.leave_status_id = 1 THEN 1 END) as pending_requests,
            SUM(lr.total_days) as total_days
        FROM leave_requests lr
        LEFT JOIN students s ON lr.applicant_type = 'student' AND lr.applicant_id = s.id
        LEFT JOIN classes c ON s.class_id = c.id
        WHERE lr.applicant_type = 'student' {where_clause}
        GROUP BY c.name
        ORDER BY c.name
        """

        result = await db.execute(text(query), params)

        return [
            {
                'class_name': row.class_name,
                'total_requests': row.total_requests,
                'approved_requests': row.approved_requests,
                'rejected_requests': row.rejected_requests,
                'pending_requests': row.pending_requests,
                'total_days': int(row.total_days or 0)
            }
            for row in result
        ]


class CRUDLeaveBalance(CRUDBase[LeaveBalance, dict, dict]):
    """CRUD operations for Leave Balance"""

    async def get_by_teacher_and_type(
        self,
        db: AsyncSession,
        *,
        teacher_id: int,
        leave_type_id: int,
        session_year_id: int
    ) -> Optional[LeaveBalance]:
        """Get leave balance for specific teacher, leave type, and session year"""
        result = await db.execute(
            select(LeaveBalance)
            .where(
                and_(
                    LeaveBalance.teacher_id == teacher_id,
                    LeaveBalance.leave_type_id == leave_type_id,
                    LeaveBalance.session_year_id == session_year_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_teacher(
        self,
        db: AsyncSession,
        *,
        teacher_id: int,
        session_year_id: int
    ) -> List[LeaveBalance]:
        """Get all leave balances for a teacher in a session year"""
        result = await db.execute(
            select(LeaveBalance)
            .options(
                joinedload(LeaveBalance.leave_type),
                joinedload(LeaveBalance.session_year)
            )
            .where(
                and_(
                    LeaveBalance.teacher_id == teacher_id,
                    LeaveBalance.session_year_id == session_year_id
                )
            )
        )
        return result.scalars().all()


class CRUDLeavePolicy(CRUDBase[LeavePolicy, dict, dict]):
    """CRUD operations for Leave Policy"""

    async def get_active_policies(self, db: AsyncSession) -> List[LeavePolicy]:
        """Get all active leave policies"""
        result = await db.execute(
            select(LeavePolicy)
            .options(joinedload(LeavePolicy.leave_type))
            .where(LeavePolicy.is_active == True)
            .order_by(LeavePolicy.policy_name)
        )
        return result.scalars().all()

    async def get_by_applicant_type(
        self,
        db: AsyncSession,
        *,
        applicant_type: ApplicantTypeEnum
    ) -> List[LeavePolicy]:
        """Get policies for specific applicant type"""
        result = await db.execute(
            select(LeavePolicy)
            .options(joinedload(LeavePolicy.leave_type))
            .where(
                and_(
                    LeavePolicy.is_active == True,
                    or_(
                        LeavePolicy.applicant_type == applicant_type.value,
                        LeavePolicy.applicant_type == 'both'
                    )
                )
            )
        )
        return result.scalars().all()


# Create instances
leave_request_crud = CRUDLeaveRequest(LeaveRequest)
leave_balance_crud = CRUDLeaveBalance(LeaveBalance)
leave_policy_crud = CRUDLeavePolicy(LeavePolicy)
