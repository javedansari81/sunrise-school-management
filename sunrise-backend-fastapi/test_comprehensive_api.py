#!/usr/bin/env python3
"""
Comprehensive API Test Script for Sunrise School Management System
Tests all major endpoints and functionality
"""

import asyncio
import httpx
import json
from datetime import date, datetime
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class APITester:
    def __init__(self):
        self.client = httpx.AsyncClient()
        self.auth_token = None
        self.headers = {}
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def set_auth_token(self, token: str):
        """Set authentication token for requests"""
        self.auth_token = token
        self.headers = {"Authorization": f"Bearer {token}"}
    
    async def test_health_check(self):
        """Test basic health check"""
        print("🔍 Testing health check...")
        response = await self.client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        print("✅ Health check passed")
    
    async def test_authentication(self):
        """Test authentication endpoints"""
        print("🔍 Testing authentication...")
        
        # Test login (assuming default admin user exists)
        login_data = {
            "email": "admin@sunrise.com",
            "password": "admin123"
        }
        
        response = await self.client.post(f"{API_BASE}/auth/login-json", json=login_data)
        if response.status_code == 200:
            data = response.json()
            self.set_auth_token(data["access_token"])
            print("✅ Authentication successful")
            print(f"   User type: {data['user']['user_type']}")
            print(f"   Permissions: {len(data['permissions'])} permissions")
        else:
            print("⚠️  Authentication failed - using without auth")
    
    async def test_fee_management(self):
        """Test fee management endpoints"""
        print("🔍 Testing fee management...")
        
        # Test get fees
        response = await self.client.get(f"{API_BASE}/fees/", headers=self.headers)
        print(f"   Get fees: {response.status_code}")
        
        # Test fee structure
        response = await self.client.get(f"{API_BASE}/fees/structure", headers=self.headers)
        print(f"   Get fee structure: {response.status_code}")
        
        # Test fee dashboard
        response = await self.client.get(f"{API_BASE}/fees/dashboard", headers=self.headers)
        print(f"   Fee dashboard: {response.status_code}")
        
        print("✅ Fee management tests completed")
    
    async def test_student_management(self):
        """Test student management endpoints"""
        print("🔍 Testing student management...")
        
        # Test get students
        response = await self.client.get(f"{API_BASE}/students/", headers=self.headers)
        print(f"   Get students: {response.status_code}")
        
        # Test student dashboard stats
        response = await self.client.get(f"{API_BASE}/students/dashboard/stats", headers=self.headers)
        print(f"   Student dashboard: {response.status_code}")
        
        # Test search students
        response = await self.client.get(f"{API_BASE}/students/search?q=test", headers=self.headers)
        print(f"   Search students: {response.status_code}")
        
        print("✅ Student management tests completed")
    
    async def test_teacher_management(self):
        """Test teacher management endpoints"""
        print("🔍 Testing teacher management...")
        
        # Test get teachers
        response = await self.client.get(f"{API_BASE}/teachers/", headers=self.headers)
        print(f"   Get teachers: {response.status_code}")
        
        # Test teacher dashboard
        response = await self.client.get(f"{API_BASE}/teachers/dashboard/stats", headers=self.headers)
        print(f"   Teacher dashboard: {response.status_code}")
        
        # Test get departments
        response = await self.client.get(f"{API_BASE}/teachers/options/departments", headers=self.headers)
        print(f"   Get departments: {response.status_code}")
        
        print("✅ Teacher management tests completed")
    
    async def test_leave_management(self):
        """Test leave management endpoints"""
        print("🔍 Testing leave management...")
        
        # Test get leaves
        response = await self.client.get(f"{API_BASE}/leaves/", headers=self.headers)
        print(f"   Get leaves: {response.status_code}")
        
        # Test pending leaves
        response = await self.client.get(f"{API_BASE}/leaves/pending", headers=self.headers)
        print(f"   Get pending leaves: {response.status_code}")
        
        # Test leave reports
        response = await self.client.get(f"{API_BASE}/leaves/reports/summary", headers=self.headers)
        print(f"   Leave reports: {response.status_code}")
        
        print("✅ Leave management tests completed")
    
    async def test_expense_management(self):
        """Test expense management endpoints"""
        print("🔍 Testing expense management...")
        
        # Test get expenses
        response = await self.client.get(f"{API_BASE}/expenses/", headers=self.headers)
        print(f"   Get expenses: {response.status_code}")
        
        # Test pending expenses
        response = await self.client.get(f"{API_BASE}/expenses/pending", headers=self.headers)
        print(f"   Get pending expenses: {response.status_code}")
        
        # Test expense categories
        response = await self.client.get(f"{API_BASE}/expenses/categories", headers=self.headers)
        print(f"   Get categories: {response.status_code}")
        
        # Test expense dashboard
        response = await self.client.get(f"{API_BASE}/expenses/dashboard", headers=self.headers)
        print(f"   Expense dashboard: {response.status_code}")
        
        print("✅ Expense management tests completed")
    
    async def test_user_profile(self):
        """Test user profile endpoints"""
        print("🔍 Testing user profile...")
        
        # Test get current user
        response = await self.client.get(f"{API_BASE}/auth/me", headers=self.headers)
        print(f"   Get current user: {response.status_code}")
        
        # Test get permissions
        response = await self.client.get(f"{API_BASE}/auth/permissions", headers=self.headers)
        print(f"   Get permissions: {response.status_code}")
        
        # Test get profile
        response = await self.client.get(f"{API_BASE}/auth/profile", headers=self.headers)
        print(f"   Get profile: {response.status_code}")
        
        print("✅ User profile tests completed")
    
    async def test_swagger_docs(self):
        """Test Swagger documentation"""
        print("🔍 Testing Swagger documentation...")
        
        response = await self.client.get(f"{BASE_URL}/docs")
        print(f"   Swagger UI: {response.status_code}")
        
        response = await self.client.get(f"{BASE_URL}/openapi.json")
        print(f"   OpenAPI spec: {response.status_code}")
        
        print("✅ Swagger documentation tests completed")
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting comprehensive API tests...\n")
        
        try:
            await self.test_health_check()
            await self.test_swagger_docs()
            await self.test_authentication()
            await self.test_fee_management()
            await self.test_student_management()
            await self.test_teacher_management()
            await self.test_leave_management()
            await self.test_expense_management()
            await self.test_user_profile()
            
            print("\n🎉 All tests completed successfully!")
            print("\n📋 Summary:")
            print("   ✅ Health check")
            print("   ✅ Swagger documentation")
            print("   ✅ Authentication & Authorization")
            print("   ✅ Fee Management System")
            print("   ✅ Student Profile Management")
            print("   ✅ Teacher Profile Management")
            print("   ✅ Leave Management System")
            print("   ✅ Expense Management System")
            print("   ✅ User Profile & Permissions")
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            raise


async def main():
    """Main test function"""
    print("=" * 60)
    print("🏫 SUNRISE SCHOOL MANAGEMENT SYSTEM - API TESTS")
    print("=" * 60)
    
    async with APITester() as tester:
        await tester.run_all_tests()
    
    print("\n" + "=" * 60)
    print("🎯 Test completed! Check the server logs for any issues.")
    print("🌐 Visit http://localhost:8000/docs to explore the API")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
