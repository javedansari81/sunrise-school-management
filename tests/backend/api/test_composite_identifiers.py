#!/usr/bin/env python3
"""
Test the new composite identifier system for leave requests
"""

import asyncio
import sys
import os

# Add the parent directory to Python path to access app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from app.utils.identifier_helpers import (
    parse_student_identifier, parse_teacher_identifier,
    format_student_identifier, format_teacher_identifier,
    validate_identifier_format
)
from app.schemas.leave import LeaveRequestCreateFriendly, ApplicantTypeEnum
from datetime import date

def test_student_identifier_parsing():
    """Test student identifier parsing with various formats"""
    
    print("🧪 Testing Student Identifier Parsing")
    print("=" * 40)
    
    test_cases = [
        # Composite formats
        ("Roll 001: John Doe", "composite"),
        ("Roll001: Jane Smith", "composite"),
        ("001 - Mike Johnson", "composite"),
        ("123-Sarah Wilson", "composite"),
        
        # Legacy formats
        ("STU001", "admission"),
        ("ADM123", "admission"),
        
        # Roll number only
        ("001", "roll"),
        ("123", "roll"),
        
        # Name only
        ("John Doe", "name"),
        ("Single", "name")
    ]
    
    for identifier, expected_type in test_cases:
        try:
            result = parse_student_identifier(identifier)
            status = "✅" if result['type'] == expected_type else "❌"
            print(f"{status} '{identifier}' -> {result['type']} (expected: {expected_type})")
            if result['type'] == 'composite':
                print(f"    Roll: {result['roll_number']}, Name: {result['name']}")
            elif result['type'] == 'admission':
                print(f"    Admission: {result['admission_number']}")
        except Exception as e:
            print(f"❌ '{identifier}' -> Error: {e}")
    
    return True


def test_teacher_identifier_parsing():
    """Test teacher identifier parsing with various formats"""
    
    print("\n🧪 Testing Teacher Identifier Parsing")
    print("=" * 40)
    
    test_cases = [
        # Composite formats
        ("John Smith (EMP001)", "composite"),
        ("Jane Doe(TCH123)", "composite"),
        ("Mike Johnson - EMP456", "composite"),
        ("Sarah Wilson-TCH789", "composite"),
        
        # Legacy formats
        ("EMP001", "employee"),
        ("TCH123", "employee"),
        
        # Name only
        ("John Smith", "name"),
        ("Jane", "name")
    ]
    
    for identifier, expected_type in test_cases:
        try:
            result = parse_teacher_identifier(identifier)
            status = "✅" if result['type'] == expected_type else "❌"
            print(f"{status} '{identifier}' -> {result['type']} (expected: {expected_type})")
            if result['type'] == 'composite':
                print(f"    Name: {result['name']}, Employee ID: {result['employee_id']}")
            elif result['type'] == 'employee':
                print(f"    Employee ID: {result['employee_id']}")
        except Exception as e:
            print(f"❌ '{identifier}' -> Error: {e}")
    
    return True


def test_identifier_formatting():
    """Test identifier formatting functions"""
    
    print("\n🧪 Testing Identifier Formatting")
    print("=" * 35)
    
    # Mock student object
    class MockStudent:
        def __init__(self, first_name, last_name, roll_number):
            self.first_name = first_name
            self.last_name = last_name
            self.roll_number = roll_number
    
    # Mock teacher object
    class MockTeacher:
        def __init__(self, first_name, last_name, employee_id):
            self.first_name = first_name
            self.last_name = last_name
            self.employee_id = employee_id
    
    # Test student formatting
    students = [
        MockStudent("John", "Doe", "1"),
        MockStudent("Jane", "Smith", "123"),
        MockStudent("Mike", "Johnson", "001")
    ]
    
    print("Student formatting:")
    for student in students:
        formatted = format_student_identifier(student)
        print(f"  {student.first_name} {student.last_name} (Roll {student.roll_number}) -> '{formatted}'")
    
    # Test teacher formatting
    teachers = [
        MockTeacher("John", "Smith", "EMP001"),
        MockTeacher("Jane", "Doe", "TCH123"),
        MockTeacher("Mike", "Wilson", "ADM456")
    ]
    
    print("\nTeacher formatting:")
    for teacher in teachers:
        formatted = format_teacher_identifier(teacher)
        print(f"  {teacher.first_name} {teacher.last_name} ({teacher.employee_id}) -> '{formatted}'")
    
    return True


def test_schema_validation():
    """Test the friendly schema with composite identifiers"""
    
    print("\n🧪 Testing Schema Validation")
    print("=" * 30)
    
    test_cases = [
        {
            "name": "Student with composite identifier",
            "data": {
                "applicant_identifier": "Roll 001: John Doe",
                "applicant_type": "student",
                "leave_type_id": 1,
                "start_date": "2025-08-05",
                "end_date": "2025-08-06",
                "reason": "Family emergency",
                "parent_consent": True,
                "total_days": 2
            }
        },
        {
            "name": "Teacher with composite identifier",
            "data": {
                "applicant_identifier": "Jane Smith (EMP001)",
                "applicant_type": "teacher",
                "leave_type_id": 1,
                "start_date": "2025-08-05",
                "end_date": "2025-08-06",
                "reason": "Professional development",
                "substitute_teacher_identifier": "Mike Johnson (EMP002)",
                "substitute_arranged": True,
                "total_days": 2
            }
        },
        {
            "name": "Legacy admission number",
            "data": {
                "applicant_identifier": "STU001",
                "applicant_type": "student",
                "leave_type_id": 1,
                "start_date": "2025-08-05",
                "end_date": "2025-08-06",
                "reason": "Medical appointment",
                "parent_consent": True,
                "total_days": 2
            }
        }
    ]
    
    for test_case in test_cases:
        try:
            # Convert string dates to date objects
            data = test_case["data"].copy()
            data["start_date"] = date.fromisoformat(data["start_date"])
            data["end_date"] = date.fromisoformat(data["end_date"])
            data["applicant_type"] = ApplicantTypeEnum(data["applicant_type"])
            
            leave_request = LeaveRequestCreateFriendly(**data)
            print(f"✅ {test_case['name']}: Validation passed")
            print(f"    Identifier: {leave_request.applicant_identifier}")
            
        except Exception as e:
            print(f"❌ {test_case['name']}: Validation failed - {e}")
    
    return True


def test_validation_functions():
    """Test identifier validation functions"""
    
    print("\n🧪 Testing Validation Functions")
    print("=" * 32)
    
    student_identifiers = [
        "Roll 001: John Doe",
        "001 - Jane Smith",
        "STU001",
        "001",
        "",
        "   "
    ]
    
    teacher_identifiers = [
        "John Smith (EMP001)",
        "Jane Doe - TCH123",
        "EMP001",
        "",
        "   "
    ]
    
    print("Student identifier validation:")
    for identifier in student_identifiers:
        is_valid = validate_identifier_format(identifier, ApplicantTypeEnum.STUDENT)
        status = "✅" if is_valid else "❌"
        print(f"  {status} '{identifier}' -> {is_valid}")
    
    print("\nTeacher identifier validation:")
    for identifier in teacher_identifiers:
        is_valid = validate_identifier_format(identifier, ApplicantTypeEnum.TEACHER)
        status = "✅" if is_valid else "❌"
        print(f"  {status} '{identifier}' -> {is_valid}")
    
    return True


if __name__ == "__main__":
    print("🚀 Starting Composite Identifier Tests")
    print("=" * 50)
    
    tests = [
        test_student_identifier_parsing,
        test_teacher_identifier_parsing,
        test_identifier_formatting,
        test_schema_validation,
        test_validation_functions
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"✅ Passed: {sum(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! Composite identifier system is ready!")
    else:
        print("\n💥 Some tests failed. Please check the implementation.")
        sys.exit(1)
