#!/usr/bin/env python3
"""
Test script to validate the leave request payload and identify validation issues
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'sunrise-backend-fastapi'))

from pydantic import ValidationError
from app.schemas.leave import LeaveRequestCreate, ApplicantTypeEnum
from datetime import date

def test_payload_validation():
    """Test the exact payload from the frontend"""
    
    # The payload from the UI
    payload = {
        "applicant_id": 101,
        "applicant_type": "student",
        "leave_type_id": 1,
        "start_date": "2025-08-01",
        "end_date": "2025-08-02",
        "reason": "PTO",
        "parent_consent": False,
        "emergency_contact_name": "",
        "emergency_contact_phone": "",
        "substitute_teacher_id": "",
        "substitute_arranged": False,
        "total_days": 2
    }
    
    print("Testing payload validation...")
    print(f"Payload: {payload}")
    
    try:
        # Try to create the schema object
        leave_request = LeaveRequestCreate(**payload)
        print("✅ Validation successful!")
        print(f"Created object: {leave_request}")
        return True
        
    except ValidationError as e:
        print("❌ Validation failed!")
        print(f"Validation errors: {e}")
        
        # Print detailed error information
        for error in e.errors():
            print(f"Field: {error['loc']}")
            print(f"Error: {error['msg']}")
            print(f"Type: {error['type']}")
            print("---")
        
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_minimal_payload():
    """Test with minimal required fields"""
    
    minimal_payload = {
        "applicant_id": 101,
        "applicant_type": ApplicantTypeEnum.STUDENT,
        "leave_type_id": 1,
        "start_date": date(2025, 8, 1),
        "end_date": date(2025, 8, 2),
        "reason": "Test reason for leave request",
        "total_days": 2
    }
    
    print("\nTesting minimal payload validation...")
    print(f"Minimal payload: {minimal_payload}")
    
    try:
        leave_request = LeaveRequestCreate(**minimal_payload)
        print("✅ Minimal validation successful!")
        print(f"Created object: {leave_request}")
        return True
        
    except ValidationError as e:
        print("❌ Minimal validation failed!")
        print(f"Validation errors: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("=== Leave Request Validation Test ===")
    
    # Test the original payload
    success1 = test_payload_validation()
    
    # Test minimal payload
    success2 = test_minimal_payload()
    
    if success1 and success2:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Some tests failed!")
