"""
Utility functions for handling soft-delete validation and user feedback
"""
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_

from app.models.teacher import Teacher
from app.models.student import Student
from app.models.user import User


async def check_teacher_soft_deleted_by_employee_id(
    db: AsyncSession, employee_id: str
) -> Optional[Teacher]:
    """
    Check if a teacher with the given employee_id exists only in soft-deleted state
    Returns the soft-deleted teacher if found, None otherwise
    """
    result = await db.execute(
        select(Teacher).where(
            and_(
                Teacher.employee_id == employee_id,
                Teacher.is_deleted == True
            )
        )
    )
    return result.scalar_one_or_none()


async def check_teacher_soft_deleted_by_email(
    db: AsyncSession, email: str
) -> Optional[Teacher]:
    """
    Check if a teacher with the given email exists only in soft-deleted state
    Returns the soft-deleted teacher if found, None otherwise
    """
    result = await db.execute(
        select(Teacher).where(
            and_(
                Teacher.email == email,
                Teacher.is_deleted == True
            )
        )
    )
    return result.scalar_one_or_none()


async def check_student_soft_deleted_by_admission_number(
    db: AsyncSession, admission_number: str
) -> Optional[Student]:
    """
    Check if a student with the given admission_number exists only in soft-deleted state
    Returns the soft-deleted student if found, None otherwise
    """
    result = await db.execute(
        select(Student).where(
            and_(
                Student.admission_number == admission_number,
                Student.is_deleted == True
            )
        )
    )
    return result.scalar_one_or_none()


async def check_student_soft_deleted_by_email(
    db: AsyncSession, email: str
) -> Optional[Student]:
    """
    Check if a student with the given email exists only in soft-deleted state
    Returns the soft-deleted student if found, None otherwise
    """
    result = await db.execute(
        select(Student).where(
            and_(
                Student.email == email,
                Student.is_deleted == True
            )
        )
    )
    return result.scalar_one_or_none()


async def check_user_soft_deleted_by_email(
    db: AsyncSession, email: str
) -> Optional[User]:
    """
    Check if a user with the given email exists only in soft-deleted state
    Returns the soft-deleted user if found, None otherwise
    """
    result = await db.execute(
        select(User).where(
            and_(
                User.email == email,
                User.is_deleted == True
            )
        )
    )
    return result.scalar_one_or_none()


def generate_replacement_success_message(
    record_type: str, name: str, identifier_type: str, identifier_value: str
) -> str:
    """
    Generate a success message when creating a record that replaces a soft-deleted one
    
    Args:
        record_type: "Teacher" or "Student"
        name: Full name of the person
        identifier_type: "employee ID", "admission number", or "email"
        identifier_value: The actual identifier value
    
    Returns:
        Formatted success message
    """
    return (
        f"{record_type} {name} created successfully "
        f"(previous record with {identifier_type} {identifier_value} was archived)"
    )


async def validate_teacher_creation_with_soft_delete_check(
    db: AsyncSession, employee_id: str, email: Optional[str] = None
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate teacher creation considering soft-deleted records
    
    Returns:
        Tuple of (can_create, success_message, error_message)
        - can_create: True if creation is allowed
        - success_message: Message to show on successful creation (if replacing soft-deleted)
        - error_message: Error message if creation is not allowed
    """
    # Check for active records first (these should block creation)
    from app.crud.crud_teacher import teacher_crud
    
    existing_teacher = await teacher_crud.get_by_employee_id(db, employee_id=employee_id)
    if existing_teacher:
        return False, None, "Teacher with this employee ID already exists"
    
    if email:
        existing_email = await teacher_crud.get_by_email(db, email=email)
        if existing_email:
            return False, None, "Teacher with this email already exists"
    
    # Check for soft-deleted records to provide appropriate success message
    soft_deleted_teacher = await check_teacher_soft_deleted_by_employee_id(db, employee_id)
    if soft_deleted_teacher:
        success_msg = generate_replacement_success_message(
            "Teacher", 
            f"{soft_deleted_teacher.first_name} {soft_deleted_teacher.last_name}",
            "employee ID",
            employee_id
        )
        return True, success_msg, None
    
    if email:
        soft_deleted_email = await check_teacher_soft_deleted_by_email(db, email)
        if soft_deleted_email:
            success_msg = generate_replacement_success_message(
                "Teacher",
                f"{soft_deleted_email.first_name} {soft_deleted_email.last_name}",
                "email",
                email
            )
            return True, success_msg, None
    
    # No conflicts, normal creation
    return True, None, None


async def validate_student_creation_with_soft_delete_check(
    db: AsyncSession, admission_number: str, email: Optional[str] = None
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate student creation considering soft-deleted records
    
    Returns:
        Tuple of (can_create, success_message, error_message)
        - can_create: True if creation is allowed
        - success_message: Message to show on successful creation (if replacing soft-deleted)
        - error_message: Error message if creation is not allowed
    """
    # Check for active records first (these should block creation)
    from app.crud.crud_student import student_crud
    
    existing_student = await student_crud.get_by_admission_number(db, admission_number=admission_number)
    if existing_student:
        return False, None, "Student with this admission number already exists"
    
    if email:
        existing_email = await student_crud.get_by_email(db, email=email)
        if existing_email:
            return False, None, "Student with this email already exists"
    
    # Check for soft-deleted records to provide appropriate success message
    soft_deleted_student = await check_student_soft_deleted_by_admission_number(db, admission_number)
    if soft_deleted_student:
        success_msg = generate_replacement_success_message(
            "Student",
            f"{soft_deleted_student.first_name} {soft_deleted_student.last_name}",
            "admission number",
            admission_number
        )
        return True, success_msg, None
    
    if email:
        soft_deleted_email = await check_student_soft_deleted_by_email(db, email)
        if soft_deleted_email:
            success_msg = generate_replacement_success_message(
                "Student",
                f"{soft_deleted_email.first_name} {soft_deleted_email.last_name}",
                "email",
                email
            )
            return True, success_msg, None
    
    # No conflicts, normal creation
    return True, None, None
