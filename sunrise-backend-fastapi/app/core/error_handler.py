"""
Centralized Error Handling Utility

This module provides centralized error handling for database operations,
converting technical database errors into user-friendly messages with
consistent response format.
"""

import logging
import re
from typing import Dict, Any, Optional, Tuple, List
from sqlalchemy.exc import IntegrityError, DataError, StatementError
from asyncpg.exceptions import (
    UniqueViolationError, ForeignKeyViolationError, CheckViolationError,
    NotNullViolationError, DataError as AsyncpgDataError
)
from fastapi import HTTPException, status

from .database_constraints_mapping import DatabaseConstraints, ConstraintType

logger = logging.getLogger(__name__)


class ErrorResponse:
    """Standard error response format"""
    
    def __init__(
        self,
        success: bool = False,
        message: str = "",
        error_code: str = "",
        field_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.message = message
        self.error_code = error_code
        self.field_name = field_name
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response"""
        response = {
            "success": self.success,
            "message": self.message,
            "error_code": self.error_code
        }
        
        if self.field_name:
            response["field_name"] = self.field_name
        
        if self.details:
            response["details"] = self.details
            
        return response


class DatabaseErrorHandler:
    """
    Centralized database error handler that converts technical database errors
    into user-friendly messages with consistent response format.
    """
    
    @staticmethod
    def extract_constraint_name(error_message: str) -> Optional[str]:
        """
        Extract constraint name from database error message
        
        Args:
            error_message: Raw database error message
            
        Returns:
            Constraint name if found, None otherwise
        """
        # Common patterns for constraint names in error messages
        patterns = [
            r'constraint "([^"]+)"',  # PostgreSQL format: constraint "constraint_name"
            r'CONSTRAINT `([^`]+)`',   # MySQL format: CONSTRAINT `constraint_name`
            r'constraint ([^\s]+)',    # Generic format: constraint constraint_name
            r'Key \(([^)]+)\)',        # PostgreSQL key format: Key (column_name)
            r'UNIQUE constraint failed: ([^\s]+)',  # SQLite format
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_message, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def determine_constraint_type(error: Exception) -> ConstraintType:
        """
        Determine the type of constraint violation from the exception
        
        Args:
            error: Database exception
            
        Returns:
            ConstraintType enum value
        """
        error_str = str(error).lower()
        
        # Check for specific exception types first (asyncpg)
        if isinstance(error, UniqueViolationError):
            return ConstraintType.UNIQUE
        elif isinstance(error, ForeignKeyViolationError):
            return ConstraintType.FOREIGN_KEY
        elif isinstance(error, CheckViolationError):
            return ConstraintType.CHECK
        elif isinstance(error, NotNullViolationError):
            return ConstraintType.NOT_NULL
        
        # Check for SQLAlchemy IntegrityError patterns
        if isinstance(error, IntegrityError):
            if any(keyword in error_str for keyword in ['unique', 'duplicate', 'already exists']):
                return ConstraintType.UNIQUE
            elif any(keyword in error_str for keyword in ['foreign key', 'violates foreign key', 'fkey']):
                return ConstraintType.FOREIGN_KEY
            elif any(keyword in error_str for keyword in ['check constraint', 'check violation']):
                return ConstraintType.CHECK
            elif any(keyword in error_str for keyword in ['not null', 'null value']):
                return ConstraintType.NOT_NULL
        
        # Default to check constraint for data validation errors
        return ConstraintType.CHECK
    
    @staticmethod
    def handle_database_error(error: Exception, operation: str = "database operation") -> ErrorResponse:
        """
        Handle database errors and convert them to user-friendly error responses
        
        Args:
            error: Database exception
            operation: Description of the operation that failed
            
        Returns:
            ErrorResponse with user-friendly message
        """
        try:
            # Log the technical error for debugging
            logger.error(f"Database error in {operation}: {str(error)}", exc_info=True)
            
            # Extract constraint information
            constraint_name = DatabaseErrorHandler.extract_constraint_name(str(error))
            constraint_type = DatabaseErrorHandler.determine_constraint_type(error)
            
            # Get user-friendly message
            if constraint_name:
                user_message = DatabaseConstraints.get_constraint_message(constraint_name, constraint_type)
                field_name = DatabaseConstraints.get_field_name(constraint_name, constraint_type)
            else:
                # Fallback for unknown constraints
                user_message = DatabaseErrorHandler._get_fallback_message(constraint_type, str(error))
                field_name = None
            
            # Generate error code
            error_code = DatabaseErrorHandler._generate_error_code(constraint_type, constraint_name)
            
            return ErrorResponse(
                success=False,
                message=user_message,
                error_code=error_code,
                field_name=field_name,
                details={
                    "operation": operation,
                    "constraint_type": constraint_type.value,
                    "constraint_name": constraint_name
                }
            )
            
        except Exception as handler_error:
            # If error handling itself fails, return a generic error
            logger.error(f"Error in error handler: {str(handler_error)}", exc_info=True)
            return ErrorResponse(
                success=False,
                message="An unexpected error occurred. Please try again or contact support.",
                error_code="UNKNOWN_ERROR",
                details={"operation": operation}
            )
    
    @staticmethod
    def _get_fallback_message(constraint_type: ConstraintType, error_message: str) -> str:
        """
        Get fallback error message when constraint name is not recognized
        
        Args:
            constraint_type: Type of constraint violation
            error_message: Raw error message
            
        Returns:
            User-friendly fallback message
        """
        # Try to extract specific information from error message
        error_lower = error_message.lower()
        
        if constraint_type == ConstraintType.UNIQUE:
            if "email" in error_lower:
                return "This email address is already in use. Please use a different email address."
            elif "admission_number" in error_lower:
                return "This admission number is already in use. Please use a different admission number."
            elif "employee_id" in error_lower:
                return "This employee ID is already in use. Please use a different employee ID."
            else:
                return "This information already exists in the system. Please use different values."
        
        elif constraint_type == ConstraintType.FOREIGN_KEY:
            return "Invalid selection made. Please select a valid option from the available choices."
        
        elif constraint_type == ConstraintType.CHECK:
            if "amount" in error_lower:
                return "Please enter a valid amount (must be greater than zero)."
            elif "date" in error_lower:
                return "Please enter a valid date."
            elif "email" in error_lower:
                return "Please enter a valid email address format."
            else:
                return "The entered data does not meet the required format. Please check your input."
        
        elif constraint_type == ConstraintType.NOT_NULL:
            return "Required information is missing. Please fill in all required fields."
        
        return "A data validation error occurred. Please check your input and try again."
    
    @staticmethod
    def _generate_error_code(constraint_type: ConstraintType, constraint_name: Optional[str]) -> str:
        """
        Generate a standardized error code
        
        Args:
            constraint_type: Type of constraint violation
            constraint_name: Name of the constraint (if available)
            
        Returns:
            Standardized error code
        """
        type_codes = {
            ConstraintType.UNIQUE: "UNIQUE_VIOLATION",
            ConstraintType.FOREIGN_KEY: "FOREIGN_KEY_VIOLATION",
            ConstraintType.CHECK: "CHECK_VIOLATION",
            ConstraintType.NOT_NULL: "NOT_NULL_VIOLATION"
        }
        
        base_code = type_codes.get(constraint_type, "CONSTRAINT_VIOLATION")
        
        if constraint_name:
            # Create a more specific error code
            return f"{base_code}_{constraint_name.upper()}"
        
        return base_code
    
    @staticmethod
    def raise_http_exception(error_response: ErrorResponse, status_code: int = status.HTTP_400_BAD_REQUEST):
        """
        Raise an HTTPException with the error response
        
        Args:
            error_response: ErrorResponse object
            status_code: HTTP status code to use
        """
        raise HTTPException(
            status_code=status_code,
            detail=error_response.to_dict()
        )


class ValidationErrorHandler:
    """
    Handler for pre-database validation errors
    """
    
    @staticmethod
    def create_validation_error(
        message: str,
        field_name: str,
        error_code: str = "VALIDATION_ERROR"
    ) -> ErrorResponse:
        """
        Create a validation error response
        
        Args:
            message: User-friendly error message
            field_name: Name of the field that failed validation
            error_code: Error code for the validation failure
            
        Returns:
            ErrorResponse object
        """
        return ErrorResponse(
            success=False,
            message=message,
            error_code=error_code,
            field_name=field_name
        )
    
    @staticmethod
    def raise_validation_exception(
        message: str,
        field_name: str,
        error_code: str = "VALIDATION_ERROR",
        status_code: int = status.HTTP_400_BAD_REQUEST
    ):
        """
        Raise an HTTPException for validation errors
        
        Args:
            message: User-friendly error message
            field_name: Name of the field that failed validation
            error_code: Error code for the validation failure
            status_code: HTTP status code to use
        """
        error_response = ValidationErrorHandler.create_validation_error(message, field_name, error_code)
        DatabaseErrorHandler.raise_http_exception(error_response, status_code)


# Convenience functions for common error handling patterns
def handle_database_error(error: Exception, operation: str = "database operation") -> ErrorResponse:
    """Convenience function for handling database errors"""
    return DatabaseErrorHandler.handle_database_error(error, operation)


def raise_database_http_exception(
    error: Exception,
    operation: str = "database operation",
    status_code: int = status.HTTP_400_BAD_REQUEST
):
    """Convenience function for raising HTTP exceptions from database errors"""
    error_response = handle_database_error(error, operation)
    DatabaseErrorHandler.raise_http_exception(error_response, status_code)


def raise_validation_http_exception(
    message: str,
    field_name: str,
    error_code: str = "VALIDATION_ERROR",
    status_code: int = status.HTTP_400_BAD_REQUEST
):
    """Convenience function for raising validation HTTP exceptions"""
    ValidationErrorHandler.raise_validation_exception(message, field_name, error_code, status_code)


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
