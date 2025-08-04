from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_, or_, func, desc, text
from datetime import datetime
import json

from app.crud.base import CRUDBase
from app.models.teacher import Teacher
from app.models.user import User
from app.models.metadata import Gender, Qualification, EmploymentStatus, Class
from app.schemas.teacher import TeacherCreate, TeacherUpdate, GenderEnum, QualificationEnum, EmploymentStatusEnum
from app.core.security import get_password_hash


class CRUDTeacher(CRUDBase[Teacher, TeacherCreate, TeacherUpdate]):
    async def get_by_employee_id(
        self, db: AsyncSession, *, employee_id: str
    ) -> Optional[Teacher]:
        result = await db.execute(
            select(Teacher).where(
                and_(
                    Teacher.employee_id == employee_id,
                    Teacher.is_deleted != True  # Exclude soft deleted
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_email(
        self, db: AsyncSession, *, email: str
    ) -> Optional[Teacher]:
        result = await db.execute(
            select(Teacher).where(
                and_(
                    Teacher.email == email,
                    Teacher.is_deleted != True  # Exclude soft deleted
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(
        self, db: AsyncSession, *, user_id: int
    ) -> Optional[Teacher]:
        result = await db.execute(
            select(Teacher).where(
                and_(
                    Teacher.user_id == user_id,
                    Teacher.is_deleted != True  # Exclude soft deleted
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_with_metadata(
        self, db: AsyncSession, *, id: int
    ) -> Optional[Dict[str, Any]]:
        """Get teacher with metadata relationships"""
        query = text("""
            SELECT
                t.*,
                g.name as gender_name,
                q.name as qualification_name,
                es.name as employment_status_name,
                c.name as class_teacher_of_name
            FROM teachers t
            LEFT JOIN genders g ON t.gender_id = g.id
            LEFT JOIN qualifications q ON t.qualification_id = q.id
            LEFT JOIN employment_statuses es ON t.employment_status_id = es.id
            LEFT JOIN classes c ON t.class_teacher_of_id = c.id
            WHERE t.id = :teacher_id AND (t.is_deleted IS NULL OR t.is_deleted = FALSE)
        """)

        result = await db.execute(query, {"teacher_id": id})
        row = result.fetchone()

        if row:
            return dict(row._mapping)
        return None

    async def get_multi_with_filters(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        department_filter: Optional[str] = None,
        position_filter: Optional[str] = None,
        qualification_filter: Optional[int] = None,
        employment_status_filter: Optional[int] = None,
        search: Optional[str] = None,
        is_active: bool = True
    ) -> tuple[List[Dict[str, Any]], int]:
        """Get teachers with metadata relationships and filters"""

        # Build WHERE conditions
        where_conditions = ["(t.is_deleted IS NULL OR t.is_deleted = FALSE)"]
        params = {}

        if is_active is not None:
            where_conditions.append("t.is_active = :is_active")
            params["is_active"] = is_active

        if department_filter:
            where_conditions.append("t.department = :department_filter")
            params["department_filter"] = department_filter

        if position_filter:
            where_conditions.append("t.position = :position_filter")
            params["position_filter"] = position_filter

        if qualification_filter:
            where_conditions.append("t.qualification_id = :qualification_filter")
            params["qualification_filter"] = qualification_filter

        if employment_status_filter:
            where_conditions.append("t.employment_status_id = :employment_status_filter")
            params["employment_status_filter"] = employment_status_filter

        if search:
            where_conditions.append("""
                (t.first_name ILIKE :search OR
                 t.last_name ILIKE :search OR
                 t.employee_id ILIKE :search OR
                 t.email ILIKE :search OR
                 CONCAT(t.first_name, ' ', t.last_name) ILIKE :search)
            """)
            params["search"] = f"%{search}%"

        where_clause = " AND ".join(where_conditions)

        # Count query
        count_query = text(f"""
            SELECT COUNT(t.id)
            FROM teachers t
            WHERE {where_clause}
        """)

        count_result = await db.execute(count_query, params)
        total = count_result.scalar()

        # Main query with metadata
        query = text(f"""
            SELECT
                t.*,
                g.name as gender_name,
                q.name as qualification_name,
                es.name as employment_status_name,
                c.name as class_teacher_of_name
            FROM teachers t
            LEFT JOIN genders g ON t.gender_id = g.id
            LEFT JOIN qualifications q ON t.qualification_id = q.id
            LEFT JOIN employment_statuses es ON t.employment_status_id = es.id
            LEFT JOIN classes c ON t.class_teacher_of_id = c.id
            WHERE {where_clause}
            ORDER BY t.first_name, t.last_name
            LIMIT :limit OFFSET :skip
        """)

        params.update({"limit": limit, "skip": skip})
        result = await db.execute(query, params)

        teachers = [dict(row._mapping) for row in result.fetchall()]
        return teachers, total

    async def get_by_department(
        self, db: AsyncSession, *, department: str
    ) -> List[Teacher]:
        result = await db.execute(
            select(Teacher).where(
                and_(
                    Teacher.department == department,
                    Teacher.is_active == True,
                    Teacher.is_deleted != True  # Exclude soft deleted
                )
            ).order_by(Teacher.first_name)
        )
        return result.scalars().all()

    async def get_by_subjects(
        self, db: AsyncSession, *, subject: str
    ) -> List[Teacher]:
        result = await db.execute(
            select(Teacher).where(
                and_(
                    Teacher.subjects.ilike(f"%{subject}%"),
                    Teacher.is_active == True,
                    Teacher.is_deleted != True  # Exclude soft deleted
                )
            ).order_by(Teacher.first_name)
        )
        return result.scalars().all()

    async def search_teachers(
        self, db: AsyncSession, *, search_term: str, limit: int = 20
    ) -> List[Teacher]:
        search_conditions = [
            Teacher.first_name.ilike(f"%{search_term}%"),
            Teacher.last_name.ilike(f"%{search_term}%"),
            Teacher.employee_id.ilike(f"%{search_term}%"),
            Teacher.email.ilike(f"%{search_term}%"),
            func.concat(Teacher.first_name, ' ', Teacher.last_name).ilike(f"%{search_term}%")
        ]

        result = await db.execute(
            select(Teacher)
            .where(
                and_(
                    Teacher.is_active == True,
                    Teacher.is_deleted != True,  # Exclude soft deleted
                    or_(*search_conditions)
                )
            )
            .order_by(Teacher.first_name, Teacher.last_name)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_with_user_account(
        self, db: AsyncSession, *, obj_in: TeacherCreate
    ) -> Teacher:
        """Create teacher with associated user account"""
        from app.crud.crud_user import CRUDUser
        from app.schemas.user import UserCreate, UserTypeEnum

        # Create teacher record first
        teacher = await self.create(db, obj_in=obj_in)

        # Create user account for teacher login
        user_crud = CRUDUser()

        # Use email if available, otherwise generate from phone
        user_email = obj_in.email
        if not user_email and obj_in.phone:
            user_email = f"teacher_{obj_in.phone}@sunriseschool.edu"

        # Check if user with this email already exists
        existing_user = await user_crud.get_by_email(db, email=user_email)
        if not existing_user:
            user_data = UserCreate(
                email=user_email,
                password="Sunrise@001",  # Default password
                first_name=obj_in.first_name,
                last_name=obj_in.last_name,
                phone=obj_in.phone,
                user_type_id=2  # TEACHER user type ID
            )

            user = await user_crud.create(db, obj_in=user_data)

            # Link teacher to user
            teacher.user_id = user.id
            await db.commit()
            await db.refresh(teacher)

        return teacher

    async def soft_delete(
        self, db: AsyncSession, *, id: int
    ) -> Optional[Teacher]:
        """Soft delete teacher by setting is_deleted=True and deleted_date"""
        teacher = await self.get(db, id=id)
        if teacher:
            teacher.is_deleted = True
            teacher.deleted_date = datetime.utcnow()
            teacher.is_active = False  # Also deactivate
            await db.commit()
            await db.refresh(teacher)
        return teacher

    async def get_dashboard_stats(self, db: AsyncSession) -> Dict[str, Any]:
        # Total teachers (excluding soft deleted)
        total_result = await db.execute(
            select(func.count(Teacher.id)).where(
                and_(
                    Teacher.is_active == True,
                    Teacher.is_deleted != True
                )
            )
        )
        total_teachers = total_result.scalar()

        # Active teachers (assuming all active teachers are currently active)
        active_teachers = total_teachers

        # Department distribution
        dept_result = await db.execute(
            select(
                Teacher.department,
                func.count(Teacher.id).label('count')
            )
            .where(
                and_(
                    Teacher.is_active == True,
                    Teacher.is_deleted != True
                )
            )
            .group_by(Teacher.department)
            .order_by(Teacher.department)
        )

        departments = [
            {'department': row.department or 'Not Assigned', 'count': row.count}
            for row in dept_result
        ]

        # Qualification breakdown using metadata
        qual_result = await db.execute(
            text("""
                SELECT q.name as qualification, COUNT(t.id) as count
                FROM teachers t
                LEFT JOIN qualifications q ON t.qualification_id = q.id
                WHERE t.is_active = TRUE AND (t.is_deleted IS NULL OR t.is_deleted = FALSE)
                GROUP BY q.name
                ORDER BY q.name
            """)
        )

        qualification_breakdown = [
            {'qualification': row.qualification or 'Not Specified', 'count': row.count}
            for row in qual_result
        ]

        # Experience breakdown
        exp_result = await db.execute(
            select(
                func.case(
                    (Teacher.experience_years < 2, '0-2 years'),
                    (Teacher.experience_years < 5, '2-5 years'),
                    (Teacher.experience_years < 10, '5-10 years'),
                    else_='10+ years'
                ).label('experience_range'),
                func.count(Teacher.id).label('count')
            )
            .where(
                and_(
                    Teacher.is_active == True,
                    Teacher.is_deleted != True
                )
            )
            .group_by('experience_range')
        )

        experience_breakdown = [
            {'experience_range': row.experience_range, 'count': row.count}
            for row in exp_result
        ]

        return {
            'total_teachers': total_teachers,
            'active_teachers': active_teachers,
            'departments': departments,
            'qualification_breakdown': qualification_breakdown,
            'experience_breakdown': experience_breakdown
        }

    async def get_recent_joinings(
        self, db: AsyncSession, *, limit: int = 10
    ) -> List[Teacher]:
        result = await db.execute(
            select(Teacher)
            .where(
                and_(
                    Teacher.is_active == True,
                    Teacher.is_deleted != True
                )
            )
            .order_by(desc(Teacher.joining_date))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_departments(self, db: AsyncSession) -> List[str]:
        result = await db.execute(
            select(Teacher.department)
            .where(
                and_(
                    Teacher.is_active == True,
                    Teacher.is_deleted != True,
                    Teacher.department.isnot(None)
                )
            )
            .distinct()
            .order_by(Teacher.department)
        )
        return [row.department for row in result]

    async def get_positions(self, db: AsyncSession) -> List[str]:
        result = await db.execute(
            select(Teacher.position)
            .where(
                and_(
                    Teacher.is_active == True,
                    Teacher.is_deleted != True
                )
            )
            .distinct()
            .order_by(Teacher.position)
        )
        return [row.position for row in result]


# Create instance
teacher_crud = CRUDTeacher(Teacher)
