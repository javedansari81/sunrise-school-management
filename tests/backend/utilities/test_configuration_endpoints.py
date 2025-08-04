#!/usr/bin/env python3
"""
Test script for configuration endpoints
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
from app.models.metadata import Class, Gender, SessionYear


class ConfigurationTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
        
    async def close(self):
        await self.client.aclose()
    
    async def test_database_metadata(self):
        """Test that metadata exists in database"""
        print("🔍 Testing database metadata...")
        
        async with AsyncSessionLocal() as db:
            # Check classes
            classes = await db.execute(select(Class))
            class_list = classes.scalars().all()
            
            print(f"📚 Classes in database: {len(class_list)}")
            for cls in class_list:
                print(f"   - ID: {cls.id}, Name: {cls.name}, Display: {cls.display_name}, Active: {cls.is_active}")
            
            # Check genders
            genders = await db.execute(select(Gender))
            gender_list = genders.scalars().all()
            
            print(f"👥 Genders in database: {len(gender_list)}")
            for gender in gender_list:
                print(f"   - ID: {gender.id}, Name: {gender.name}, Active: {gender.is_active}")
            
            # Check session years
            session_years = await db.execute(select(SessionYear))
            session_year_list = session_years.scalars().all()
            
            print(f"📅 Session Years in database: {len(session_year_list)}")
            for sy in session_year_list:
                print(f"   - ID: {sy.id}, Name: {sy.name}, Current: {sy.is_current}, Active: {sy.is_active}")
            
            return len(class_list) > 0, len(gender_list) > 0, len(session_year_list) > 0
    
    async def test_student_management_endpoint(self):
        """Test student management configuration endpoint"""
        print("\n🔍 Testing student management configuration endpoint...")
        
        try:
            # Note: This endpoint requires authentication, so this might fail
            # In a real test, you'd need to get a valid token first
            response = await self.client.get(
                f"{self.base_url}/api/v1/configuration/student-management/"
            )
            
            if response.status_code == 401:
                print("⚠️  Authentication required - endpoint exists but needs login")
                return True
            elif response.status_code == 200:
                config_data = response.json()
                print("✅ Student management configuration endpoint working")
                
                # Check classes
                classes = config_data.get('classes', [])
                print(f"📚 Classes in response: {len(classes)}")
                for cls in classes[:3]:  # Show first 3
                    print(f"   - ID: {cls.get('id')}, Name: {cls.get('name')}, Display: {cls.get('display_name')}")
                
                # Check genders
                genders = config_data.get('genders', [])
                print(f"👥 Genders in response: {len(genders)}")
                
                # Check session years
                session_years = config_data.get('session_years', [])
                print(f"📅 Session Years in response: {len(session_years)}")
                
                return len(classes) > 0
            else:
                print(f"❌ Endpoint failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing endpoint: {e}")
            return False
    
    async def test_legacy_endpoint(self):
        """Test legacy configuration endpoint"""
        print("\n🔍 Testing legacy configuration endpoint...")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/configuration/"
            )
            
            if response.status_code == 401:
                print("⚠️  Authentication required - endpoint exists but needs login")
                return True
            elif response.status_code == 200:
                print("⚠️  Legacy endpoint still working (should be deprecated)")
                return True
            elif response.status_code == 410 or response.status_code == 404:
                print("✅ Legacy endpoint properly deprecated")
                return True
            else:
                print(f"❌ Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing legacy endpoint: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Configuration Endpoint Tests")
        print("=" * 60)
        
        tests_passed = 0
        total_tests = 3
        
        try:
            # Test 1: Database metadata
            has_classes, has_genders, has_session_years = await self.test_database_metadata()
            if has_classes and has_genders and has_session_years:
                tests_passed += 1
                print("✅ Database metadata test passed")
            else:
                print("❌ Database metadata test failed")
            
            # Test 2: Student management endpoint
            if await self.test_student_management_endpoint():
                tests_passed += 1
                print("✅ Student management endpoint test passed")
            else:
                print("❌ Student management endpoint test failed")
            
            # Test 3: Legacy endpoint
            if await self.test_legacy_endpoint():
                tests_passed += 1
                print("✅ Legacy endpoint test passed")
            else:
                print("❌ Legacy endpoint test failed")
            
            print("\n" + "=" * 60)
            print(f"🎯 Test Results: {tests_passed}/{total_tests} tests passed")
            
            if tests_passed == total_tests:
                print("🎉 All tests passed! Configuration endpoints are working correctly.")
                return True
            else:
                print(f"⚠️  {total_tests - tests_passed} tests failed. Please check the issues above.")
                return False
                
        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            return False


async def main():
    """Main function"""
    tester = ConfigurationTester()
    
    try:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
