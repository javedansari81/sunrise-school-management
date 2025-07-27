from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_, or_, func, desc
import json

from app.crud.base import CRUDBase
from app.models.teacher import Teacher
from app.schemas.teacher import TeacherCreate, TeacherUpdate, GenderEnum, QualificationEnum, EmploymentStatusEnum


class CRUDTeacher(CRUDBase[Teacher, TeacherCreate, TeacherUpdate]):
    async def get_by_employee_id(
        self, db: AsyncSession, *, employee_id: str
    ) -> Optional[Teacher]:
        result = await db.execute(
            select(Teacher).where(Teacher.employee_id == employee_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(
        self, db: AsyncSession, *, email: str
    ) -> Optional[Teacher]:
        result = await db.execute(
            select(Teacher).where(Teacher.email == email)
        )
        return result.scalar_one_or_none()

    async def get_multi_with_filters(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        department_filter: Optional[str] = None,
        position_filter: Optional[str] = None,
        qualification_filter: Optional[str] = None,
        employment_status_filter: Optional[str] = None,
        search: Optional[str] = None,
        is_active: bool = True
    ) -> tuple[List[Teacher], int]:
        query = select(Teacher)
        
        # Apply filters
        conditions = [Teacher.is_active == is_active]
        
        if department_filter:
            conditions.append(Teacher.department == department_filter)
        
        if position_filter:
            conditions.append(Teacher.position == position_filter)
        
        if qualification_filter:
            conditions.append(Teacher.qualification == qualification_filter)
        
        if employment_status_filter:
            conditions.append(Teacher.employment_status == employment_status_filter)
        
        if search:
            search_conditions = [
                Teacher.first_name.ilike(f"%{search}%"),
                Teacher.last_name.ilike(f"%{search}%"),
                Teacher.employee_id.ilike(f"%{search}%"),
                Teacher.email.ilike(f"%{search}%"),
                func.concat(Teacher.first_name, ' ', Teacher.last_name).ilike(f"%{search}%")
            ]
            conditions.append(or_(*search_conditions))
        
        query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count(Teacher.id)).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.order_by(Teacher.first_name, Teacher.last_name).offset(skip).limit(limit)
        result = await db.execute(query)
        
        return result.scalars().all(), total

    async def get_by_department(
        self, db: AsyncSession, *, department: str
    ) -> List[Teacher]:
        result = await db.execute(
            select(Teacher).where(
                and_(
                    Teacher.department == department,
                    Teacher.is_active == True
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
                    Teacher.is_active == True
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
                    or_(*search_conditions)
                )
            )
            .order_by(Teacher.first_name, Teacher.last_name)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_dashboard_stats(self, db: AsyncSession) -> Dict[str, Any]:
        # Total teachers
        total_result = await db.execute(
            select(func.count(Teacher.id)).where(Teacher.is_active == True)
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
            .where(Teacher.is_active == True)
            .group_by(Teacher.department)
            .order_by(Teacher.department)
        )
        
        departments = [
            {'department': row.department or 'Not Assigned', 'count': row.count}
            for row in dept_result
        ]
        
        # Qualification breakdown
        qual_result = await db.execute(
            select(
                Teacher.qualification,
                func.count(Teacher.id).label('count')
            )
            .where(Teacher.is_active == True)
            .group_by(Teacher.qualification)
            .order_by(Teacher.qualification)
        )
        
        qualification_breakdown = [
            {'qualification': row.qualification, 'count': row.count}
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
            .where(Teacher.is_active == True)
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
            .where(Teacher.is_active == True)
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
            .where(Teacher.is_active == True)
            .distinct()
            .order_by(Teacher.position)
        )
        return [row.position for row in result]


# Create instance
teacher_crud = CRUDTeacher(Teacher)
