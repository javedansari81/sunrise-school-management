#!/usr/bin/env python3
"""
Test script to validate student API
"""
import asyncio
import json
from datetime import date
import httpx

async def test_student_creation():
    """Test student creation with minimal data"""
    
    # First login to get token
    login_data = {
        "email": "admin@sunriseschool.edu",
        "password": "admin123"
    }
    
    async with httpx.AsyncClient() as client:
        # Login
        login_response = await client.post(
            "http://localhost:8000/api/v1/auth/login-json",
            json=login_data
        )
        
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.status_code}")
            print(login_response.text)
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test student data with unique admission number
        student_data = {
            "admission_number": "TEST999",  # Use unique number
            "first_name": "Test",
            "last_name": "Student",
            "date_of_birth": "2010-01-01",
            "gender_id": 1,  # Male
            "class_id": 1,   # First class
            "session_year_id": 4,  # 2025-26
            "father_name": "Test Father",
            "mother_name": "Test Mother",
            "admission_date": "2025-01-01"
        }
        
        print("Sending student data:")
        print(json.dumps(student_data, indent=2))
        
        # Test the test endpoint first
        test_response = await client.post(
            "http://localhost:8000/api/v1/students/test",
            json=student_data,
            headers=headers,
            timeout=10.0
        )

        print(f"\nTest endpoint response status: {test_response.status_code}")
        print(f"Test endpoint response body: {test_response.text}")

        # Create student
        response = await client.post(
            "http://localhost:8000/api/v1/students/",
            json=student_data,
            headers=headers,
            timeout=10.0
        )
        
        print(f"\nResponse status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 422:
            print("\nValidation errors:")
            error_data = response.json()
            for error in error_data.get("detail", []):
                print(f"- {error}")

if __name__ == "__main__":
    asyncio.run(test_student_creation())
