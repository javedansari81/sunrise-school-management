#!/usr/bin/env python3
"""
Test the leave request API endpoint using the test framework
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from main import app
from app.core.database import get_db
from app.models.user import User
from app.models.student import Student
from app.core.security import get_password_hash
from datetime import date

# Mock database session for testing
async def get_test_db():
    # This would normally return a test database session
    # For now, we'll use the real database
    async for db in get_db():
        yield db

async def test_leave_request_creation():
    """Test leave request creation via API"""
    
    # Override the database dependency
    app.dependency_overrides[get_db] = get_test_db
    
    try:
        async with AsyncClient(base_url="http://localhost:8000") as client:
            # Test payload
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
            
            print("Testing leave request creation via API...")
            print(f"Payload: {payload}")
            
            # First, try to login to get a token
            print("Attempting to login...")
            login_response = await client.post(
                "/api/v1/auth/login",
                data={"username": "admin@sunriseschool.edu", "password": "admin123"}
            )
            
            print(f"Login response status: {login_response.status_code}")
            if login_response.status_code != 200:
                print(f"Login failed: {login_response.text}")
                return False
            
            login_data = login_response.json()
            token = login_data.get("access_token")
            if not token:
                print("No access token received")
                return False
            
            print("✅ Login successful, got token")
            
            # Now test the leave request creation
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.post(
                "/api/v1/leaves/",
                json=payload,
                headers=headers
            )
            
            print(f"Leave request response status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Leave request created successfully!")
                print(f"Response: {response.json()}")
                return True
            else:
                print(f"❌ Leave request failed: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error during API test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up dependency overrides
        app.dependency_overrides.clear()

if __name__ == "__main__":
    success = asyncio.run(test_leave_request_creation())
    if success:
        print("\n🎉 API test passed!")
    else:
        print("\n💥 API test failed!")
        exit(1)
