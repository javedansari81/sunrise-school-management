"""
Backend Validation Layer

This module provides validation functions that check constraints before database operations
to catch errors proactively and provide better user experience.
"""

import re
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models import (
    User, Student, Teacher, FeeStructure, FeeRecord, LeaveRequest,
    Expense, Vendor, Budget
)
from app.crud.metadata import validate_metadata_ids
from .error_handler import ValidationErrorHandler


class BaseValidator:
    """Base validator with common validation methods"""
    
    @staticmethod
    def validate_email_format(email: str) -> bool:
        """Validate email format using regex"""
        if not email:
            return False
        
        pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone_format(phone: Optional[str]) -> bool:
        """Validate phone format"""
        if not phone:
            return True  # Phone is optional in most cases
        
        pattern = r'^[0-9+\-\s()]+$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_positive_amount(amount: Optional[Decimal]) -> bool:
        """Validate that amount is positive"""
        if amount is None:
            return True
        return amount > 0
    
    @staticmethod
    def validate_non_negative_amount(amount: Optional[Decimal]) -> bool:
        """Validate that amount is non-negative"""
        if amount is None:
            return True
        return amount >= 0
    
    @staticmethod
    def validate_date_not_future(date_value: Optional[date]) -> bool:
        """Validate that date is not in the future"""
        if not date_value:
            return True
        return date_value <= date.today()
    
    @staticmethod
    def validate_date_range(start_date: date, end_date: date) -> bool:
        """Validate that end date is not before start date"""
        return end_date >= start_date


class UserValidator(BaseValidator):
    """Validator for User model operations"""
    
    @staticmethod
    async def validate_unique_email(db: AsyncSession, email: str, exclude_id: Optional[int] = None) -> bool:
        """Check if email is unique"""
        query = select(User).where(User.email == email)
        if exclude_id:
            query = query.where(User.id != exclude_id)
        
        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()
        return existing_user is None
    
    @staticmethod
    async def validate_user_creation(db: AsyncSession, user_data: Dict[str, Any]) -> List[str]:
        """Validate user creation data"""
        errors = []
        
        # Validate email format
        if not BaseValidator.validate_email_format(user_data.get('email', '')):
            errors.append("Please enter a valid email address format (e.g., user@example.com).")
        
        # Validate unique email
        email = user_data.get('email')
        if email and not await UserValidator.validate_unique_email(db, email):
            errors.append("A user with this email address already exists. Please use a different email address.")
        
        # Validate user type
        user_type_id = user_data.get('user_type_id')
        if user_type_id and not await validate_metadata_ids(db, {'user_type_id': user_type_id}):
            errors.append("Invalid user type selected. Please select a valid user type.")
        
        return errors


class StudentValidator(BaseValidator):
    """Validator for Student model operations"""
    
    @staticmethod
    async def validate_unique_admission_number(
        db: AsyncSession, 
        admission_number: str, 
        session_year_id: int,
        exclude_id: Optional[int] = None
    ) -> bool:
        """Check if admission number is unique within session year"""
        query = select(Student).where(
            and_(
                Student.admission_number == admission_number,
                Student.session_year_id == session_year_id,
                Student.is_deleted == False
            )
        )
        if exclude_id:
            query = query.where(Student.id != exclude_id)
        
        result = await db.execute(query)
        existing_student = result.scalar_one_or_none()
        return existing_student is None
    
    @staticmethod
    async def validate_unique_user_id(db: AsyncSession, user_id: int, exclude_id: Optional[int] = None) -> bool:
        """Check if user_id is unique (not already linked to another student)"""
        query = select(Student).where(
            and_(
                Student.user_id == user_id,
                Student.is_deleted == False
            )
        )
        if exclude_id:
            query = query.where(Student.id != exclude_id)
        
        result = await db.execute(query)
        existing_student = result.scalar_one_or_none()
        return existing_student is None
    
    @staticmethod
    async def validate_student_creation(db: AsyncSession, student_data: Dict[str, Any]) -> List[str]:
        """Validate student creation data"""
        errors = []
        
        # Validate admission number uniqueness
        admission_number = student_data.get('admission_number')
        session_year_id = student_data.get('session_year_id')
        if admission_number and session_year_id:
            if not await StudentValidator.validate_unique_admission_number(db, admission_number, session_year_id):
                errors.append("A student with this admission number already exists for the selected session year. Please use a different admission number.")
        
        # Validate user_id uniqueness if provided
        user_id = student_data.get('user_id')
        if user_id and not await StudentValidator.validate_unique_user_id(db, user_id):
            errors.append("This user account is already linked to another student profile.")
        
        # Validate phone format
        phone = student_data.get('phone')
        if phone and not BaseValidator.validate_phone_format(phone):
            errors.append("Please enter a valid phone number using only numbers, spaces, parentheses, plus signs, and hyphens.")
        
        # Validate admission date
        admission_date = student_data.get('admission_date')
        if admission_date and not BaseValidator.validate_date_not_future(admission_date):
            errors.append("Admission date cannot be in the future. Please enter a valid admission date.")
        
        # Validate graduation date vs admission date
        graduation_date = student_data.get('graduation_date')
        if graduation_date and admission_date and graduation_date <= admission_date:
            errors.append("Graduation date must be after the admission date.")
        
        # Validate metadata IDs
        metadata_fields = {
            'gender_id': student_data.get('gender_id'),
            'class_id': student_data.get('class_id'),
            'session_year_id': student_data.get('session_year_id')
        }
        metadata_fields = {k: v for k, v in metadata_fields.items() if v is not None}
        
        if metadata_fields and not await validate_metadata_ids(db, metadata_fields):
            errors.append("Invalid selection made. Please select valid options from the available choices.")
        
        return errors


class TeacherValidator(BaseValidator):
    """Validator for Teacher model operations"""
    
    @staticmethod
    async def validate_unique_employee_id(db: AsyncSession, employee_id: str, exclude_id: Optional[int] = None) -> bool:
        """Check if employee ID is unique"""
        query = select(Teacher).where(
            and_(
                Teacher.employee_id == employee_id,
                Teacher.is_deleted == False
            )
        )
        if exclude_id:
            query = query.where(Teacher.id != exclude_id)
        
        result = await db.execute(query)
        existing_teacher = result.scalar_one_or_none()
        return existing_teacher is None
    
    @staticmethod
    async def validate_unique_email(db: AsyncSession, email: str, exclude_id: Optional[int] = None) -> bool:
        """Check if email is unique"""
        query = select(Teacher).where(
            and_(
                Teacher.email == email,
                Teacher.is_deleted == False
            )
        )
        if exclude_id:
            query = query.where(Teacher.id != exclude_id)
        
        result = await db.execute(query)
        existing_teacher = result.scalar_one_or_none()
        return existing_teacher is None
    
    @staticmethod
    async def validate_unique_user_id(db: AsyncSession, user_id: int, exclude_id: Optional[int] = None) -> bool:
        """Check if user_id is unique (not already linked to another teacher)"""
        query = select(Teacher).where(
            and_(
                Teacher.user_id == user_id,
                Teacher.is_deleted == False
            )
        )
        if exclude_id:
            query = query.where(Teacher.id != exclude_id)
        
        result = await db.execute(query)
        existing_teacher = result.scalar_one_or_none()
        return existing_teacher is None
    
    @staticmethod
    async def validate_teacher_creation(db: AsyncSession, teacher_data: Dict[str, Any]) -> List[str]:
        """Validate teacher creation data"""
        errors = []
        
        # Validate employee ID uniqueness
        employee_id = teacher_data.get('employee_id')
        if employee_id and not await TeacherValidator.validate_unique_employee_id(db, employee_id):
            errors.append("A teacher with this employee ID already exists. Please use a different employee ID.")
        
        # Validate email uniqueness
        email = teacher_data.get('email')
        if email:
            if not BaseValidator.validate_email_format(email):
                errors.append("Please enter a valid email address format (e.g., user@example.com).")
            elif not await TeacherValidator.validate_unique_email(db, email):
                errors.append("A teacher with this email address already exists. Please use a different email address.")
        
        # Validate user_id uniqueness if provided
        user_id = teacher_data.get('user_id')
        if user_id and not await TeacherValidator.validate_unique_user_id(db, user_id):
            errors.append("This user account is already linked to another teacher profile.")
        
        # Validate joining date
        joining_date = teacher_data.get('joining_date')
        if joining_date and not BaseValidator.validate_date_not_future(joining_date):
            errors.append("Joining date cannot be in the future. Please enter a valid joining date.")
        
        # Validate resignation date vs joining date
        resignation_date = teacher_data.get('resignation_date')
        if resignation_date and joining_date and resignation_date <= joining_date:
            errors.append("Resignation date must be after the joining date.")
        
        # Validate salary
        salary = teacher_data.get('salary')
        if salary is not None and not BaseValidator.validate_positive_amount(salary):
            errors.append("Salary must be greater than zero. Please enter a valid salary amount.")
        
        # Validate experience years
        experience_years = teacher_data.get('experience_years')
        if experience_years is not None and experience_years < 0:
            errors.append("Experience years cannot be negative. Please enter a valid number of years.")
        
        # Validate metadata IDs
        metadata_fields = {
            'gender_id': teacher_data.get('gender_id'),
            'qualification_id': teacher_data.get('qualification_id'),
            'employment_status_id': teacher_data.get('employment_status_id'),
            'class_teacher_of_id': teacher_data.get('class_teacher_of_id')
        }
        metadata_fields = {k: v for k, v in metadata_fields.items() if v is not None}
        
        if metadata_fields and not await validate_metadata_ids(db, metadata_fields):
            errors.append("Invalid selection made. Please select valid options from the available choices.")
        
        return errors


class LeaveValidator(BaseValidator):
    """Validator for Leave-related model operations"""

    @staticmethod
    async def validate_leave_request_creation(db: AsyncSession, leave_data: Dict[str, Any]) -> List[str]:
        """Validate leave request creation data"""
        errors = []

        # Validate applicant type
        applicant_type = leave_data.get('applicant_type')
        if applicant_type and applicant_type not in ['student', 'teacher']:
            errors.append("Applicant type must be either 'student' or 'teacher'.")

        # Validate date range
        start_date = leave_data.get('start_date')
        end_date = leave_data.get('end_date')
        if start_date and end_date:
            if not BaseValidator.validate_date_range(start_date, end_date):
                errors.append("Leave end date must be on or after the start date.")

        # Validate total days
        total_days = leave_data.get('total_days')
        if total_days is not None and total_days <= 0:
            errors.append("Total leave days must be greater than zero.")

        # Validate half day session
        half_day_session = leave_data.get('half_day_session')
        if half_day_session and half_day_session not in ['morning', 'afternoon']:
            errors.append("Half day session must be either 'morning' or 'afternoon'.")

        # Validate metadata IDs
        metadata_fields = {
            'leave_type_id': leave_data.get('leave_type_id'),
            'leave_status_id': leave_data.get('leave_status_id')
        }
        metadata_fields = {k: v for k, v in metadata_fields.items() if v is not None}

        if metadata_fields and not await validate_metadata_ids(db, metadata_fields):
            errors.append("Invalid selection made. Please select valid options from the available choices.")

        return errors


class ExpenseValidator(BaseValidator):
    """Validator for Expense-related model operations"""

    @staticmethod
    async def validate_unique_vendor_name(db: AsyncSession, vendor_name: str, exclude_id: Optional[int] = None) -> bool:
        """Check if vendor name is unique"""
        query = select(Vendor).where(Vendor.vendor_name == vendor_name)
        if exclude_id:
            query = query.where(Vendor.id != exclude_id)

        result = await db.execute(query)
        existing_vendor = result.scalar_one_or_none()
        return existing_vendor is None

    @staticmethod
    async def validate_unique_vendor_code(db: AsyncSession, vendor_code: str, exclude_id: Optional[int] = None) -> bool:
        """Check if vendor code is unique"""
        query = select(Vendor).where(Vendor.vendor_code == vendor_code)
        if exclude_id:
            query = query.where(Vendor.id != exclude_id)

        result = await db.execute(query)
        existing_vendor = result.scalar_one_or_none()
        return existing_vendor is None

    # Note: PurchaseOrder model not available, removing PO validation for now

    @staticmethod
    async def validate_expense_creation(db: AsyncSession, expense_data: Dict[str, Any]) -> List[str]:
        """Validate expense creation data"""
        errors = []

        # Validate expense date
        expense_date = expense_data.get('expense_date')
        if expense_date and expense_date < date(2020, 1, 1):
            errors.append("Expense date must be a valid date (not before year 2020).")

        # Validate amounts
        amount = expense_data.get('amount')
        if amount is not None and not BaseValidator.validate_positive_amount(amount):
            errors.append("Expense amount must be greater than zero. Please enter a valid amount.")

        tax_amount = expense_data.get('tax_amount')
        if tax_amount is not None and not BaseValidator.validate_non_negative_amount(tax_amount):
            errors.append("Tax amount cannot be negative. Please enter a valid tax amount.")

        total_amount = expense_data.get('total_amount')
        if total_amount is not None and not BaseValidator.validate_positive_amount(total_amount):
            errors.append("Total expense amount must be greater than zero. Please enter a valid amount.")

        # Validate payment date vs expense date
        payment_date = expense_data.get('payment_date')
        if payment_date and expense_date and payment_date < expense_date:
            errors.append("Payment date must be on or after the expense date.")

        # Validate priority
        priority = expense_data.get('priority')
        if priority and priority not in ['Low', 'Medium', 'High', 'Urgent']:
            errors.append("Priority must be one of: Low, Medium, High, Urgent.")

        # Validate recurring frequency
        recurring_frequency = expense_data.get('recurring_frequency')
        if recurring_frequency and recurring_frequency not in ['Monthly', 'Quarterly', 'Half Yearly', 'Yearly']:
            errors.append("Recurring frequency must be one of: Monthly, Quarterly, Half Yearly, Yearly.")

        # Validate metadata IDs
        metadata_fields = {
            'expense_category_id': expense_data.get('expense_category_id'),
            'payment_method_id': expense_data.get('payment_method_id'),
            'payment_status_id': expense_data.get('payment_status_id'),
            'expense_status_id': expense_data.get('expense_status_id'),
            'session_year_id': expense_data.get('session_year_id')
        }
        metadata_fields = {k: v for k, v in metadata_fields.items() if v is not None}

        if metadata_fields and not await validate_metadata_ids(db, metadata_fields):
            errors.append("Invalid selection made. Please select valid options from the available choices.")

        return errors

    @staticmethod
    async def validate_vendor_creation(db: AsyncSession, vendor_data: Dict[str, Any]) -> List[str]:
        """Validate vendor creation data"""
        errors = []

        # Validate vendor name uniqueness
        vendor_name = vendor_data.get('vendor_name')
        if vendor_name and not await ExpenseValidator.validate_unique_vendor_name(db, vendor_name):
            errors.append("A vendor with this name already exists. Please use a different vendor name.")

        # Validate vendor code uniqueness
        vendor_code = vendor_data.get('vendor_code')
        if vendor_code and not await ExpenseValidator.validate_unique_vendor_code(db, vendor_code):
            errors.append("A vendor with this code already exists. Please use a different vendor code.")

        # Validate email format
        email = vendor_data.get('email')
        if email and not BaseValidator.validate_email_format(email):
            errors.append("Please enter a valid email address format (e.g., vendor@example.com).")

        # Validate rating
        rating = vendor_data.get('rating')
        if rating is not None and (rating < 0 or rating > 5):
            errors.append("Vendor rating must be between 0 and 5. Please enter a valid rating.")

        return errors

    # Note: Purchase order validation removed as PurchaseOrder model is not available


class BudgetValidator(BaseValidator):
    """Validator for Budget-related model operations"""

    @staticmethod
    async def validate_unique_budget(
        db: AsyncSession,
        session_year_id: int,
        expense_category_id: int,
        exclude_id: Optional[int] = None
    ) -> bool:
        """Check if budget is unique for session year and expense category"""
        query = select(Budget).where(
            and_(
                Budget.session_year_id == session_year_id,
                Budget.expense_category_id == expense_category_id
            )
        )
        if exclude_id:
            query = query.where(Budget.id != exclude_id)

        result = await db.execute(query)
        existing_budget = result.scalar_one_or_none()
        return existing_budget is None

    @staticmethod
    async def validate_budget_creation(db: AsyncSession, budget_data: Dict[str, Any]) -> List[str]:
        """Validate budget creation data"""
        errors = []

        # Validate uniqueness
        session_year_id = budget_data.get('session_year_id')
        expense_category_id = budget_data.get('expense_category_id')
        if session_year_id and expense_category_id:
            if not await BudgetValidator.validate_unique_budget(db, session_year_id, expense_category_id):
                errors.append("A budget already exists for this category and session year. Please edit the existing budget instead.")

        # Validate amounts
        allocated_amount = budget_data.get('allocated_amount')
        if allocated_amount is not None and not BaseValidator.validate_positive_amount(allocated_amount):
            errors.append("Allocated budget amount must be greater than zero. Please enter a valid amount.")

        spent_amount = budget_data.get('spent_amount')
        if spent_amount is not None and not BaseValidator.validate_non_negative_amount(spent_amount):
            errors.append("Spent amount cannot be negative. Please enter a valid amount.")

        remaining_amount = budget_data.get('remaining_amount')
        if remaining_amount is not None and not BaseValidator.validate_non_negative_amount(remaining_amount):
            errors.append("Remaining amount cannot be negative. Please check the budget calculations.")

        # Validate metadata IDs
        metadata_fields = {
            'session_year_id': budget_data.get('session_year_id'),
            'expense_category_id': budget_data.get('expense_category_id')
        }
        metadata_fields = {k: v for k, v in metadata_fields.items() if v is not None}

        if metadata_fields and not await validate_metadata_ids(db, metadata_fields):
            errors.append("Invalid selection made. Please select valid options from the available choices.")

        return errors


# Convenience functions for validation
async def validate_and_raise_errors(errors: List[str], operation: str = "operation"):
    """Raise validation errors if any exist"""
    if errors:
        # Combine all errors into a single message
        combined_message = " ".join(errors)
        ValidationErrorHandler.raise_validation_exception(
            message=combined_message,
            field_name="validation",
            error_code="VALIDATION_FAILED"
        )


class FeeValidator(BaseValidator):
    """Validator for Fee-related model operations"""
    
    @staticmethod
    async def validate_unique_fee_structure(
        db: AsyncSession, 
        class_id: int, 
        session_year_id: int,
        exclude_id: Optional[int] = None
    ) -> bool:
        """Check if fee structure is unique for class and session"""
        query = select(FeeStructure).where(
            and_(
                FeeStructure.class_id == class_id,
                FeeStructure.session_year_id == session_year_id
            )
        )
        if exclude_id:
            query = query.where(FeeStructure.id != exclude_id)
        
        result = await db.execute(query)
        existing_structure = result.scalar_one_or_none()
        return existing_structure is None
    
    @staticmethod
    async def validate_fee_structure_creation(db: AsyncSession, fee_data: Dict[str, Any]) -> List[str]:
        """Validate fee structure creation data"""
        errors = []
        
        # Validate uniqueness
        class_id = fee_data.get('class_id')
        session_year_id = fee_data.get('session_year_id')
        if class_id and session_year_id:
            if not await FeeValidator.validate_unique_fee_structure(db, class_id, session_year_id):
                errors.append("A fee structure already exists for this class and session year. Please edit the existing fee structure instead.")
        
        # Validate amounts
        total_annual_fee = fee_data.get('total_annual_fee')
        if total_annual_fee is not None and not BaseValidator.validate_positive_amount(total_annual_fee):
            errors.append("Total annual fee must be greater than zero. Please enter a valid amount.")
        
        # Validate individual fee components
        fee_components = [
            'tuition_fee', 'admission_fee', 'development_fee', 'activity_fee',
            'transport_fee', 'library_fee', 'lab_fee', 'exam_fee', 'other_fee'
        ]
        
        for component in fee_components:
            amount = fee_data.get(component)
            if amount is not None and not BaseValidator.validate_non_negative_amount(amount):
                errors.append(f"{component.replace('_', ' ').title()} cannot be negative. Please enter a valid amount.")
        
        # Validate metadata IDs
        metadata_fields = {
            'class_id': fee_data.get('class_id'),
            'session_year_id': fee_data.get('session_year_id')
        }
        metadata_fields = {k: v for k, v in metadata_fields.items() if v is not None}
        
        if metadata_fields and not await validate_metadata_ids(db, metadata_fields):
            errors.append("Invalid selection made. Please select valid options from the available choices.")
        
        return errors
    
    @staticmethod
    async def validate_fee_record_creation(db: AsyncSession, fee_data: Dict[str, Any]) -> List[str]:
        """Validate fee record creation data"""
        errors = []
        
        # Validate amounts
        total_amount = fee_data.get('total_amount')
        if total_amount is not None and not BaseValidator.validate_positive_amount(total_amount):
            errors.append("Total fee amount must be greater than zero. Please enter a valid amount.")
        
        paid_amount = fee_data.get('paid_amount')
        if paid_amount is not None and not BaseValidator.validate_non_negative_amount(paid_amount):
            errors.append("Paid amount cannot be negative. Please enter a valid amount.")
        
        balance_amount = fee_data.get('balance_amount')
        if balance_amount is not None and not BaseValidator.validate_non_negative_amount(balance_amount):
            errors.append("Balance amount cannot be negative. Please check the payment calculations.")
        
        # Validate balance calculation
        if all(x is not None for x in [total_amount, paid_amount, balance_amount]):
            if balance_amount != (total_amount - paid_amount):
                errors.append("Balance amount must equal total amount minus paid amount. Please check the calculations.")
        
        # Validate due date
        due_date = fee_data.get('due_date')
        if due_date and due_date < date(2020, 1, 1):
            errors.append("Due date must be a valid date (not before year 2020).")
        
        # Validate metadata IDs
        metadata_fields = {
            'student_id': fee_data.get('student_id'),
            'session_year_id': fee_data.get('session_year_id'),
            'payment_type_id': fee_data.get('payment_type_id'),
            'payment_status_id': fee_data.get('payment_status_id'),
            'payment_method_id': fee_data.get('payment_method_id')
        }
        metadata_fields = {k: v for k, v in metadata_fields.items() if v is not None}
        
        if metadata_fields and not await validate_metadata_ids(db, metadata_fields):
            errors.append("Invalid selection made. Please select valid options from the available choices.")
        
        return errors
