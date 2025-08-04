"""
Sample data for testing.

This module contains sample data objects that can be used across different tests.
"""
from datetime import date, datetime
from typing import Dict, Any


class SampleData:
    """Container for sample test data."""

    @staticmethod
    def teacher_data() -> Dict[str, Any]:
        """Sample teacher data for testing."""
        return {
            "employee_id": "EMP001",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@test.com",
            "phone": "1234567890",
            "date_of_birth": "1985-01-15",
            "joining_date": "2020-08-01",
            "position": "Teacher",
            "department": "Mathematics",
            "gender_id": 1,
            "qualification_id": 1,
            "employment_status_id": 1,
            "address": "123 Test Street, Test City",
            "city": "Test City",
            "state": "Test State",
            "postal_code": "12345",
            "country": "Test Country",
            "emergency_contact_name": "Jane Doe",
            "emergency_contact_phone": "0987654321",
            "emergency_contact_relation": "Spouse",
            "subjects": "Mathematics, Physics",
            "experience_years": 5,
            "salary": 50000.00,
            "is_active": True
        }

    @staticmethod
    def student_data() -> Dict[str, Any]:
        """Sample student data for testing."""
        return {
            "admission_number": "ADM001",
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@test.com",
            "phone": "0987654321",
            "date_of_birth": "2005-03-20",
            "admission_date": "2020-04-01",
            "class_id": 1,
            "session_year_id": 1,
            "gender_id": 2,
            "roll_number": "001",
            "section": "A",
            "blood_group": "O+",
            "address": "456 Student Lane, Student City",
            "city": "Student City",
            "state": "Student State",
            "postal_code": "54321",
            "country": "Student Country",
            "father_name": "Robert Smith",
            "father_phone": "1111111111",
            "father_email": "robert.smith@test.com",
            "father_occupation": "Engineer",
            "mother_name": "Mary Smith",
            "mother_phone": "2222222222",
            "mother_email": "mary.smith@test.com",
            "mother_occupation": "Doctor",
            "emergency_contact_name": "Robert Smith",
            "emergency_contact_phone": "1111111111",
            "emergency_contact_relation": "Father",
            "previous_school": "Previous School Name",
            "is_active": True
        }

    @staticmethod
    def user_data() -> Dict[str, Any]:
        """Sample user data for testing."""
        return {
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User",
            "phone": "1234567890",
            "user_type_id": 2,  # Teacher
            "is_active": True,
            "is_verified": True
        }

    @staticmethod
    def admin_user_data() -> Dict[str, Any]:
        """Sample admin user data for testing."""
        return {
            "email": "admin@test.com",
            "password": "adminpassword123",
            "first_name": "Admin",
            "last_name": "User",
            "phone": "9999999999",
            "user_type_id": 1,  # Admin
            "is_active": True,
            "is_verified": True
        }

    @staticmethod
    def login_credentials() -> Dict[str, str]:
        """Sample login credentials for testing."""
        return {
            "email": "amit.kumar@gmail.com",
            "password": "Sunrise@001"
        }

    @staticmethod
    def profile_update_data() -> Dict[str, Any]:
        """Sample profile update data for testing."""
        return {
            "phone": "9876543210",
            "address": "Updated Address, Test City",
            "emergency_contact_name": "Emergency Contact",
            "emergency_contact_phone": "9876543211"
        }

    @staticmethod
    def invalid_data_samples() -> Dict[str, Dict[str, Any]]:
        """Sample invalid data for testing validation."""
        return {
            "invalid_email": {
                "email": "invalid_email_format",
                "first_name": "Test",
                "last_name": "User"
            },
            "invalid_phone": {
                "phone": "invalid_phone_format",
                "first_name": "Test",
                "last_name": "User"
            },
            "invalid_date": {
                "date_of_birth": "invalid_date_format",
                "first_name": "Test",
                "last_name": "User"
            },
            "missing_required_fields": {
                "first_name": "Test"
                # Missing last_name and other required fields
            }
        }

    @staticmethod
    def configuration_data() -> Dict[str, Any]:
        """Sample configuration data for testing."""
        return {
            "genders": [
                {"id": 1, "name": "Male", "is_active": True},
                {"id": 2, "name": "Female", "is_active": True}
            ],
            "qualifications": [
                {"id": 1, "name": "Bachelor's Degree", "is_active": True},
                {"id": 2, "name": "Master's Degree", "is_active": True},
                {"id": 3, "name": "PhD", "is_active": True}
            ],
            "employment_statuses": [
                {"id": 1, "name": "Full-time", "is_active": True},
                {"id": 2, "name": "Part-time", "is_active": True},
                {"id": 3, "name": "Contract", "is_active": True}
            ],
            "user_types": [
                {"id": 1, "name": "Admin", "is_active": True},
                {"id": 2, "name": "Teacher", "is_active": True},
                {"id": 3, "name": "Student", "is_active": True}
            ]
        }

    @staticmethod
    def date_samples() -> Dict[str, Any]:
        """Sample date data for testing date conversion."""
        return {
            "valid_string_dates": [
                "2020-01-01",
                "1985-12-31",
                "2000-02-29"  # Leap year
            ],
            "invalid_string_dates": [
                "invalid-date",
                "2020-13-01",  # Invalid month
                "2020-02-30",  # Invalid day
                "20-01-01",    # Wrong format
                "",            # Empty string
                "2020/01/01"   # Wrong separator
            ],
            "date_objects": [
                date(2020, 1, 1),
                date(1985, 12, 31),
                date(2000, 2, 29)
            ],
            "datetime_objects": [
                datetime(2020, 1, 1, 12, 0, 0),
                datetime(1985, 12, 31, 23, 59, 59),
                datetime(2000, 2, 29, 6, 30, 0)
            ]
        }

    @staticmethod
    def api_response_samples() -> Dict[str, Any]:
        """Sample API response data for testing."""
        return {
            "success_response": {
                "status": "success",
                "data": {"id": 1, "name": "Test"},
                "message": "Operation successful"
            },
            "error_response": {
                "status": "error",
                "error": "Something went wrong",
                "details": "Detailed error message"
            },
            "validation_error_response": {
                "detail": [
                    {
                        "type": "value_error",
                        "loc": ["body", "email"],
                        "msg": "field required",
                        "input": None,
                        "url": "https://errors.pydantic.dev/2.5/v/missing"
                    }
                ]
            }
        }

    @staticmethod
    def bulk_data_samples(count: int = 10) -> Dict[str, Any]:
        """Generate bulk sample data for performance testing."""
        teachers = []
        students = []
        
        for i in range(count):
            teacher = SampleData.teacher_data()
            teacher["employee_id"] = f"EMP{i+1:03d}"
            teacher["email"] = f"teacher{i+1}@test.com"
            teachers.append(teacher)
            
            student = SampleData.student_data()
            student["admission_number"] = f"ADM{i+1:03d}"
            student["email"] = f"student{i+1}@test.com"
            student["roll_number"] = f"{i+1:03d}"
            students.append(student)
        
        return {
            "teachers": teachers,
            "students": students
        }
