from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_, or_, func, desc

from app.crud.base import CRUDBase
from app.models.student import Student
from app.models.fee import FeeRecord
from app.models.metadata import Gender, Class, SessionYear
from app.schemas.student import StudentCreate, StudentUpdate, ClassEnum, GenderEnum


class CRUDStudent(CRUDBase[Student, StudentCreate, StudentUpdate]):
    def __init__(self):
        super().__init__(Student)
    async def get_by_admission_number(
        self, db: AsyncSession, *, admission_number: str
    ) -> Optional[Student]:
        result = await db.execute(
            select(Student).where(Student.admission_number == admission_number)
        )
        return result.scalar_one_or_none()

    async def get_with_metadata(self, db: AsyncSession, id: int) -> Optional[Student]:
        """Get student with metadata relationships loaded"""
        result = await db.execute(
            select(Student)
            .options(
                selectinload(Student.gender),
                selectinload(Student.class_ref),
                selectinload(Student.session_year)
            )
            .where(Student.id == id)
        )
        return result.scalar_one_or_none()

    async def get_with_fees(self, db: AsyncSession, id: int) -> Optional[Student]:
        result = await db.execute(
            select(Student)
            .options(selectinload(Student.fee_records))
            .where(Student.id == id)
        )
        return result.scalar_one_or_none()

    async def create_with_validation(self, db: AsyncSession, *, obj_in: StudentCreate) -> Student:
        """Create student with metadata validation"""
        # Validate metadata IDs exist
        if obj_in.gender_id:
            gender_result = await db.execute(select(Gender).where(Gender.id == obj_in.gender_id))
            if not gender_result.scalar_one_or_none():
                raise ValueError(f"Invalid gender_id: {obj_in.gender_id}")

        if obj_in.class_id:
            class_result = await db.execute(select(Class).where(Class.id == obj_in.class_id))
            if not class_result.scalar_one_or_none():
                raise ValueError(f"Invalid class_id: {obj_in.class_id}")

        if obj_in.session_year_id:
            session_year_result = await db.execute(select(SessionYear).where(SessionYear.id == obj_in.session_year_id))
            if not session_year_result.scalar_one_or_none():
                raise ValueError(f"Invalid session_year_id: {obj_in.session_year_id}")

        # Create student
        db_obj = Student(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_multi_with_filters(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        class_filter: Optional[str] = None,
        section_filter: Optional[str] = None,
        gender_filter: Optional[str] = None,
        search: Optional[str] = None,
        is_active: bool = True
    ) -> tuple[List[Student], int]:
        query = select(Student)
        
        # Apply filters
        conditions = [Student.is_active == is_active]
        
        if class_filter:
            conditions.append(Student.current_class == class_filter)
        
        if section_filter:
            conditions.append(Student.section == section_filter)
        
        if gender_filter:
            conditions.append(Student.gender == gender_filter)
        
        if search:
            search_conditions = [
                Student.first_name.ilike(f"%{search}%"),
                Student.last_name.ilike(f"%{search}%"),
                Student.admission_number.ilike(f"%{search}%"),
                Student.father_name.ilike(f"%{search}%"),
                Student.mother_name.ilike(f"%{search}%")
            ]
            conditions.append(or_(*search_conditions))
        
        query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count(Student.id)).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.order_by(Student.first_name, Student.last_name).offset(skip).limit(limit)
        result = await db.execute(query)
        
        return result.scalars().all(), total

    async def get_by_class(
        self, db: AsyncSession, *, class_name: str, section: Optional[str] = None
    ) -> List[Student]:
        query = select(Student).where(
            and_(
                Student.current_class == class_name,
                Student.is_active == True
            )
        )
        
        if section:
            query = query.where(Student.section == section)
        
        query = query.order_by(Student.roll_number, Student.first_name)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_students_with_pending_fees(
        self, db: AsyncSession, *, session_year: Optional[str] = None
    ) -> List[Student]:
        query = (
            select(Student)
            .join(FeeRecord)
            .where(
                and_(
                    Student.is_active == True,
                    FeeRecord.balance_amount > 0
                )
            )
        )
        
        if session_year:
            query = query.where(FeeRecord.session_year == session_year)
        
        query = query.distinct().order_by(Student.first_name)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_class_statistics(self, db: AsyncSession) -> List[Dict[str, Any]]:
        result = await db.execute(
            select(
                Student.current_class,
                func.count(Student.id).label('total_students'),
                func.count(
                    func.case(
                        (Student.gender == GenderEnum.MALE, 1),
                        else_=None
                    )
                ).label('male_count'),
                func.count(
                    func.case(
                        (Student.gender == GenderEnum.FEMALE, 1),
                        else_=None
                    )
                ).label('female_count')
            )
            .where(Student.is_active == True)
            .group_by(Student.current_class)
            .order_by(Student.current_class)
        )
        
        stats = []
        for row in result:
            stats.append({
                'class_name': row.current_class,
                'total_students': row.total_students,
                'male_count': row.male_count,
                'female_count': row.female_count
            })
        
        return stats

    async def get_recent_admissions(
        self, db: AsyncSession, *, limit: int = 10
    ) -> List[Student]:
        result = await db.execute(
            select(Student)
            .where(Student.is_active == True)
            .order_by(desc(Student.admission_date))
            .limit(limit)
        )
        return result.scalars().all()

    async def search_students(
        self, db: AsyncSession, *, search_term: str, limit: int = 20
    ) -> List[Student]:
        search_conditions = [
            Student.first_name.ilike(f"%{search_term}%"),
            Student.last_name.ilike(f"%{search_term}%"),
            Student.admission_number.ilike(f"%{search_term}%"),
            func.concat(Student.first_name, ' ', Student.last_name).ilike(f"%{search_term}%")
        ]
        
        result = await db.execute(
            select(Student)
            .where(
                and_(
                    Student.is_active == True,
                    or_(*search_conditions)
                )
            )
            .order_by(Student.first_name, Student.last_name)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_dashboard_stats(self, db: AsyncSession) -> Dict[str, Any]:
        # Total students
        total_result = await db.execute(
            select(func.count(Student.id)).where(Student.is_active == True)
        )
        total_students = total_result.scalar()
        
        # Gender distribution
        gender_result = await db.execute(
            select(
                Student.gender,
                func.count(Student.id).label('count')
            )
            .where(Student.is_active == True)
            .group_by(Student.gender)
        )
        
        gender_stats = {row.gender: row.count for row in gender_result}
        
        # Class distribution
        class_result = await db.execute(
            select(
                Student.current_class,
                func.count(Student.id).label('count')
            )
            .where(Student.is_active == True)
            .group_by(Student.current_class)
            .order_by(Student.current_class)
        )
        
        class_stats = [
            {'class_name': row.current_class, 'count': row.count}
            for row in class_result
        ]
        
        return {
            'total_students': total_students,
            'gender_distribution': gender_stats,
            'class_distribution': class_stats
        }


# Create instance
student_crud = CRUDStudent()
