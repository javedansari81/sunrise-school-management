#!/usr/bin/env python3
"""
Script to validate API endpoints with test data
"""
import asyncio
import httpx
import json
from typing import Dict, Any


class APIValidator:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.auth_token = None
    
    async def test_health(self) -> bool:
        """Test if the API is running"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/docs")
                return response.status_code == 200
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    async def test_login(self) -> bool:
        """Test login endpoint"""
        try:
            async with httpx.AsyncClient() as client:
                # First, try to create a test user (this might fail if user exists)
                test_user = {
                    "first_name": "Test",
                    "last_name": "User",
                    "mobile": "1234567890",
                    "email": "test@example.com",
                    "password": "testpassword",
                    "user_type": "admin"
                }
                
                # Try login with test credentials
                login_data = {
                    "email": "test@example.com",
                    "password": "testpassword"
                }
                
                response = await client.post(
                    f"{self.base_url}/api/v1/auth/login",
                    json=login_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.auth_token = data.get("access_token")
                    print("✅ Login successful")
                    return True
                else:
                    print(f"❌ Login failed: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Login test failed: {e}")
            return False
    
    async def test_protected_route(self) -> bool:
        """Test protected route"""
        if not self.auth_token:
            print("❌ No auth token available for protected route test")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                response = await client.get(
                    f"{self.base_url}/api/v1/auth/protected",
                    headers=headers
                )
                
                if response.status_code == 200:
                    print("✅ Protected route accessible")
                    return True
                else:
                    print(f"❌ Protected route failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Protected route test failed: {e}")
            return False
    
    async def test_users_endpoint(self) -> bool:
        """Test users endpoint"""
        if not self.auth_token:
            print("❌ No auth token available for users endpoint test")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                response = await client.get(
                    f"{self.base_url}/api/v1/users/",
                    headers=headers
                )
                
                if response.status_code == 200:
                    users = response.json()
                    print(f"✅ Users endpoint working - found {len(users)} users")
                    return True
                else:
                    print(f"❌ Users endpoint failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Users endpoint test failed: {e}")
            return False
    
    async def test_swagger_docs(self) -> bool:
        """Test Swagger documentation"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/docs")
                
                if response.status_code == 200:
                    print("✅ Swagger documentation accessible")
                    return True
                else:
                    print(f"❌ Swagger docs failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Swagger docs test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all validation tests"""
        print("🚀 Starting API validation tests...")
        print(f"Testing API at: {self.base_url}")
        print("-" * 50)
        
        tests = [
            ("Health Check", self.test_health),
            ("Swagger Documentation", self.test_swagger_docs),
            ("Login Endpoint", self.test_login),
            ("Protected Route", self.test_protected_route),
            ("Users Endpoint", self.test_users_endpoint),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            if await test_func():
                passed += 1
            else:
                print(f"   Test failed: {test_name}")
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! API is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
        
        return passed == total


async def main():
    """Main function"""
    validator = APIValidator()
    success = await validator.run_all_tests()
    
    if success:
        print("\n✅ API validation completed successfully!")
        print("🌐 Access your API documentation at: http://localhost:8000/docs")
    else:
        print("\n❌ API validation failed!")
        print("💡 Make sure the server is running: python main.py")


if __name__ == "__main__":
    asyncio.run(main())
