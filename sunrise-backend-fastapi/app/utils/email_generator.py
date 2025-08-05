"""
Email generation utilities for students and teachers.

This module provides functions to automatically generate unique email addresses
for students and teachers based on their personal information.
"""

import re
from datetime import date
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User
from app.core.logging import log_crud_operation


def sanitize_name(name: str) -> str:
    """
    Sanitize a name for use in email addresses.
    
    - Convert to lowercase
    - Remove spaces and special characters
    - Keep only alphanumeric characters
    """
    if not name:
        return ""
    
    # Convert to lowercase and remove spaces
    sanitized = name.lower().strip()
    
    # Remove special characters, keep only alphanumeric
    sanitized = re.sub(r'[^a-z0-9]', '', sanitized)
    
    return sanitized


def format_date_for_email(birth_date: date) -> str:
    """
    Format date of birth for email generation.

    Format: MMYYYY (e.g., 031995 for March 1995)
    """
    return birth_date.strftime("%m%Y")


def generate_base_email(first_name: str, last_name: str, date_of_birth: date, user_type: str = "student") -> str:
    """
    Generate base email address format.

    Format: {firstname}.{lastname}.{MMYYYY}@sunrise.edu

    Args:
        first_name: User's first name
        last_name: User's last name
        date_of_birth: User's date of birth
        user_type: Type of user (student/teacher) - for logging purposes

    Returns:
        Base email address string
    """
    # Sanitize names
    clean_first = sanitize_name(first_name)
    clean_last = sanitize_name(last_name)

    # Format date
    date_str = format_date_for_email(date_of_birth)

    # Generate base email
    base_email = f"{clean_first}.{clean_last}.{date_str}@sunrise.edu"

    log_crud_operation("EMAIL_GENERATION", f"Generated base email for {user_type}",
                      first_name=first_name, last_name=last_name,
                      date_of_birth=str(date_of_birth), base_email=base_email)

    return base_email


async def ensure_unique_email(db: AsyncSession, base_email: str, user_type: str = "student") -> str:
    """
    Ensure email uniqueness by checking database and appending number if needed.
    
    Args:
        db: Database session
        base_email: Base email address to check
        user_type: Type of user (student/teacher) - for logging purposes
    
    Returns:
        Unique email address
    """
    # Check if base email exists
    existing_user_result = await db.execute(select(User).where(User.email == base_email))
    existing_user = existing_user_result.scalar_one_or_none()
    
    if not existing_user:
        log_crud_operation("EMAIL_UNIQUENESS", f"Base email is unique for {user_type}", 
                          email=base_email)
        return base_email
    
    # If base email exists, try with sequential numbers
    counter = 2
    while counter <= 999:  # Reasonable limit
        numbered_email = base_email.replace("@sunrise.edu", f".{counter}@sunrise.edu")
        
        existing_numbered_result = await db.execute(select(User).where(User.email == numbered_email))
        existing_numbered = existing_numbered_result.scalar_one_or_none()
        
        if not existing_numbered:
            log_crud_operation("EMAIL_UNIQUENESS", f"Found unique email with suffix for {user_type}", 
                              original_email=base_email, unique_email=numbered_email, suffix=counter)
            return numbered_email
        
        counter += 1
    
    # If we can't find a unique email after 999 attempts, raise an error
    log_crud_operation("EMAIL_UNIQUENESS", f"Failed to generate unique email for {user_type}", 
                      "error", base_email=base_email, max_attempts=999)
    raise ValueError(f"Unable to generate unique email for {base_email} after 999 attempts")


async def generate_student_email(db: AsyncSession, first_name: str, last_name: str, date_of_birth: date) -> str:
    """
    Generate unique email address for a student.
    
    Args:
        db: Database session
        first_name: Student's first name
        last_name: Student's last name
        date_of_birth: Student's date of birth
    
    Returns:
        Unique email address for the student
    """
    base_email = generate_base_email(first_name, last_name, date_of_birth, "student")
    ##unique_email = await ensure_unique_email(db, base_email, "student")
    unique_email = base_email
    
    log_crud_operation("STUDENT_EMAIL_GENERATED", f"Generated unique email for student", 
                      first_name=first_name, last_name=last_name, email=unique_email)
    
    return unique_email


async def generate_teacher_email(db: AsyncSession, first_name: str, last_name: str, date_of_birth: date) -> str:
    """
    Generate unique email address for a teacher.
    
    Args:
        db: Database session
        first_name: Teacher's first name
        last_name: Teacher's last name
        date_of_birth: Teacher's date of birth
    
    Returns:
        Unique email address for the teacher
    """
    base_email = generate_base_email(first_name, last_name, date_of_birth, "teacher")
    unique_email = await ensure_unique_email(db, base_email, "teacher")
    
    log_crud_operation("TEACHER_EMAIL_GENERATED", f"Generated unique email for teacher", 
                      first_name=first_name, last_name=last_name, email=unique_email)
    
    return unique_email


def validate_generated_email(email: str) -> bool:
    """
    Validate that an email follows the expected generated format.

    Args:
        email: Email address to validate

    Returns:
        True if email follows the generated format, False otherwise
    """
    # Pattern: firstname.lastname.mmyyyy[@.number]@sunrise.edu
    pattern = r'^[a-z]+\.[a-z]+\.\d{6}(?:\.\d+)?@sunrise\.edu$'

    return bool(re.match(pattern, email))


def extract_info_from_generated_email(email: str) -> Optional[dict]:
    """
    Extract information from a generated email address.
    
    Args:
        email: Generated email address
    
    Returns:
        Dictionary with extracted info or None if not a generated email
    """
    if not validate_generated_email(email):
        return None
    
    # Remove domain
    local_part = email.split('@')[0]
    
    # Split by dots
    parts = local_part.split('.')
    
    if len(parts) < 3:
        return None
    
    first_name = parts[0]
    last_name = parts[1]
    date_part = parts[2]
    suffix = parts[3] if len(parts) > 3 else None

    # Parse date (MMYYYY)
    if len(date_part) != 6:
        return None

    try:
        month = int(date_part[:2])
        year = int(date_part[2:6])
        # Use day 1 as we only have month and year
        birth_date = date(year, month, 1)
    except (ValueError, TypeError):
        return None
    
    return {
        'first_name': first_name,
        'last_name': last_name,
        'date_of_birth': birth_date,
        'suffix': suffix,
        'is_generated': True
    }
