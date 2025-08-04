#!/usr/bin/env python3
"""
Test script to verify the student creation fix works
"""

import asyncio
import sys
import json
from pathlib import Path

# Add the backend directory to the path
backend_path = Path(__file__).parent / "sunrise-backend-fastapi"
sys.path.append(str(backend_path))

try:
    from app.schemas.student import StudentCreate
    print("✅ Successfully imported StudentCreate schema")
except ImportError as e:
    print(f"❌ Failed to import StudentCreate schema: {e}")
    sys.exit(1)

def test_student_validation():
    """Test the student validation with the problematic payload"""
    
    # Your original payload that was causing the 422 error
    test_payload = {
        "admission_number": "STU002",
        "roll_number": "2",
        "first_name": "Javed",
        "last_name": "Ansari",
        "class_id": 1,
        "session_year_id": 4,
        "section": "A",
        "date_of_birth": "2019-01-04",
        "gender_id": 1,
        "blood_group": None,
        "phone": None,
        "email": None,
        "aadhar_no": "",  # This was causing the issue
        "address": None,
        "city": None,
        "state": None,
        "postal_code": None,
        "country": "India",
        "father_name": "Shahid Ansari",
        "father_phone": None,
        "father_email": None,
        "father_occupation": None,
        "mother_name": "Hamida Khatoon",
        "mother_phone": None,
        "mother_email": None,
        "mother_occupation": None,
        "emergency_contact_name": None,
        "emergency_contact_phone": None,
        "emergency_contact_relation": None,
        "admission_date": "2025-08-01",
        "previous_school": None,
        "is_active": True
    }
    
    print("🧪 Testing student validation with original payload...")
    
    try:
        # Try to create StudentCreate instance with the payload
        student = StudentCreate(**test_payload)
        print("✅ SUCCESS: Student validation passed!")
        print(f"   - Admission Number: {student.admission_number}")
        print(f"   - Name: {student.first_name} {student.last_name}")
        print(f"   - Aadhar No: {student.aadhar_no} (should be None for empty string)")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Student validation failed with error: {e}")
        return False

def test_aadhar_variations():
    """Test different aadhar_no variations"""
    
    base_payload = {
        "admission_number": "STU003",
        "first_name": "Test",
        "last_name": "Student",
        "class_id": 1,
        "session_year_id": 4,
        "date_of_birth": "2019-01-04",
        "gender_id": 1,
        "father_name": "Test Father",
        "mother_name": "Test Mother",
        "admission_date": "2025-08-01",
        "country": "India"
    }
    
    test_cases = [
        {"aadhar_no": "", "description": "Empty string"},
        {"aadhar_no": None, "description": "None/null"},
        {"aadhar_no": "123456789012", "description": "Valid 12-digit Aadhar"},
        {"aadhar_no": "12345", "description": "Invalid - too short"},
        {"aadhar_no": "12345678901234", "description": "Invalid - too long"},
        {"aadhar_no": "12345678901a", "description": "Invalid - contains letter"},
    ]
    
    print("\n🧪 Testing various Aadhar number formats...")
    
    for i, test_case in enumerate(test_cases, 1):
        payload = {**base_payload, **test_case}
        payload["admission_number"] = f"STU00{i+2}"  # Unique admission numbers
        
        try:
            student = StudentCreate(**payload)
            print(f"✅ Test {i}: {test_case['description']} - PASSED")
            print(f"   Result: aadhar_no = {student.aadhar_no}")
        except Exception as e:
            if "too short" in test_case['description'] or "too long" in test_case['description'] or "contains letter" in test_case['description']:
                print(f"✅ Test {i}: {test_case['description']} - CORRECTLY REJECTED")
                print(f"   Error: {e}")
            else:
                print(f"❌ Test {i}: {test_case['description']} - UNEXPECTEDLY FAILED")
                print(f"   Error: {e}")

def main():
    """Main test function"""
    print("=" * 60)
    print("🎯 Student Creation Fix Validation Test")
    print("=" * 60)
    
    # Test the original problematic payload
    success = test_student_validation()
    
    # Test various aadhar number formats
    test_aadhar_variations()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Fix validation successful!")
        print("\nThe student creation API should now work with your payload.")
        print("You can now restart your FastAPI server and try the API call again.")
    else:
        print("❌ Fix validation failed!")
        print("There may be additional issues to resolve.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
