from typing import List, Optional, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_, or_, func, desc, text
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.crud.base import CRUDBase
from app.models.student import Student
from app.models.user import User
from app.models.fee import FeeRecord
from app.models.metadata import Gender, Class, SessionYear, UserType
from app.schemas.student import StudentCreate, StudentUpdate, ClassEnum, GenderEnum
from app.schemas.user import UserCreate
from app.core.security import get_password_hash
from app.core.error_handler import (
    DatabaseErrorHandler, ValidationErrorHandler,
    raise_database_http_exception
)


class CRUDStudent(CRUDBase[Student, StudentCreate, StudentUpdate]):
    def __init__(self):
        super().__init__(Student)

    async def get_next_admission_number(self, db: AsyncSession) -> str:
        """
        Get the next available admission number by finding the maximum existing number
        and incrementing it. Handles both numeric and alphanumeric formats.

        Returns:
            str: Next admission number (e.g., "ADM001", "ADM002", etc.)
        """
        try:
            # Get the maximum admission number from the database
            result = await db.execute(
                select(Student.admission_number)
                .where(
                    and_(
                        Student.is_deleted != True,
                        Student.admission_number.isnot(None)
                    )
                )
                .order_by(desc(Student.admission_number))
                .limit(1)
            )
            max_admission_number = result.scalar_one_or_none()

            if not max_admission_number:
                # No students exist yet, start with default
                return "ADM001"

            # Extract numeric part from admission number
            # Handle formats like "ADM001", "001", "ADM-001", etc.
            import re
            numeric_match = re.search(r'(\d+)$', max_admission_number)

            if numeric_match:
                # Extract the numeric part
                numeric_part = numeric_match.group(1)
                prefix = max_admission_number[:numeric_match.start()]

                # Increment the number
                next_number = int(numeric_part) + 1

                # Preserve the zero-padding
                next_number_str = str(next_number).zfill(len(numeric_part))

                # Combine prefix and new number
                return f"{prefix}{next_number_str}"
            else:
                # If no numeric part found, default to ADM001
                return "ADM001"

        except Exception as e:
            # On any error, return default
            return "ADM001"

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
            select(Student).where(
                and_(
                    Student.admission_number == admission_number,
                    (Student.is_deleted == False) | (Student.is_deleted.is_(None))
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_email(
        self, db: AsyncSession, *, email: str
    ) -> Optional[Student]:
        result = await db.execute(
            select(Student).where(
                and_(
                    Student.email == email,
                    (Student.is_deleted == False) | (Student.is_deleted.is_(None))
                )
            )
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

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: Student,
        obj_in: Union[StudentUpdate, Dict[str, Any]]
    ) -> Student:
        """
        Override update method to cascade is_active status to user account.
        When student.is_active changes, automatically update users.is_active.
        Also re-detect siblings if father details change.
        """
        from app.core.logging import log_crud_operation
        import logging

        # Check if is_active is being updated
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        # Check if father details are changing (for sibling re-detection)
        father_details_changed = False
        if 'father_name' in update_data or 'father_phone' in update_data:
            old_father_name = db_obj.father_name
            old_father_phone = db_obj.father_phone
            new_father_name = update_data.get('father_name', old_father_name)
            new_father_phone = update_data.get('father_phone', old_father_phone)

            if old_father_name != new_father_name or old_father_phone != new_father_phone:
                father_details_changed = True

        # If is_active is being changed, cascade to user account
        if 'is_active' in update_data and db_obj.user_id:
            new_is_active = update_data['is_active']

            # Only update if the value is actually changing
            if db_obj.is_active != new_is_active:
                # Get the associated user
                user_result = await db.execute(
                    select(User).where(User.id == db_obj.user_id)
                )
                user = user_result.scalar_one_or_none()

                if user:
                    # Update user's is_active status to match student's is_active
                    user.is_active = new_is_active
                    db.add(user)
                    # Note: We don't commit here, let the parent update method handle the commit

        # Call parent update method to handle the actual student update
        updated_student = await super().update(db, db_obj=db_obj, obj_in=obj_in)

        # Re-detect siblings if father details changed
        if father_details_changed:
            try:
                from app.crud.crud_student_sibling import student_sibling_crud

                # Remove old sibling relationships
                await db.execute(
                    text("DELETE FROM student_siblings WHERE student_id = :sid OR sibling_student_id = :sid"),
                    {"sid": updated_student.id}
                )

                # Detect new siblings
                new_father_name = update_data.get('father_name', updated_student.father_name)
                new_father_phone = update_data.get('father_phone', updated_student.father_phone)

                if new_father_name and new_father_phone:
                    potential_siblings = await student_sibling_crud.detect_siblings_by_father_and_phone(
                        db,
                        father_name=new_father_name,
                        father_phone=new_father_phone,
                        exclude_student_id=updated_student.id
                    )

                    if potential_siblings:
                        sibling_ids = [s.id for s in potential_siblings]
                        await student_sibling_crud.create_sibling_relationships_for_student(
                            db,
                            student_id=updated_student.id,
                            detected_sibling_ids=sibling_ids
                        )

                        log_crud_operation("SIBLING_REDETECTION", f"Re-detected {len(potential_siblings)} siblings after update",
                                         student_id=updated_student.id, sibling_count=len(potential_siblings))

                await db.commit()

            except Exception as sibling_error:
                log_crud_operation("SIBLING_REDETECTION_ERROR", f"Failed to re-detect siblings: {str(sibling_error)}",
                                 "error", student_id=updated_student.id)
                logging.exception("Sibling re-detection error:")
                # Don't fail update due to sibling detection errors

        return updated_student

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
        """Override base create method with validation and error handling"""
        from app.utils.email_generator import generate_student_email
        from app.core.logging import log_crud_operation

        try:
            # Basic validation will be handled by database constraints
            student_data = obj_in.dict()

            # Auto-generate email if not provided
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

        except IntegrityError as e:
            await db.rollback()
            raise_database_http_exception(e, "student creation")
        except Exception as e:
            await db.rollback()
            raise

    async def create_with_validation(self, db: AsyncSession, *, obj_in: StudentCreate) -> Student:
        """Create student with comprehensive validation and user account"""
        from app.core.logging import log_crud_operation
        from app.utils.email_generator import generate_student_email
        import logging

        try:
            # Basic validation will be handled by database constraints
            student_data = obj_in.dict()

            # Auto-generate email if not provided
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
                            password=get_password_hash("Sunrise@001"),  # Default password
                            first_name=obj_in.first_name,
                            last_name=obj_in.last_name,
                            phone=obj_in.phone,
                            user_type_id=student_user_type_obj.id,
                            is_active=True
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

            # Detect and link siblings after student creation
            detected_siblings = []
            if obj_in.father_name and obj_in.father_phone:
                try:
                    from app.crud.crud_student_sibling import student_sibling_crud

                    # Detect potential siblings
                    potential_siblings = await student_sibling_crud.detect_siblings_by_father_and_phone(
                        db,
                        father_name=obj_in.father_name,
                        father_phone=obj_in.father_phone,
                        exclude_student_id=db_obj.id
                    )

                    if potential_siblings:
                        # Create sibling relationships
                        sibling_ids = [s.id for s in potential_siblings]
                        await student_sibling_crud.create_sibling_relationships_for_student(
                            db,
                            student_id=db_obj.id,
                            detected_sibling_ids=sibling_ids
                        )
                        detected_siblings = potential_siblings

                        log_crud_operation("SIBLING_DETECTION", f"Detected and linked {len(detected_siblings)} siblings",
                                         student_id=db_obj.id, sibling_count=len(detected_siblings))

                except Exception as sibling_error:
                    log_crud_operation("SIBLING_DETECTION_ERROR", f"Failed to detect/link siblings: {str(sibling_error)}",
                                     "error", student_id=db_obj.id)
                    logging.exception("Sibling detection error:")
                    # Don't fail student creation due to sibling detection errors

            # Store detected siblings info on the object for later use
            db_obj._detected_siblings = detected_siblings

            return db_obj

        except IntegrityError as e:
            await db.rollback()
            raise_database_http_exception(e, "student creation with validation")
        except Exception as e:
            await db.rollback()
            raise

    async def get_multi_with_filters(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        class_filter: Optional[int] = None,
        section_filter: Optional[str] = None,
        gender_filter: Optional[int] = None,
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
            # Filter by class ID
            conditions.append(Student.class_id == class_filter)

        if section_filter:
            conditions.append(Student.section == section_filter)

        if gender_filter:
            # Filter by gender ID
            conditions.append(Student.gender_id == gender_filter)

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
            .where(
                and_(
                    Student.is_active == True,
                    or_(Student.is_deleted == False, Student.is_deleted.is_(None))
                )
            )
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
            .where(
                and_(
                    Student.is_active == True,
                    or_(Student.is_deleted == False, Student.is_deleted.is_(None))
                )
            )
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
                    or_(Student.is_deleted == False, Student.is_deleted.is_(None)),
                    or_(*search_conditions)
                )
            )
            .order_by(Student.first_name, Student.last_name)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_dashboard_stats(self, db: AsyncSession) -> Dict[str, Any]:
        # Total students (excluding soft deleted)
        total_result = await db.execute(
            select(func.count(Student.id)).where(
                and_(
                    Student.is_active == True,
                    or_(Student.is_deleted == False, Student.is_deleted.is_(None))
                )
            )
        )
        total_students = total_result.scalar()

        # Gender distribution (excluding soft deleted)
        gender_result = await db.execute(
            select(
                Student.gender_id,
                func.count(Student.id).label('count')
            )
            .where(
                and_(
                    Student.is_active == True,
                    or_(Student.is_deleted == False, Student.is_deleted.is_(None))
                )
            )
            .group_by(Student.gender_id)
        )

        gender_stats = {row.gender_id: row.count for row in gender_result}

        # Class distribution (excluding soft deleted)
        class_result = await db.execute(
            select(
                Student.class_id,
                func.count(Student.id).label('count')
            )
            .where(
                and_(
                    Student.is_active == True,
                    or_(Student.is_deleted == False, Student.is_deleted.is_(None))
                )
            )
            .group_by(Student.class_id)
            .order_by(Student.class_id)
        )

        class_stats = [
            {'class_id': row.class_id, 'count': row.count}
            for row in class_result
        ]

        return {
            'total_students': total_students,
            'gender_distribution': gender_stats,
            'class_distribution': class_stats
        }

    async def remove(self, db: AsyncSession, *, id: int) -> Student:
        """
        Override base remove method to cascade soft delete to user account
        This is called by the DELETE endpoint
        """
        obj = await self.get(db, id=id)
        if obj:
            # Soft delete using available columns
            obj.is_active = False
            obj.is_deleted = True
            obj.deleted_date = datetime.utcnow()

            # Cascade soft delete to user account if exists
            if obj.user_id:
                user_result = await db.execute(
                    select(User).where(User.id == obj.user_id)
                )
                user = user_result.scalar_one_or_none()

                if user:
                    user.is_active = False
                    user.is_deleted = True
                    user.deleted_date = datetime.utcnow()
                    db.add(user)

            db.add(obj)
            await db.commit()
            await db.refresh(obj)
        return obj

    async def soft_delete(self, db: AsyncSession, *, id: int) -> Optional[Student]:
        """
        Soft delete a student record by setting is_deleted=True and deleted_date
        Also cascades soft delete to the associated user account
        """
        try:
            # Get the student
            result = await db.execute(
                select(Student).where(Student.id == id)
            )
            obj = result.scalar_one_or_none()

            if not obj:
                return None

            # Set soft delete flags
            obj.is_deleted = True
            obj.deleted_date = datetime.utcnow()
            obj.is_active = False  # Also deactivate

            # Cascade soft delete to user account if exists
            if obj.user_id:
                user_result = await db.execute(
                    select(User).where(User.id == obj.user_id)
                )
                user = user_result.scalar_one_or_none()

                if user:
                    user.is_active = False
                    user.is_deleted = True
                    user.deleted_date = datetime.utcnow()
                    db.add(user)

            db.add(obj)
            await db.commit()
            await db.refresh(obj)

            return obj
        except Exception as e:
            await db.rollback()
            raise e

    async def restore(self, db: AsyncSession, *, id: int) -> Optional[Student]:
        """
        Restore a soft-deleted student record
        Also restores the associated user account (clears is_deleted flag)
        """
        try:
            # Get the student (including soft deleted ones)
            result = await db.execute(
                select(Student).where(Student.id == id)
            )
            obj = result.scalar_one_or_none()

            if not obj:
                return None

            # Clear soft delete flags
            obj.is_deleted = False
            obj.deleted_date = None
            obj.is_active = True  # Reactivate

            # Cascade restore to user account if exists
            if obj.user_id:
                user_result = await db.execute(
                    select(User).where(User.id == obj.user_id)
                )
                user = user_result.scalar_one_or_none()

                if user:
                    user.is_active = True
                    user.is_deleted = False
                    user.deleted_date = None
                    db.add(user)

            db.add(obj)
            await db.commit()
            await db.refresh(obj)

            return obj
        except Exception as e:
            await db.rollback()
            raise e

    async def get_deleted(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Student]:
        """Get all soft-deleted students"""
        result = await db.execute(
            select(Student)
            .where(Student.is_deleted == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()


# Create instance
student_crud = CRUDStudent()
