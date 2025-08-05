from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_, or_, func, desc

from app.crud.base import CRUDBase
from app.models.student import Student
from app.models.user import User
from app.models.fee import FeeRecord
from app.models.metadata import Gender, Class, SessionYear, UserType
from app.schemas.student import StudentCreate, StudentUpdate, ClassEnum, GenderEnum
from app.schemas.user import UserCreate
from app.core.security import get_password_hash


class CRUDStudent(CRUDBase[Student, StudentCreate, StudentUpdate]):
    def __init__(self):
        super().__init__(Student)

    async def get(self, db: AsyncSession, id: Any) -> Optional[Student]:
        """Override to include class relationship"""
        result = await db.execute(
            select(Student)
            .options(joinedload(Student.class_ref))
            .where(Student.id == id)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Student]:
        """Override to get all students (active and inactive) but exclude soft deleted"""
        query = select(self.model)

        # Only exclude soft deleted records, include both active and inactive
        if hasattr(self.model, 'is_deleted'):
            query = query.where(
                (self.model.is_deleted == False) | (self.model.is_deleted.is_(None))
            )

        result = await db.execute(
            query.offset(skip).limit(limit)
        )
        return result.scalars().all()
    async def get_by_admission_number(
        self, db: AsyncSession, *, admission_number: str
    ) -> Optional[Student]:
        result = await db.execute(
            select(Student).where(Student.admission_number == admission_number)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(
        self, db: AsyncSession, *, user_id: int
    ) -> Optional[Student]:
        """Get student by user_id"""
        result = await db.execute(
            select(Student).where(Student.user_id == user_id)
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

    async def create(self, db: AsyncSession, *, obj_in: StudentCreate) -> Student:
        """Override base create method to ensure email generation is always used"""
        from app.utils.email_generator import generate_student_email
        from app.core.logging import log_crud_operation

        # Auto-generate email if not provided
        student_data = obj_in.dict()
        if not student_data.get('email'):
            generated_email = await generate_student_email(
                db,
                obj_in.first_name,
                obj_in.last_name,
                obj_in.date_of_birth
            )
            student_data['email'] = generated_email
            log_crud_operation("STUDENT_EMAIL_AUTO_GENERATED", f"Auto-generated email in basic create method",
                             first_name=obj_in.first_name, last_name=obj_in.last_name,
                             email=generated_email)

        # Use the parent create method with the updated data
        updated_obj_in = StudentCreate(**student_data)
        return await super().create(db, obj_in=updated_obj_in)

    async def create_with_validation(self, db: AsyncSession, *, obj_in: StudentCreate) -> Student:
        """Create student with metadata validation and user account"""
        from app.core.logging import log_crud_operation
        from app.utils.email_generator import generate_student_email
        import logging

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

        # Auto-generate email if not provided
        student_data = obj_in.dict()
        if not student_data.get('email'):
            generated_email = await generate_student_email(
                db,
                obj_in.first_name,
                obj_in.last_name,
                obj_in.date_of_birth
            )
            student_data['email'] = generated_email
            log_crud_operation("STUDENT_EMAIL_AUTO_GENERATED", f"Auto-generated email for student",
                             first_name=obj_in.first_name, last_name=obj_in.last_name,
                             email=generated_email)

        # Create student
        db_obj = Student(**student_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        log_crud_operation("STUDENT_CREATE", f"Student record created",
                          student_id=db_obj.id, admission_number=obj_in.admission_number)

        # Create or link user account for student if email or phone is provided
        # Note: email is now always generated, so we should always create user account
        user_account = None
        if db_obj.email or obj_in.phone:
            try:
                # Get STUDENT user type ID
                student_user_type = await db.execute(select(UserType).where(UserType.name == "STUDENT"))
                student_user_type_obj = student_user_type.scalar_one_or_none()

                if not student_user_type_obj:
                    raise ValueError("STUDENT user type not found in database")

                # Use the email from the student record (either provided or auto-generated)
                user_email = db_obj.email
                if not user_email and obj_in.phone:
                    # Fallback: Generate email from phone for login purposes
                    user_email = f"student_{obj_in.phone}@sunriseschool.edu"

                log_crud_operation("USER_LINK_ATTEMPT", f"Attempting to link user account",
                                 student_id=db_obj.id, user_email=user_email)

                # Check if user with this email already exists
                existing_user_result = await db.execute(select(User).where(User.email == user_email))
                existing_user = existing_user_result.scalar_one_or_none()

                if existing_user:
                    # User already exists - link to existing user
                    log_crud_operation("USER_LINK_EXISTING", f"Linking to existing user",
                                     student_id=db_obj.id, user_id=existing_user.id, user_email=user_email)

                    # Verify the existing user is a student type
                    if existing_user.user_type_id != student_user_type_obj.id:
                        log_crud_operation("USER_LINK_WARNING", f"Existing user has different user type",
                                         "warning", user_id=existing_user.id,
                                         expected_type=student_user_type_obj.id,
                                         actual_type=existing_user.user_type_id)

                    # Link existing user to student
                    db_obj.user_id = existing_user.id
                    user_account = existing_user
                else:
                    # Create new user account
                    log_crud_operation("USER_CREATE_NEW", f"Creating new user account",
                                     student_id=db_obj.id, user_email=user_email)

                    user_account = User(
                        email=user_email,
                        hashed_password=get_password_hash("Sunrise@001"),  # Default password
                        first_name=obj_in.first_name,
                        last_name=obj_in.last_name,
                        phone=obj_in.phone,
                        user_type_id=student_user_type_obj.id,
                        is_active=True,
                        is_verified=False
                    )
                    db.add(user_account)
                    await db.commit()
                    await db.refresh(user_account)

                    # Link new user account to student
                    db_obj.user_id = user_account.id

                    log_crud_operation("USER_CREATE_SUCCESS", f"New user account created and linked",
                                     student_id=db_obj.id, user_id=user_account.id)

                # Commit the student-user link
                await db.commit()
                await db.refresh(db_obj)

                log_crud_operation("STUDENT_USER_LINK_SUCCESS", f"Student successfully linked to user",
                                 student_id=db_obj.id, user_id=db_obj.user_id)

            except Exception as user_creation_error:
                # Log the error with full details
                log_crud_operation("STUDENT_USER_LINK_ERROR", f"Failed to create/link user account: {str(user_creation_error)}",
                                 "error", student_id=db_obj.id, admission_number=obj_in.admission_number,
                                 error_type=type(user_creation_error).__name__)
                logging.exception("Full user creation/linking error traceback:")

                # Don't fail student creation, but ensure we log this properly
                print(f"Warning: Failed to create/link user account for student {obj_in.admission_number}: {user_creation_error}")

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
        is_active: Optional[bool] = None
    ) -> tuple[List[Student], int]:
        query = select(Student)

        # Apply filters
        conditions = []

        # Only filter by is_active if explicitly provided
        if is_active is not None:
            conditions.append(Student.is_active == is_active)

        # Always exclude soft deleted records
        if hasattr(Student, 'is_deleted'):
            conditions.append(
                (Student.is_deleted == False) | (Student.is_deleted.is_(None))
            )
        
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
