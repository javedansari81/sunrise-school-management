#!/usr/bin/env python3
"""
Test script to make the actual API call to create a student
This will help us see the exact error that's occurring
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_student_creation_api():
    """Test the student creation API with the problematic payload"""
    
    # Your original payload
    student_payload = {
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
        "aadhar_no": None,  # Use None instead of empty string
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
    
    # First, let's try to login to get a valid token using JSON format
    login_payload = {
        "email": "admin@sunriseschool.edu",  # Default admin email
        "password": "admin123"  # Default admin password
    }

    print("🔐 Attempting to login...")

    async with aiohttp.ClientSession() as session:
        try:
            # Login to get token using the JSON endpoint
            async with session.post(
                "http://localhost:8000/api/v1/auth/login-json",
                json=login_payload,
                headers={"Content-Type": "application/json"}
            ) as login_response:
                
                if login_response.status == 200:
                    login_data = await login_response.json()
                    access_token = login_data.get("access_token")
                    print(f"✅ Login successful! Token: {access_token[:20]}...")
                    
                    # Now try to create student with the token
                    print("\n👤 Attempting to create student...")
                    
                    headers = {
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    }
                    
                    async with session.post(
                        "http://localhost:8000/api/v1/students",
                        json=student_payload,
                        headers=headers
                    ) as student_response:
                        
                        print(f"📊 Response Status: {student_response.status}")
                        response_text = await student_response.text()
                        
                        if student_response.status == 200 or student_response.status == 201:
                            print("✅ Student created successfully!")
                            response_data = await student_response.json()
                            print(f"   Student ID: {response_data.get('id')}")
                            print(f"   Name: {response_data.get('first_name')} {response_data.get('last_name')}")
                            print(f"   Admission Number: {response_data.get('admission_number')}")
                        else:
                            print(f"❌ Student creation failed!")
                            print(f"   Status: {student_response.status}")
                            print(f"   Response: {response_text}")
                            
                            # Try to parse as JSON for better error details
                            try:
                                error_data = json.loads(response_text)
                                print(f"   Error Detail: {error_data.get('detail', 'No detail provided')}")
                            except:
                                print(f"   Raw Response: {response_text}")
                
                else:
                    print(f"❌ Login failed! Status: {login_response.status}")
                    login_text = await login_response.text()
                    print(f"   Response: {login_text}")
                    return False
                    
        except aiohttp.ClientError as e:
            print(f"❌ Connection error: {e}")
            print("   Make sure your FastAPI server is running on http://localhost:8000")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False

async def test_auth_endpoint():
    """Test if the auth endpoint is working"""
    print("🔍 Testing authentication endpoint...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("http://localhost:8000/api/v1/auth/me") as response:
                print(f"📊 Auth endpoint status: {response.status}")
                if response.status == 401:
                    print("✅ Auth endpoint is working (returns 401 without token as expected)")
                else:
                    response_text = await response.text()
                    print(f"   Response: {response_text}")
        except Exception as e:
            print(f"❌ Error testing auth endpoint: {e}")

async def test_server_health():
    """Test if the server is running"""
    print("🏥 Testing server health...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("http://localhost:8000/health") as response:
                if response.status == 200:
                    print("✅ Server is running and healthy")
                    return True
                else:
                    print(f"⚠️  Server responded with status: {response.status}")
                    return True  # Server is running but maybe no health endpoint
        except aiohttp.ClientError:
            print("❌ Server is not running or not accessible")
            print("   Please start your FastAPI server with: uvicorn main:app --reload")
            return False
        except Exception as e:
            print(f"❌ Error testing server: {e}")
            return False

async def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 Student Creation API Test")
    print("=" * 60)
    
    # Test server health first
    server_ok = await test_server_health()
    if not server_ok:
        return
    
    # Test auth endpoint
    await test_auth_endpoint()
    
    # Test student creation
    await test_student_creation_api()
    
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print("If you're still getting 422 errors, the issue might be:")
    print("1. Authentication token issues")
    print("2. Database constraint violations")
    print("3. Missing metadata in the database")
    print("4. Schema validation problems")
    print("\nCheck the FastAPI server logs for more detailed error information.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
