"""
Helper functions to convert between human-readable identifiers and database IDs
Supports both composite identifiers and legacy formats for backward compatibility
"""

import re
from typing import Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.crud import student_crud, teacher_crud, user_crud
from app.schemas.leave import ApplicantTypeEnum


def parse_student_identifier(identifier: str) -> Dict[str, Any]:
    """
    Parse student identifier in various formats:
    - "Roll 001 - Class 5A" (new frontend format)
    - "Roll 001: John Doe" (preferred composite format)
    - "001 - John Doe" (alternative composite format)
    - "STU001" (legacy admission number)
    - "001" (roll number only)

    Returns:
        Dict with parsed components: {'type': 'frontend|composite|roll|admission', 'roll_number': str, 'name': str, 'class_name': str, 'admission_number': str}
    """
    identifier = identifier.strip()

    # Pattern 0: "Roll 001 - Class 5A" (new frontend format)
    pattern0 = re.match(r'^Roll\s*(\d+)\s*-\s*Class\s*(.+)$', identifier, re.IGNORECASE)
    if pattern0:
        return {
            'type': 'frontend',
            'roll_number': pattern0.group(1).zfill(3),  # Ensure 3 digits
            'class_name': pattern0.group(2).strip(),
            'name': None,
            'admission_number': None
        }

    # Pattern 1: "Roll 001: John Doe" or "Roll001: John Doe"
    pattern1 = re.match(r'^Roll\s*(\d+):\s*(.+)$', identifier, re.IGNORECASE)
    if pattern1:
        return {
            'type': 'composite',
            'roll_number': pattern1.group(1).zfill(3),  # Ensure 3 digits
            'name': pattern1.group(2).strip(),
            'class_name': None,
            'admission_number': None
        }

    # Pattern 2: "001 - John Doe" or "001-John Doe"
    pattern2 = re.match(r'^(\d+)\s*-\s*(.+)$', identifier)
    if pattern2:
        return {
            'type': 'composite',
            'roll_number': pattern2.group(1).zfill(3),  # Ensure 3 digits
            'name': pattern2.group(2).strip(),
            'class_name': None,
            'admission_number': None
        }

    # Pattern 3: Legacy admission number (e.g., "STU001")
    if re.match(r'^[A-Z]{2,4}\d+$', identifier, re.IGNORECASE):
        return {
            'type': 'admission',
            'roll_number': None,
            'name': None,
            'class_name': None,
            'admission_number': identifier.upper()
        }

    # Pattern 4: Roll number only (e.g., "001")
    if re.match(r'^\d+$', identifier):
        return {
            'type': 'roll',
            'roll_number': identifier.zfill(3),  # Ensure 3 digits
            'name': None,
            'class_name': None,
            'admission_number': None
        }

    # If no pattern matches, treat as name search
    return {
        'type': 'name',
        'roll_number': None,
        'name': identifier,
        'class_name': None,
        'admission_number': None
    }


def parse_teacher_identifier(identifier: str) -> Dict[str, Any]:
    """
    Parse teacher identifier in various formats:
    - "John Smith (EMP001)" (preferred composite format)
    - "John Smith - EMP001" (alternative composite format)
    - "EMP001" (legacy employee ID)

    Returns:
        Dict with parsed components: {'type': 'composite|employee|name', 'name': str, 'employee_id': str}
    """
    identifier = identifier.strip()

    # Pattern 1: "John Smith (EMP001)" or "John Smith(EMP001)"
    pattern1 = re.match(r'^(.+?)\s*\(([A-Z]{2,4}\d+)\)$', identifier, re.IGNORECASE)
    if pattern1:
        return {
            'type': 'composite',
            'name': pattern1.group(1).strip(),
            'employee_id': pattern1.group(2).upper()
        }

    # Pattern 2: "John Smith - EMP001" or "John Smith-EMP001"
    pattern2 = re.match(r'^(.+?)\s*-\s*([A-Z]{2,4}\d+)$', identifier, re.IGNORECASE)
    if pattern2:
        return {
            'type': 'composite',
            'name': pattern2.group(1).strip(),
            'employee_id': pattern2.group(2).upper()
        }

    # Pattern 3: Legacy employee ID (e.g., "EMP001")
    if re.match(r'^[A-Z]{2,4}\d+$', identifier, re.IGNORECASE):
        return {
            'type': 'employee',
            'name': None,
            'employee_id': identifier.upper()
        }

    # If no pattern matches, treat as name search
    return {
        'type': 'name',
        'name': identifier,
        'employee_id': None
    }


def format_student_identifier(student) -> str:
    """
    Format student information into the preferred composite identifier format

    Args:
        student: Student model instance

    Returns:
        Formatted identifier string: "Roll 001: John Doe"
    """
    roll_number = getattr(student, 'roll_number', '000') or '000'
    # Ensure roll number is properly formatted (3 digits)
    roll_formatted = str(roll_number).zfill(3)
    return f"Roll {roll_formatted}: {student.first_name} {student.last_name}"


def format_teacher_identifier(teacher) -> str:
    """
    Format teacher information into the preferred composite identifier format

    Args:
        teacher: Teacher model instance

    Returns:
        Formatted identifier string: "John Smith (EMP001)"
    """
    return f"{teacher.first_name} {teacher.last_name} ({teacher.employee_id})"


async def resolve_applicant_identifier(
    db: AsyncSession,
    identifier: str,
    applicant_type: ApplicantTypeEnum
) -> Tuple[int, str]:
    """
    Convert human-readable identifier to database ID and return applicant name
    Supports both composite identifiers and legacy formats

    Args:
        db: Database session
        identifier: Human-readable identifier in various formats
        applicant_type: Type of applicant (student or teacher)

    Returns:
        Tuple of (database_id, full_name)

    Raises:
        HTTPException: If identifier not found
    """
    if applicant_type == ApplicantTypeEnum.STUDENT:
        return await _resolve_student_identifier(db, identifier)
    elif applicant_type == ApplicantTypeEnum.TEACHER:
        return await _resolve_teacher_identifier(db, identifier)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid applicant type: {applicant_type}"
        )


async def _resolve_student_identifier(db: AsyncSession, identifier: str) -> Tuple[int, str]:
    """
    Resolve student identifier using various strategies
    """
    parsed = parse_student_identifier(identifier)

    if parsed['type'] == 'frontend':
        # New frontend format: "Roll 001 - Class 5A"
        student = await _find_student_by_roll_and_class(
            db, parsed['roll_number'], parsed['class_name']
        )
        if student:
            return student.id, f"{student.first_name} {student.last_name}"

    elif parsed['type'] == 'composite':
        # Search by roll number and name combination
        student = await _find_student_by_roll_and_name(
            db, parsed['roll_number'], parsed['name']
        )
        if student:
            return student.id, f"{student.first_name} {student.last_name}"

    elif parsed['type'] == 'admission':
        # Legacy admission number lookup
        student = await student_crud.get_by_admission_number(
            db, admission_number=parsed['admission_number']
        )
        if student:
            return student.id, f"{student.first_name} {student.last_name}"

    elif parsed['type'] == 'roll':
        # Roll number only lookup
        student = await _find_student_by_roll_number(db, parsed['roll_number'])
        if student:
            return student.id, f"{student.first_name} {student.last_name}"

    elif parsed['type'] == 'name':
        # Name-based search
        students = await student_crud.search_students(db, search_term=parsed['name'], limit=5)
        if len(students) == 1:
            student = students[0]
            return student.id, f"{student.first_name} {student.last_name}"
        elif len(students) > 1:
            # Multiple matches - provide helpful error
            names = [f"{s.first_name} {s.last_name} (Roll {s.roll_number})" for s in students[:3]]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Multiple students found for '{identifier}'. Please be more specific. Found: {', '.join(names)}"
            )

    # If we get here, no student was found
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Student not found for identifier '{identifier}'. Try formats like 'Roll 001 - Class 5A', 'Roll 001: John Doe' or 'STU001'"
    )


async def _resolve_teacher_identifier(db: AsyncSession, identifier: str) -> Tuple[int, str]:
    """
    Resolve teacher identifier using various strategies
    """
    parsed = parse_teacher_identifier(identifier)

    if parsed['type'] == 'composite':
        # Search by name and employee ID combination
        teacher = await _find_teacher_by_name_and_employee_id(
            db, parsed['name'], parsed['employee_id']
        )
        if teacher:
            return teacher.id, f"{teacher.first_name} {teacher.last_name}"

    elif parsed['type'] == 'employee':
        # Legacy employee ID lookup
        teacher = await teacher_crud.get_by_employee_id(
            db, employee_id=parsed['employee_id']
        )
        if teacher:
            return teacher.id, f"{teacher.first_name} {teacher.last_name}"

    elif parsed['type'] == 'name':
        # Name-based search
        teachers = await teacher_crud.search_teachers(db, search_term=parsed['name'], limit=5)
        if len(teachers) == 1:
            teacher = teachers[0]
            return teacher.id, f"{teacher.first_name} {teacher.last_name}"
        elif len(teachers) > 1:
            # Multiple matches - provide helpful error
            names = [f"{t.first_name} {t.last_name} ({t.employee_id})" for t in teachers[:3]]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Multiple teachers found for '{identifier}'. Please be more specific. Found: {', '.join(names)}"
            )

    # If we get here, no teacher was found
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Teacher not found for identifier '{identifier}'. Try formats like 'John Smith (EMP001)' or 'EMP001'"
    )


async def _find_student_by_roll_and_class(
    db: AsyncSession,
    roll_number: str,
    class_name: str
) -> Optional[any]:
    """Find student by roll number and class name combination (new frontend format)"""
    from sqlalchemy import and_, select, join
    from app.models.student import Student
    from app.models.metadata import Class

    # First, find the class by name
    class_result = await db.execute(
        select(Class).where(
            and_(
                Class.name.ilike(class_name),
                Class.is_active == True
            )
        )
    )
    class_obj = class_result.scalar_one_or_none()

    if not class_obj:
        # If exact class name not found, try partial match
        class_result = await db.execute(
            select(Class).where(
                and_(
                    Class.name.ilike(f"%{class_name}%"),
                    Class.is_active == True
                )
            )
        )
        class_obj = class_result.scalar_one_or_none()

    if not class_obj:
        return None

    # Now find student by roll number and class
    result = await db.execute(
        select(Student).where(
            and_(
                Student.roll_number == roll_number,
                Student.class_id == class_obj.id,
                Student.is_active == True
            )
        )
    )
    return result.scalar_one_or_none()


async def _find_student_by_roll_and_name(
    db: AsyncSession,
    roll_number: str,
    name: str
) -> Optional[any]:
    """Find student by roll number and name combination"""
    from sqlalchemy import and_, func, select
    from app.models.student import Student

    # Split name into parts for flexible matching
    name_parts = name.strip().split()
    if len(name_parts) >= 2:
        first_name = name_parts[0]
        last_name = ' '.join(name_parts[1:])

        # Try exact match first
        result = await db.execute(
            select(Student).where(
                and_(
                    Student.roll_number == roll_number,
                    Student.first_name.ilike(first_name),
                    Student.last_name.ilike(last_name),
                    Student.is_active == True
                )
            )
        )
        student = result.scalar_one_or_none()
        if student:
            return student

    # Try roll number with partial name match
    result = await db.execute(
        select(Student).where(
            and_(
                Student.roll_number == roll_number,
                func.concat(Student.first_name, ' ', Student.last_name).ilike(f"%{name}%"),
                Student.is_active == True
            )
        )
    )
    return result.scalar_one_or_none()


async def _find_student_by_roll_number(db: AsyncSession, roll_number: str) -> Optional[any]:
    """Find student by roll number only"""
    from sqlalchemy import and_, select
    from app.models.student import Student

    result = await db.execute(
        select(Student).where(
            and_(
                Student.roll_number == roll_number,
                Student.is_active == True
            )
        )
    )
    return result.scalar_one_or_none()


async def _find_teacher_by_name_and_employee_id(
    db: AsyncSession,
    name: str,
    employee_id: str
) -> Optional[any]:
    """Find teacher by name and employee ID combination"""
    from sqlalchemy import and_, func, select
    from app.models.teacher import Teacher

    # Split name into parts for flexible matching
    name_parts = name.strip().split()
    if len(name_parts) >= 2:
        first_name = name_parts[0]
        last_name = ' '.join(name_parts[1:])

        # Try exact match first
        result = await db.execute(
            select(Teacher).where(
                and_(
                    Teacher.employee_id == employee_id,
                    Teacher.first_name.ilike(first_name),
                    Teacher.last_name.ilike(last_name),
                    Teacher.is_active == True
                )
            )
        )
        teacher = result.scalar_one_or_none()
        if teacher:
            return teacher

    # Try employee ID with partial name match
    result = await db.execute(
        select(Teacher).where(
            and_(
                Teacher.employee_id == employee_id,
                func.concat(Teacher.first_name, ' ', Teacher.last_name).ilike(f"%{name}%"),
                Teacher.is_active == True
            )
        )
    )
    return result.scalar_one_or_none()


async def resolve_substitute_teacher_identifier(
    db: AsyncSession,
    identifier: Optional[str]
) -> Optional[int]:
    """
    Convert substitute teacher identifier to database ID
    Supports both composite identifiers and legacy formats

    Args:
        db: Database session
        identifier: Teacher identifier in various formats (optional)

    Returns:
        Database ID or None

    Raises:
        HTTPException: If identifier provided but not found
    """
    if not identifier:
        return None

    try:
        teacher_id, _ = await _resolve_teacher_identifier(db, identifier)
        return teacher_id
    except HTTPException as e:
        # Re-raise with more specific context for substitute teacher
        raise HTTPException(
            status_code=e.status_code,
            detail=f"Substitute teacher not found: {e.detail}"
        )


async def resolve_applied_to_identifier(
    db: AsyncSession, 
    identifier: Optional[str]
) -> Optional[int]:
    """
    Convert applied_to identifier to user database ID
    This could be extended to handle different types of identifiers
    
    Args:
        db: Database session
        identifier: User identifier (optional)
    
    Returns:
        User database ID or None
    
    Raises:
        HTTPException: If identifier provided but not found
    """
    if not identifier:
        return None
    
    # For now, assume it's an email address
    # This can be extended to handle employee IDs or other identifiers
    user = await user_crud.get_by_email(db, email=identifier)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with identifier '{identifier}' not found"
        )
    
    return user.id


async def get_applicant_display_info(
    db: AsyncSession,
    applicant_id: int,
    applicant_type: ApplicantTypeEnum
) -> dict:
    """
    Get display information for an applicant using the new composite format

    Args:
        db: Database session
        applicant_id: Database ID
        applicant_type: Type of applicant

    Returns:
        Dictionary with display information
    """
    if applicant_type == ApplicantTypeEnum.STUDENT:
        student = await student_crud.get(db, id=applicant_id)
        if not student:
            return {"identifier": "Unknown", "name": "Unknown Student", "details": ""}

        return {
            "identifier": format_student_identifier(student),
            "name": f"{student.first_name} {student.last_name}",
            "details": f"Class {getattr(student, 'current_class', 'N/A')} - {getattr(student, 'section', 'N/A')}",
            "legacy_identifier": getattr(student, 'admission_number', 'N/A')
        }

    elif applicant_type == ApplicantTypeEnum.TEACHER:
        teacher = await teacher_crud.get(db, id=applicant_id)
        if not teacher:
            return {"identifier": "Unknown", "name": "Unknown Teacher", "details": ""}

        return {
            "identifier": format_teacher_identifier(teacher),
            "name": f"{teacher.first_name} {teacher.last_name}",
            "details": f"{getattr(teacher, 'department', 'N/A')}",
            "legacy_identifier": teacher.employee_id
        }

    return {"identifier": "Unknown", "name": "Unknown", "details": ""}


def validate_identifier_format(identifier: str, applicant_type: ApplicantTypeEnum) -> bool:
    """
    Basic validation for identifier format
    
    Args:
        identifier: The identifier to validate
        applicant_type: Type of applicant
    
    Returns:
        True if format is valid
    """
    if not identifier or not identifier.strip():
        return False
    
    # Basic format validation - can be extended
    if applicant_type == ApplicantTypeEnum.STUDENT:
        # Student admission numbers are typically alphanumeric
        return len(identifier) >= 3 and identifier.replace('-', '').replace('_', '').isalnum()
    
    elif applicant_type == ApplicantTypeEnum.TEACHER:
        # Teacher employee IDs are typically alphanumeric
        return len(identifier) >= 3 and identifier.replace('-', '').replace('_', '').isalnum()
    
    return True
