#!/usr/bin/env python3
"""
Simple test to verify backend is working
"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_backend():
    """Test basic backend functionality"""
    print("🧪 Testing Backend Basic Functionality")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            # Test 1: Health check
            print("\n1. Testing health endpoint...")
            health_response = await client.get(f"{BASE_URL}/")
            print(f"   Status: {health_response.status_code}")
            if health_response.status_code == 200:
                print("✅ Backend is responding")
            else:
                print("❌ Backend health check failed")
                return
            
            # Test 2: Try to access docs
            print("\n2. Testing docs endpoint...")
            docs_response = await client.get(f"{BASE_URL}/docs")
            print(f"   Status: {docs_response.status_code}")
            if docs_response.status_code == 200:
                print("✅ Docs endpoint working")
            else:
                print("❌ Docs endpoint failed")
            
            # Test 3: Try login with correct format
            print("\n3. Testing login endpoint...")
            login_data = {
                "username": "admin@sunriseschool.edu",
                "password": "admin123"
            }
            
            # Try form data first
            login_response = await client.post(
                f"{BASE_URL}/api/v1/auth/login",
                data=login_data
            )
            
            print(f"   Login Status: {login_response.status_code}")
            if login_response.status_code == 200:
                print("✅ Login successful")
                result = login_response.json()
                token = result.get("access_token")
                print(f"   Token received: {token[:20] if token else 'None'}...")
                
                # Test 4: Try authenticated endpoint
                print("\n4. Testing authenticated endpoint...")
                headers = {"Authorization": f"Bearer {token}"}
                
                # Try to get leave types (should be available)
                config_response = await client.get(
                    f"{BASE_URL}/api/v1/configuration/leave-management/",
                    headers=headers
                )
                
                print(f"   Config Status: {config_response.status_code}")
                if config_response.status_code == 200:
                    print("✅ Authenticated endpoint working")
                    config_data = config_response.json()
                    leave_types = config_data.get("leave_types", [])
                    classes = config_data.get("classes", [])
                    print(f"   Found {len(leave_types)} leave types and {len(classes)} classes")
                else:
                    print("❌ Authenticated endpoint failed")
                    print(f"   Error: {config_response.text}")
                
            else:
                print("❌ Login failed")
                print(f"   Error: {login_response.text}")
                
                # Try to understand the error
                try:
                    error_data = login_response.json()
                    print(f"   Error details: {json.dumps(error_data, indent=2)}")
                except:
                    pass
                
        except Exception as e:
            print(f"❌ Error during testing: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_backend())
