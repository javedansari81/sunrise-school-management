#!/usr/bin/env python3
"""
Integration test script for the Leave Management System
Tests the complete workflow from configuration endpoint to CRUD operations
"""

import asyncio
import aiohttp
import json
import sys
from datetime import date, datetime


class LeaveSystemTester:
    """Integration tester for the leave management system"""
    
    def __init__(self, base_url="http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.session = None
        self.auth_token = None
        self.test_results = []
    
    async def setup(self):
        """Setup test session and authentication"""
        self.session = aiohttp.ClientSession()
        
        # Login to get auth token (mock for now)
        self.auth_token = "test-token"
        print("✓ Test session initialized")
    
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
        print("✓ Test session cleaned up")
    
    def get_headers(self):
        """Get authentication headers"""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    async def test_configuration_endpoint(self):
        """Test configuration endpoint returns leave metadata"""
        print("\n🧪 Testing Configuration Endpoint...")
        
        try:
            async with self.session.get(
                f"{self.base_url}/configuration/",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check required leave metadata
                    required_keys = ['leave_types', 'leave_statuses']
                    
                    for key in required_keys:
                        if key in data:
                            print(f"  ✓ {key}: {len(data[key])} items")
                            
                            # Check if items have required fields
                            if data[key]:
                                item = data[key][0]
                                if 'id' in item and 'name' in item and 'is_active' in item:
                                    print(f"    ✓ {key} items have required fields")
                                else:
                                    print(f"    ✗ {key} items missing required fields")
                                    return False
                        else:
                            print(f"  ✗ Missing {key}")
                            return False
                    
                    self.test_results.append(("Configuration Endpoint", True))
                    return True
                else:
                    print(f"  ✗ Configuration endpoint failed: {response.status}")
                    if response.status == 404:
                        print("    This suggests the configuration endpoint is not accessible")
                        print("    Check if the backend is running and the endpoint is properly configured")
                    self.test_results.append(("Configuration Endpoint", False))
                    return False
                    
        except Exception as e:
            print(f"  ✗ Configuration test error: {e}")
            print("    This suggests the backend server is not running or not accessible")
            self.test_results.append(("Configuration Endpoint", False))
            return False
    
    async def test_leave_crud_operations(self):
        """Test complete CRUD operations for leave requests"""
        print("\n🧪 Testing Leave CRUD Operations...")
        
        # Test data
        leave_data = {
            "applicant_id": 1,
            "applicant_type": "student",
            "leave_type_id": 1,
            "start_date": "2024-02-15",
            "end_date": "2024-02-17",
            "total_days": 3,
            "reason": "Integration test leave request for CRUD operations"
        }
        
        leave_id = None
        
        try:
            # CREATE - Test leave creation
            print("  Testing CREATE operation...")
            async with self.session.post(
                f"{self.base_url}/leaves/",
                headers=self.get_headers(),
                json=leave_data
            ) as response:
                if response.status == 200:
                    created_leave = await response.json()
                    leave_id = created_leave["id"]
                    print(f"    ✓ Leave request created with ID: {leave_id}")
                else:
                    print(f"    ✗ Create failed: {response.status}")
                    error_text = await response.text()
                    print(f"    Error: {error_text}")
                    return False
            
            # READ - Test getting the created leave
            print("  Testing READ operation...")
            async with self.session.get(
                f"{self.base_url}/leaves/{leave_id}",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    leave = await response.json()
                    if leave["reason"] == leave_data["reason"]:
                        print("    ✓ Leave request retrieved successfully")
                    else:
                        print("    ✗ Retrieved leave data mismatch")
                        return False
                else:
                    print(f"    ✗ Read failed: {response.status}")
                    return False
            
            # UPDATE - Test updating the leave
            print("  Testing UPDATE operation...")
            update_data = {
                "reason": "Updated integration test leave request",
                "total_days": 2
            }
            
            async with self.session.put(
                f"{self.base_url}/leaves/{leave_id}",
                headers=self.get_headers(),
                json=update_data
            ) as response:
                if response.status == 200:
                    updated_leave = await response.json()
                    if updated_leave["reason"] == update_data["reason"]:
                        print("    ✓ Leave request updated successfully")
                    else:
                        print("    ✗ Update data mismatch")
                        return False
                else:
                    print(f"    ✗ Update failed: {response.status}")
                    return False
            
            # APPROVE - Test leave approval
            print("  Testing APPROVE operation...")
            approval_data = {
                "leave_status_id": 2,  # Approved
                "review_comments": "Integration test approval"
            }
            
            async with self.session.patch(
                f"{self.base_url}/leaves/{leave_id}/approve",
                headers=self.get_headers(),
                json=approval_data
            ) as response:
                if response.status == 200:
                    approved_leave = await response.json()
                    if approved_leave["leave_status_id"] == 2:
                        print("    ✓ Leave request approved successfully")
                    else:
                        print("    ✗ Approval status not updated")
                        return False
                else:
                    print(f"    ✗ Approval failed: {response.status}")
                    return False
            
            # DELETE - Test leave deletion (create a new one first since approved ones can't be deleted)
            print("  Testing DELETE operation...")
            
            # Create a new leave for deletion
            delete_leave_data = {**leave_data, "reason": "Leave for deletion test"}
            async with self.session.post(
                f"{self.base_url}/leaves/",
                headers=self.get_headers(),
                json=delete_leave_data
            ) as response:
                if response.status == 200:
                    delete_leave = await response.json()
                    delete_leave_id = delete_leave["id"]
                    
                    # Now delete it
                    async with self.session.delete(
                        f"{self.base_url}/leaves/{delete_leave_id}",
                        headers=self.get_headers()
                    ) as delete_response:
                        if delete_response.status == 200:
                            print("    ✓ Leave request deleted successfully")
                        else:
                            print(f"    ✗ Delete failed: {delete_response.status}")
                            return False
                else:
                    print("    ✗ Could not create leave for deletion test")
                    return False
            
            self.test_results.append(("Leave CRUD Operations", True))
            return True
            
        except Exception as e:
            print(f"  ✗ CRUD test error: {e}")
            self.test_results.append(("Leave CRUD Operations", False))
            return False
    
    async def test_leave_filtering(self):
        """Test leave filtering functionality"""
        print("\n🧪 Testing Leave Filtering...")
        
        try:
            # Test basic filtering
            filters = {
                "applicant_type": "student",
                "page": 1,
                "per_page": 10
            }
            
            async with self.session.get(
                f"{self.base_url}/leaves/",
                headers=self.get_headers(),
                params=filters
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check response structure
                    required_keys = ["leaves", "total", "page", "per_page", "total_pages"]
                    for key in required_keys:
                        if key not in data:
                            print(f"    ✗ Missing key in response: {key}")
                            return False
                    
                    print(f"    ✓ Filtering returned {len(data['leaves'])} leave requests")
                    print(f"    ✓ Total leave requests: {data['total']}")
                    
                    self.test_results.append(("Leave Filtering", True))
                    return True
                else:
                    print(f"    ✗ Filtering failed: {response.status}")
                    self.test_results.append(("Leave Filtering", False))
                    return False
                    
        except Exception as e:
            print(f"  ✗ Filtering test error: {e}")
            self.test_results.append(("Leave Filtering", False))
            return False
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("🧪 LEAVE MANAGEMENT SYSTEM TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)
        
        for test_name, result in self.test_results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status:<8} {test_name}")
        
        print("-"*60)
        print(f"TOTAL: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Leave management system is working correctly.")
            return True
        else:
            print("❌ Some tests failed. Please check the system configuration.")
            if passed == 0:
                print("\n💡 TROUBLESHOOTING TIPS:")
                print("   1. Make sure the backend server is running on http://localhost:8000")
                print("   2. Check if the configuration endpoint is accessible")
                print("   3. Verify that leave management endpoints are properly configured")
                print("   4. Ensure the database has the required metadata tables")
            return False


async def main():
    """Main test runner"""
    print("🚀 Starting Leave Management System Integration Tests")
    print("="*60)
    
    tester = LeaveSystemTester()
    
    try:
        await tester.setup()
        
        # Run all tests
        tests = [
            tester.test_configuration_endpoint(),
            tester.test_leave_crud_operations(),
            tester.test_leave_filtering()
        ]
        
        # Execute tests
        for test in tests:
            await test
        
        # Print summary
        success = tester.print_summary()
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ Test runner error: {e}")
        return 1
    
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
