#!/usr/bin/env python3
"""
Test script to validate the leave request payload and identify validation issues
"""

from pydantic import ValidationError
from app.schemas.leave import LeaveRequestCreate, ApplicantTypeEnum
from datetime import date

def test_payload_validation():
    """Test the exact payload from the frontend"""
    
    # The payload from the UI (updated with valid student ID)
    payload = {
        "applicant_id": 5,
        "applicant_type": "student",
        "leave_type_id": 1,
        "start_date": "2025-08-01",
        "end_date": "2025-08-02",
        "reason": "Personal Time Off",
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

if __name__ == "__main__":
    print("=== Leave Request Validation Test ===")
    test_payload_validation()
