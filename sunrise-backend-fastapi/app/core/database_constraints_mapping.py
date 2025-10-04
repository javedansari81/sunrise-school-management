"""
Database Constraints Mapping and Validation Rules

This module contains a comprehensive mapping of all database constraints
and their corresponding validation rules and user-friendly error messages.
"""

from typing import Dict, List, Any
from enum import Enum


class ConstraintType(Enum):
    UNIQUE = "unique"
    FOREIGN_KEY = "foreign_key"
    CHECK = "check"
    NOT_NULL = "not_null"


class DatabaseConstraints:
    """
    Comprehensive mapping of database constraints to user-friendly error messages
    """
    
    # =====================================================
    # UNIQUE CONSTRAINTS MAPPING
    # =====================================================
    
    UNIQUE_CONSTRAINTS = {
        # Users table
        "users_email_key": {
            "table": "users",
            "columns": ["email"],
            "message": "A user with this email address already exists. Please use a different email address.",
            "field_name": "email"
        },
        
        # Students table
        "students_admission_number_key": {
            "table": "students",
            "columns": ["admission_number"],
            "message": "A student with this admission number already exists. Please use a different admission number.",
            "field_name": "admission_number"
        },
        "uk_students_admission_session": {
            "table": "students",
            "columns": ["admission_number", "session_year_id"],
            "message": "A student with this admission number already exists for the selected session year. Please use a different admission number.",
            "field_name": "admission_number"
        },
        "students_user_id_key": {
            "table": "students",
            "columns": ["user_id"],
            "message": "This user account is already linked to another student profile.",
            "field_name": "user_id"
        },
        
        # Teachers table
        "teachers_employee_id_key": {
            "table": "teachers",
            "columns": ["employee_id"],
            "message": "A teacher with this employee ID already exists. Please use a different employee ID.",
            "field_name": "employee_id"
        },
        "uk_teachers_employee_id": {
            "table": "teachers",
            "columns": ["employee_id"],
            "message": "A teacher with this employee ID already exists. Please use a different employee ID.",
            "field_name": "employee_id"
        },
        "teachers_email_key": {
            "table": "teachers",
            "columns": ["email"],
            "message": "A teacher with this email address already exists. Please use a different email address.",
            "field_name": "email"
        },
        "teachers_user_id_key": {
            "table": "teachers",
            "columns": ["user_id"],
            "message": "This user account is already linked to another teacher profile.",
            "field_name": "user_id"
        },
        
        # Fee Structures table
        "uk_fee_structures_class_session": {
            "table": "fee_structures",
            "columns": ["class_id", "session_year_id"],
            "message": "A fee structure already exists for this class and session year. Please edit the existing fee structure instead.",
            "field_name": "class_session"
        },
        "fee_structures_class_id_session_year_id_key": {
            "table": "fee_structures",
            "columns": ["class_id", "session_year_id"],
            "message": "A fee structure already exists for this class and session year. Please edit the existing fee structure instead.",
            "field_name": "class_session"
        },
        
        # Fee Payments table
        "fee_payments_receipt_number_key": {
            "table": "fee_payments",
            "columns": ["receipt_number"],
            "message": "A payment with this receipt number already exists. Please use a different receipt number.",
            "field_name": "receipt_number"
        },
        
        # Monthly Fee Tracking table
        "monthly_fee_tracking_fee_record_id_academic_month_academic_year_key": {
            "table": "monthly_fee_tracking",
            "columns": ["fee_record_id", "academic_month", "academic_year"],
            "message": "Monthly fee tracking already exists for this month and year. Cannot create duplicate monthly records.",
            "field_name": "monthly_tracking"
        },
        
        # Monthly Payment Allocations table
        "monthly_payment_allocations_fee_payment_id_monthly_tracking_id_key": {
            "table": "monthly_payment_allocations",
            "columns": ["fee_payment_id", "monthly_tracking_id"],
            "message": "This payment has already been allocated to this month. Cannot allocate the same payment twice.",
            "field_name": "payment_allocation"
        },
        
        # Leave Balance table
        "leave_balance_teacher_id_session_year_id_key": {
            "table": "leave_balance",
            "columns": ["teacher_id", "session_year_id"],
            "message": "Leave balance already exists for this teacher and session year.",
            "field_name": "teacher_session"
        },
        
        # Vendors table
        "vendors_vendor_name_key": {
            "table": "vendors",
            "columns": ["vendor_name"],
            "message": "A vendor with this name already exists. Please use a different vendor name.",
            "field_name": "vendor_name"
        },
        "vendors_vendor_code_key": {
            "table": "vendors",
            "columns": ["vendor_code"],
            "message": "A vendor with this code already exists. Please use a different vendor code.",
            "field_name": "vendor_code"
        },
        
        # Purchase Orders table
        "purchase_orders_po_number_key": {
            "table": "purchase_orders",
            "columns": ["po_number"],
            "message": "A purchase order with this number already exists. Please use a different PO number.",
            "field_name": "po_number"
        },
        
        # Budgets table
        "budgets_session_year_id_expense_category_id_key": {
            "table": "budgets",
            "columns": ["session_year_id", "expense_category_id"],
            "message": "A budget already exists for this category and session year. Please edit the existing budget instead.",
            "field_name": "budget_category_session"
        }
    }
    
    # =====================================================
    # FOREIGN KEY CONSTRAINTS MAPPING
    # =====================================================
    
    FOREIGN_KEY_CONSTRAINTS = {
        # Users table
        "users_user_type_id_fkey": {
            "table": "users",
            "column": "user_type_id",
            "referenced_table": "user_types",
            "message": "Invalid user type selected. Please select a valid user type.",
            "field_name": "user_type_id"
        },
        
        # Students table
        "students_user_id_fkey": {
            "table": "students",
            "column": "user_id",
            "referenced_table": "users",
            "message": "Invalid user account selected. Please select a valid user account.",
            "field_name": "user_id"
        },
        "students_gender_id_fkey": {
            "table": "students",
            "column": "gender_id",
            "referenced_table": "genders",
            "message": "Invalid gender selected. Please select a valid gender option.",
            "field_name": "gender_id"
        },
        "students_class_id_fkey": {
            "table": "students",
            "column": "class_id",
            "referenced_table": "classes",
            "message": "Invalid class selected. Please select a valid class.",
            "field_name": "class_id"
        },
        "students_session_year_id_fkey": {
            "table": "students",
            "column": "session_year_id",
            "referenced_table": "session_years",
            "message": "Invalid session year selected. Please select a valid session year.",
            "field_name": "session_year_id"
        },
        
        # Teachers table
        "teachers_user_id_fkey": {
            "table": "teachers",
            "column": "user_id",
            "referenced_table": "users",
            "message": "Invalid user account selected. Please select a valid user account.",
            "field_name": "user_id"
        },
        "teachers_gender_id_fkey": {
            "table": "teachers",
            "column": "gender_id",
            "referenced_table": "genders",
            "message": "Invalid gender selected. Please select a valid gender option.",
            "field_name": "gender_id"
        },
        "teachers_qualification_id_fkey": {
            "table": "teachers",
            "column": "qualification_id",
            "referenced_table": "qualifications",
            "message": "Invalid qualification selected. Please select a valid qualification.",
            "field_name": "qualification_id"
        },
        "teachers_employment_status_id_fkey": {
            "table": "teachers",
            "column": "employment_status_id",
            "referenced_table": "employment_statuses",
            "message": "Invalid employment status selected. Please select a valid employment status.",
            "field_name": "employment_status_id"
        },
        "teachers_class_teacher_of_id_fkey": {
            "table": "teachers",
            "column": "class_teacher_of_id",
            "referenced_table": "classes",
            "message": "Invalid class selected for class teacher assignment. Please select a valid class.",
            "field_name": "class_teacher_of_id"
        },
        
        # Fee Structures table
        "fee_structures_class_id_fkey": {
            "table": "fee_structures",
            "column": "class_id",
            "referenced_table": "classes",
            "message": "Invalid class selected. Please select a valid class.",
            "field_name": "class_id"
        },
        "fee_structures_session_year_id_fkey": {
            "table": "fee_structures",
            "column": "session_year_id",
            "referenced_table": "session_years",
            "message": "Invalid session year selected. Please select a valid session year.",
            "field_name": "session_year_id"
        },
        
        # Fee Records table
        "fee_records_student_id_fkey": {
            "table": "fee_records",
            "column": "student_id",
            "referenced_table": "students",
            "message": "Invalid student selected. Please select a valid student.",
            "field_name": "student_id"
        },
        "fee_records_session_year_id_fkey": {
            "table": "fee_records",
            "column": "session_year_id",
            "referenced_table": "session_years",
            "message": "Invalid session year selected. Please select a valid session year.",
            "field_name": "session_year_id"
        },
        "fee_records_payment_type_id_fkey": {
            "table": "fee_records",
            "column": "payment_type_id",
            "referenced_table": "payment_types",
            "message": "Invalid payment type selected. Please select a valid payment type.",
            "field_name": "payment_type_id"
        },
        "fee_records_payment_status_id_fkey": {
            "table": "fee_records",
            "column": "payment_status_id",
            "referenced_table": "payment_statuses",
            "message": "Invalid payment status selected. Please select a valid payment status.",
            "field_name": "payment_status_id"
        },
        "fee_records_payment_method_id_fkey": {
            "table": "fee_records",
            "column": "payment_method_id",
            "referenced_table": "payment_methods",
            "message": "Invalid payment method selected. Please select a valid payment method.",
            "field_name": "payment_method_id"
        },
        "fee_records_fee_structure_id_fkey": {
            "table": "fee_records",
            "column": "fee_structure_id",
            "referenced_table": "fee_structures",
            "message": "Invalid fee structure selected. Please select a valid fee structure.",
            "field_name": "fee_structure_id"
        },

        # Fee Payments table
        "fee_payments_fee_record_id_fkey": {
            "table": "fee_payments",
            "column": "fee_record_id",
            "referenced_table": "fee_records",
            "message": "Invalid fee record selected. Please select a valid fee record.",
            "field_name": "fee_record_id"
        },
        "fee_payments_payment_method_id_fkey": {
            "table": "fee_payments",
            "column": "payment_method_id",
            "referenced_table": "payment_methods",
            "message": "Invalid payment method selected. Please select a valid payment method.",
            "field_name": "payment_method_id"
        },
        "fk_fee_payments_collected_by": {
            "table": "fee_payments",
            "column": "collected_by",
            "referenced_table": "users",
            "message": "Invalid user selected for payment collection. Please select a valid user.",
            "field_name": "collected_by"
        },

        # Leave Requests table
        "leave_requests_leave_type_id_fkey": {
            "table": "leave_requests",
            "column": "leave_type_id",
            "referenced_table": "leave_types",
            "message": "Invalid leave type selected. Please select a valid leave type.",
            "field_name": "leave_type_id"
        },
        "leave_requests_leave_status_id_fkey": {
            "table": "leave_requests",
            "column": "leave_status_id",
            "referenced_table": "leave_statuses",
            "message": "Invalid leave status selected. Please select a valid leave status.",
            "field_name": "leave_status_id"
        },
        "fk_leave_requests_applied_to": {
            "table": "leave_requests",
            "column": "applied_to",
            "referenced_table": "users",
            "message": "Invalid approver selected. Please select a valid approver.",
            "field_name": "applied_to"
        },
        "fk_leave_requests_reviewed_by": {
            "table": "leave_requests",
            "column": "reviewed_by",
            "referenced_table": "users",
            "message": "Invalid reviewer selected. Please select a valid reviewer.",
            "field_name": "reviewed_by"
        },
        "fk_leave_requests_substitute": {
            "table": "leave_requests",
            "column": "substitute_teacher_id",
            "referenced_table": "teachers",
            "message": "Invalid substitute teacher selected. Please select a valid teacher.",
            "field_name": "substitute_teacher_id"
        },

        # Leave Balance table
        "leave_balance_teacher_id_fkey": {
            "table": "leave_balance",
            "column": "teacher_id",
            "referenced_table": "teachers",
            "message": "Invalid teacher selected. Please select a valid teacher.",
            "field_name": "teacher_id"
        },
        "leave_balance_session_year_id_fkey": {
            "table": "leave_balance",
            "column": "session_year_id",
            "referenced_table": "session_years",
            "message": "Invalid session year selected. Please select a valid session year.",
            "field_name": "session_year_id"
        },

        # Expenses table
        "expenses_expense_category_id_fkey": {
            "table": "expenses",
            "column": "expense_category_id",
            "referenced_table": "expense_categories",
            "message": "Invalid expense category selected. Please select a valid expense category.",
            "field_name": "expense_category_id"
        },
        "expenses_payment_method_id_fkey": {
            "table": "expenses",
            "column": "payment_method_id",
            "referenced_table": "payment_methods",
            "message": "Invalid payment method selected. Please select a valid payment method.",
            "field_name": "payment_method_id"
        },
        "expenses_payment_status_id_fkey": {
            "table": "expenses",
            "column": "payment_status_id",
            "referenced_table": "payment_statuses",
            "message": "Invalid payment status selected. Please select a valid payment status.",
            "field_name": "payment_status_id"
        },
        "expenses_expense_status_id_fkey": {
            "table": "expenses",
            "column": "expense_status_id",
            "referenced_table": "expense_statuses",
            "message": "Invalid expense status selected. Please select a valid expense status.",
            "field_name": "expense_status_id"
        },
        "fk_expenses_requested_by": {
            "table": "expenses",
            "column": "requested_by",
            "referenced_table": "users",
            "message": "Invalid user selected for expense request. Please select a valid user.",
            "field_name": "requested_by"
        },
        "fk_expenses_approved_by": {
            "table": "expenses",
            "column": "approved_by",
            "referenced_table": "users",
            "message": "Invalid user selected for expense approval. Please select a valid user.",
            "field_name": "approved_by"
        },
        "expenses_session_year_id_fkey": {
            "table": "expenses",
            "column": "session_year_id",
            "referenced_table": "session_years",
            "message": "Invalid session year selected. Please select a valid session year.",
            "field_name": "session_year_id"
        },

        # Purchase Orders table
        "purchase_orders_vendor_id_fkey": {
            "table": "purchase_orders",
            "column": "vendor_id",
            "referenced_table": "vendors",
            "message": "Invalid vendor selected. Please select a valid vendor.",
            "field_name": "vendor_id"
        },
        "fk_purchase_orders_created_by": {
            "table": "purchase_orders",
            "column": "created_by",
            "referenced_table": "users",
            "message": "Invalid user selected for purchase order creation. Please select a valid user.",
            "field_name": "created_by"
        },
        "fk_purchase_orders_approved_by": {
            "table": "purchase_orders",
            "column": "approved_by",
            "referenced_table": "users",
            "message": "Invalid user selected for purchase order approval. Please select a valid user.",
            "field_name": "approved_by"
        },

        # Budgets table
        "budgets_session_year_id_fkey": {
            "table": "budgets",
            "column": "session_year_id",
            "referenced_table": "session_years",
            "message": "Invalid session year selected. Please select a valid session year.",
            "field_name": "session_year_id"
        },
        "budgets_expense_category_id_fkey": {
            "table": "budgets",
            "column": "expense_category_id",
            "referenced_table": "expense_categories",
            "message": "Invalid expense category selected. Please select a valid expense category.",
            "field_name": "expense_category_id"
        }
    }

    # =====================================================
    # CHECK CONSTRAINTS MAPPING
    # =====================================================

    CHECK_CONSTRAINTS = {
        # Users table
        "chk_users_email_format": {
            "table": "users",
            "columns": ["email"],
            "message": "Please enter a valid email address format (e.g., user@example.com).",
            "field_name": "email"
        },

        # Students table
        "students_phone_check": {
            "table": "students",
            "columns": ["phone"],
            "message": "Please enter a valid phone number using only numbers, spaces, parentheses, plus signs, and hyphens.",
            "field_name": "phone"
        },
        "students_admission_date_check": {
            "table": "students",
            "columns": ["admission_date"],
            "message": "Admission date cannot be in the future. Please enter a valid admission date.",
            "field_name": "admission_date"
        },
        "students_graduation_date_check": {
            "table": "students",
            "columns": ["graduation_date"],
            "message": "Graduation date must be after the admission date.",
            "field_name": "graduation_date"
        },

        # Teachers table
        "teachers_experience_years_check": {
            "table": "teachers",
            "columns": ["experience_years"],
            "message": "Experience years cannot be negative. Please enter a valid number of years.",
            "field_name": "experience_years"
        },
        "teachers_joining_date_check": {
            "table": "teachers",
            "columns": ["joining_date"],
            "message": "Joining date cannot be in the future. Please enter a valid joining date.",
            "field_name": "joining_date"
        },
        "teachers_salary_check": {
            "table": "teachers",
            "columns": ["salary"],
            "message": "Salary must be greater than zero. Please enter a valid salary amount.",
            "field_name": "salary"
        },
        "teachers_resignation_date_check": {
            "table": "teachers",
            "columns": ["resignation_date"],
            "message": "Resignation date must be after the joining date.",
            "field_name": "resignation_date"
        },

        # Fee Records table
        "fee_records_total_amount_check": {
            "table": "fee_records",
            "columns": ["total_amount"],
            "message": "Total fee amount must be greater than zero. Please enter a valid amount.",
            "field_name": "total_amount"
        },
        "fee_records_paid_amount_check": {
            "table": "fee_records",
            "columns": ["paid_amount"],
            "message": "Paid amount cannot be negative. Please enter a valid amount.",
            "field_name": "paid_amount"
        },
        "fee_records_balance_amount_check": {
            "table": "fee_records",
            "columns": ["balance_amount"],
            "message": "Balance amount cannot be negative. Please check the payment calculations.",
            "field_name": "balance_amount"
        },
        "chk_fee_records_balance": {
            "table": "fee_records",
            "columns": ["balance_amount", "total_amount", "paid_amount"],
            "message": "Balance amount must equal total amount minus paid amount. Please check the calculations.",
            "field_name": "balance_calculation"
        },
        "fee_records_due_date_check": {
            "table": "fee_records",
            "columns": ["due_date"],
            "message": "Due date must be a valid date (not before year 2020).",
            "field_name": "due_date"
        },

        # Fee Payments table
        "fee_payments_amount_check": {
            "table": "fee_payments",
            "columns": ["amount"],
            "message": "Payment amount must be greater than zero. Please enter a valid amount.",
            "field_name": "amount"
        },
        "fee_payments_payment_date_check": {
            "table": "fee_payments",
            "columns": ["payment_date"],
            "message": "Payment date cannot be in the future. Please enter a valid payment date.",
            "field_name": "payment_date"
        },

        # Monthly Fee Tracking table
        "chk_academic_month_valid": {
            "table": "monthly_fee_tracking",
            "columns": ["academic_month"],
            "message": "Academic month must be between 1 and 12. Please select a valid month.",
            "field_name": "academic_month"
        },

        # Leave Requests table
        "leave_requests_applicant_type_check": {
            "table": "leave_requests",
            "columns": ["applicant_type"],
            "message": "Applicant type must be either 'student' or 'teacher'.",
            "field_name": "applicant_type"
        },
        "chk_leave_requests_dates": {
            "table": "leave_requests",
            "columns": ["start_date", "end_date"],
            "message": "Leave end date must be on or after the start date.",
            "field_name": "leave_dates"
        },
        "chk_leave_requests_total_days": {
            "table": "leave_requests",
            "columns": ["total_days"],
            "message": "Total leave days must be greater than zero.",
            "field_name": "total_days"
        },
        "leave_requests_half_day_session_check": {
            "table": "leave_requests",
            "columns": ["half_day_session"],
            "message": "Half day session must be either 'morning' or 'afternoon'.",
            "field_name": "half_day_session"
        },

        # Expenses table
        "expenses_expense_date_check": {
            "table": "expenses",
            "columns": ["expense_date"],
            "message": "Expense date must be a valid date (not before year 2020).",
            "field_name": "expense_date"
        },
        "expenses_amount_check": {
            "table": "expenses",
            "columns": ["amount"],
            "message": "Expense amount must be greater than zero. Please enter a valid amount.",
            "field_name": "amount"
        },
        "expenses_tax_amount_check": {
            "table": "expenses",
            "columns": ["tax_amount"],
            "message": "Tax amount cannot be negative. Please enter a valid tax amount.",
            "field_name": "tax_amount"
        },
        "expenses_total_amount_check": {
            "table": "expenses",
            "columns": ["total_amount"],
            "message": "Total expense amount must be greater than zero. Please enter a valid amount.",
            "field_name": "total_amount"
        },
        "expenses_payment_date_check": {
            "table": "expenses",
            "columns": ["payment_date"],
            "message": "Payment date must be on or after the expense date.",
            "field_name": "payment_date"
        },
        "expenses_recurring_frequency_check": {
            "table": "expenses",
            "columns": ["recurring_frequency"],
            "message": "Recurring frequency must be one of: Monthly, Quarterly, Half Yearly, Yearly.",
            "field_name": "recurring_frequency"
        },
        "expenses_priority_check": {
            "table": "expenses",
            "columns": ["priority"],
            "message": "Priority must be one of: Low, Medium, High, Urgent.",
            "field_name": "priority"
        },

        # Purchase Orders table
        "purchase_orders_subtotal_check": {
            "table": "purchase_orders",
            "columns": ["subtotal"],
            "message": "Purchase order subtotal must be greater than zero. Please enter a valid amount.",
            "field_name": "subtotal"
        },
        "purchase_orders_tax_amount_check": {
            "table": "purchase_orders",
            "columns": ["tax_amount"],
            "message": "Tax amount cannot be negative. Please enter a valid tax amount.",
            "field_name": "tax_amount"
        },
        "purchase_orders_discount_amount_check": {
            "table": "purchase_orders",
            "columns": ["discount_amount"],
            "message": "Discount amount cannot be negative. Please enter a valid discount amount.",
            "field_name": "discount_amount"
        },
        "purchase_orders_total_amount_check": {
            "table": "purchase_orders",
            "columns": ["total_amount"],
            "message": "Total purchase order amount must be greater than zero. Please enter a valid amount.",
            "field_name": "total_amount"
        },
        "purchase_orders_status_check": {
            "table": "purchase_orders",
            "columns": ["status"],
            "message": "Purchase order status must be one of: Draft, Sent, Acknowledged, Delivered, Completed, Cancelled.",
            "field_name": "status"
        },
        "chk_purchase_orders_dates": {
            "table": "purchase_orders",
            "columns": ["expected_delivery_date", "order_date"],
            "message": "Expected delivery date must be on or after the order date.",
            "field_name": "delivery_date"
        },
        "chk_purchase_orders_actual_delivery": {
            "table": "purchase_orders",
            "columns": ["actual_delivery_date", "order_date"],
            "message": "Actual delivery date must be on or after the order date.",
            "field_name": "actual_delivery_date"
        },

        # Vendors table
        "vendors_rating_check": {
            "table": "vendors",
            "columns": ["rating"],
            "message": "Vendor rating must be between 0 and 5. Please enter a valid rating.",
            "field_name": "rating"
        }
    }

    @classmethod
    def get_constraint_message(cls, constraint_name: str, constraint_type: ConstraintType) -> str:
        """
        Get user-friendly error message for a database constraint violation

        Args:
            constraint_name: Name of the constraint that was violated
            constraint_type: Type of constraint (unique, foreign_key, check, not_null)

        Returns:
            User-friendly error message
        """
        constraint_maps = {
            ConstraintType.UNIQUE: cls.UNIQUE_CONSTRAINTS,
            ConstraintType.FOREIGN_KEY: cls.FOREIGN_KEY_CONSTRAINTS,
            ConstraintType.CHECK: cls.CHECK_CONSTRAINTS
        }

        constraint_map = constraint_maps.get(constraint_type, {})
        constraint_info = constraint_map.get(constraint_name)

        if constraint_info:
            return constraint_info["message"]

        # Fallback messages for unknown constraints
        fallback_messages = {
            ConstraintType.UNIQUE: "This information already exists in the system. Please use different values.",
            ConstraintType.FOREIGN_KEY: "Invalid reference selected. Please select a valid option from the dropdown.",
            ConstraintType.CHECK: "The entered data does not meet the required format or constraints.",
            ConstraintType.NOT_NULL: "This field is required and cannot be empty."
        }

        return fallback_messages.get(constraint_type, "A database constraint was violated. Please check your input and try again.")

    @classmethod
    def get_field_name(cls, constraint_name: str, constraint_type: ConstraintType) -> str:
        """
        Get the field name associated with a constraint

        Args:
            constraint_name: Name of the constraint
            constraint_type: Type of constraint

        Returns:
            Field name or generic identifier
        """
        constraint_maps = {
            ConstraintType.UNIQUE: cls.UNIQUE_CONSTRAINTS,
            ConstraintType.FOREIGN_KEY: cls.FOREIGN_KEY_CONSTRAINTS,
            ConstraintType.CHECK: cls.CHECK_CONSTRAINTS
        }

        constraint_map = constraint_maps.get(constraint_type, {})
        constraint_info = constraint_map.get(constraint_name)

        if constraint_info:
            return constraint_info["field_name"]

        return "unknown_field"
