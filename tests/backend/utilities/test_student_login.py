#!/usr/bin/env python3
"""
Test script for student login functionality
"""
import asyncio
import sys
from pathlib import Path
import httpx
import json

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.student import Student
from app.crud.crud_user import CRUDUser


class StudentLoginTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
        self.user_crud = CRUDUser()
        
    async def close(self):
        await self.client.aclose()
    
    async def test_database_setup(self):
        """Test that students have user accounts in database"""
        print("🔍 Testing database setup...")
        
        async with AsyncSessionLocal() as db:
            # Check students with user accounts
            students_with_users = await db.execute(
                select(Student).where(Student.user_id.is_not(None))
            )
            students = students_with_users.scalars().all()
            
            if not students:
                print("❌ No students with user accounts found!")
                return False
            
            print(f"✅ Found {len(students)} students with user accounts")
            
            # Test a sample student
            sample_student = students[0]
            user = await db.execute(
                select(User).where(User.id == sample_student.user_id)
            )
            user_obj = user.scalar_one_or_none()
            
            if not user_obj:
                print(f"❌ User account not found for student {sample_student.admission_number}")
                return False
            
            print(f"✅ Sample student verification:")
            print(f"   📚 Student: {sample_student.first_name} {sample_student.last_name}")
            print(f"   📧 Email: {user_obj.email}")
            print(f"   📱 Phone: {user_obj.phone or 'Not provided'}")
            print(f"   👤 User Type: {user_obj.user_type_id}")
            
            return True
    
    async def test_authentication_crud(self):
        """Test the enhanced authentication CRUD methods"""
        print("\n🔍 Testing authentication CRUD...")
        
        async with AsyncSessionLocal() as db:
            # Get a student user for testing
            student_user = await db.execute(
                select(User).join(Student).where(Student.user_id == User.id).limit(1)
            )
            user = student_user.scalar_one_or_none()
            
            if not user:
                print("❌ No student user found for testing")
                return False
            
            # Test email authentication
            print(f"🧪 Testing email authentication for: {user.email}")
            auth_result = await self.user_crud.authenticate(
                db, email=user.email, password="Sunrise@001"
            )
            
            if not auth_result:
                print("❌ Email authentication failed")
                return False
            
            print("✅ Email authentication successful")

            # Note: Phone authentication has been removed for security purposes
            # Only email authentication is now supported

            return True
    
    async def test_login_endpoint(self):
        """Test the login endpoint with student credentials"""
        print("\n🔍 Testing login endpoint...")
        
        async with AsyncSessionLocal() as db:
            # Get a student user for testing
            student_user = await db.execute(
                select(User).join(Student).where(Student.user_id == User.id).limit(1)
            )
            user = student_user.scalar_one_or_none()
            
            if not user:
                print("❌ No student user found for testing")
                return False, None
            
            # Test login with email
            login_data = {
                "email": user.email,
                "password": "Sunrise@001"
            }
            
            try:
                response = await self.client.post(
                    f"{self.base_url}/api/v1/auth/login-json",
                    json=login_data
                )
                
                if response.status_code != 200:
                    print(f"❌ Login failed with status {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False, None
                
                login_response = response.json()
                print("✅ Login endpoint successful")
                print(f"   👤 User: {login_response['user']['first_name']} {login_response['user']['last_name']}")
                print(f"   🎭 Role: {login_response['user']['user_type']}")
                print(f"   🔑 Token received: {bool(login_response.get('access_token'))}")
                
                return True, login_response.get('access_token')
                
            except Exception as e:
                print(f"❌ Login endpoint error: {e}")
                return False, None
    
    async def test_student_profile_endpoints(self, token):
        """Test student profile endpoints"""
        print("\n🔍 Testing student profile endpoints...")
        
        if not token:
            print("❌ No token available for testing")
            return False
        
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            # Test GET profile
            response = await self.client.get(
                f"{self.base_url}/api/v1/students/my-profile",
                headers=headers
            )
            
            if response.status_code != 200:
                print(f"❌ Get profile failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                return False
            
            profile_data = response.json()
            print("✅ Get profile endpoint successful")
            print(f"   📚 Student: {profile_data['first_name']} {profile_data['last_name']}")
            print(f"   🎓 Admission: {profile_data['admission_number']}")
            print(f"   🏫 Class: {profile_data.get('class_name', 'N/A')}")
            
            # Test PUT profile (update)
            update_data = {
                "emergency_contact_name": "Test Emergency Contact",
                "emergency_contact_phone": "9999999999"
            }
            
            response = await self.client.put(
                f"{self.base_url}/api/v1/students/my-profile",
                headers=headers,
                json=update_data
            )
            
            if response.status_code != 200:
                print(f"❌ Update profile failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                return False
            
            print("✅ Update profile endpoint successful")
            return True
            
        except Exception as e:
            print(f"❌ Profile endpoints error: {e}")
            return False
    
    async def test_security_restrictions(self, token):
        """Test that students cannot access admin endpoints"""
        print("\n🔍 Testing security restrictions...")
        
        if not token:
            print("❌ No token available for testing")
            return False
        
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            # Try to access admin student list (should fail)
            response = await self.client.get(
                f"{self.base_url}/api/v1/students/",
                headers=headers
            )
            
            if response.status_code == 200:
                print("❌ Student was able to access admin endpoint (security issue!)")
                return False
            
            print("✅ Student correctly blocked from admin endpoints")
            return True
            
        except Exception as e:
            print(f"❌ Security test error: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Student Login Functionality Tests")
        print("=" * 60)
        
        tests_passed = 0
        total_tests = 5
        
        try:
            # Test 1: Database setup
            if await self.test_database_setup():
                tests_passed += 1
            
            # Test 2: Authentication CRUD
            if await self.test_authentication_crud():
                tests_passed += 1
            
            # Test 3: Login endpoint
            login_success, token = await self.test_login_endpoint()
            if login_success:
                tests_passed += 1
            
            # Test 4: Student profile endpoints
            if await self.test_student_profile_endpoints(token):
                tests_passed += 1
            
            # Test 5: Security restrictions
            if await self.test_security_restrictions(token):
                tests_passed += 1
            
            print("\n" + "=" * 60)
            print(f"🎯 Test Results: {tests_passed}/{total_tests} tests passed")
            
            if tests_passed == total_tests:
                print("🎉 All tests passed! Student login functionality is working correctly.")
                return True
            else:
                print(f"⚠️  {total_tests - tests_passed} tests failed. Please check the issues above.")
                return False
                
        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            return False


async def main():
    """Main function"""
    tester = StudentLoginTester()
    
    try:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
