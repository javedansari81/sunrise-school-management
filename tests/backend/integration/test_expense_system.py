#!/usr/bin/env python3
"""
Comprehensive integration test script for the expense management system
Tests the complete workflow from database to API to frontend
"""

import asyncio
import aiohttp
import json
import sys
from datetime import date, datetime
from decimal import Decimal


class ExpenseSystemTester:
    """Integration tester for the expense management system"""
    
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
        """Test configuration endpoint returns metadata"""
        print("\n🧪 Testing Configuration Endpoint...")
        
        try:
            async with self.session.get(
                f"{self.base_url}/configuration/",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check required metadata
                    required_keys = [
                        'expense_categories', 'expense_statuses', 
                        'payment_methods', 'session_years'
                    ]
                    
                    for key in required_keys:
                        if key in data:
                            print(f"  ✓ {key}: {len(data[key])} items")
                        else:
                            print(f"  ✗ Missing {key}")
                            return False
                    
                    self.test_results.append(("Configuration Endpoint", True))
                    return True
                else:
                    print(f"  ✗ Configuration endpoint failed: {response.status}")
                    self.test_results.append(("Configuration Endpoint", False))
                    return False
                    
        except Exception as e:
            print(f"  ✗ Configuration test error: {e}")
            self.test_results.append(("Configuration Endpoint", False))
            return False
    
    async def test_expense_crud_operations(self):
        """Test complete CRUD operations for expenses"""
        print("\n🧪 Testing Expense CRUD Operations...")
        
        # Test data
        expense_data = {
            "expense_date": "2024-01-15",
            "expense_category_id": 1,
            "subcategory": "Test Equipment",
            "description": "Integration test expense for CRUD operations",
            "amount": 5000.00,
            "tax_amount": 900.00,
            "total_amount": 5900.00,
            "currency": "INR",
            "vendor_name": "Test Vendor Ltd",
            "vendor_contact": "9876543210",
            "vendor_email": "test@vendor.com",
            "payment_method_id": 1,
            "payment_reference": "TEST001",
            "priority": "Medium",
            "is_emergency": False,
            "is_recurring": False
        }
        
        expense_id = None
        
        try:
            # CREATE - Test expense creation
            print("  Testing CREATE operation...")
            async with self.session.post(
                f"{self.base_url}/expenses/",
                headers=self.get_headers(),
                json=expense_data
            ) as response:
                if response.status == 200:
                    created_expense = await response.json()
                    expense_id = created_expense["id"]
                    print(f"    ✓ Expense created with ID: {expense_id}")
                else:
                    print(f"    ✗ Create failed: {response.status}")
                    error_text = await response.text()
                    print(f"    Error: {error_text}")
                    return False
            
            # READ - Test getting the created expense
            print("  Testing READ operation...")
            async with self.session.get(
                f"{self.base_url}/expenses/{expense_id}",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    expense = await response.json()
                    if expense["description"] == expense_data["description"]:
                        print("    ✓ Expense retrieved successfully")
                    else:
                        print("    ✗ Retrieved expense data mismatch")
                        return False
                else:
                    print(f"    ✗ Read failed: {response.status}")
                    return False
            
            # UPDATE - Test updating the expense
            print("  Testing UPDATE operation...")
            update_data = {
                "description": "Updated integration test expense",
                "amount": 6000.00,
                "tax_amount": 1080.00,
                "total_amount": 7080.00
            }
            
            async with self.session.put(
                f"{self.base_url}/expenses/{expense_id}",
                headers=self.get_headers(),
                json=update_data
            ) as response:
                if response.status == 200:
                    updated_expense = await response.json()
                    if updated_expense["description"] == update_data["description"]:
                        print("    ✓ Expense updated successfully")
                    else:
                        print("    ✗ Update data mismatch")
                        return False
                else:
                    print(f"    ✗ Update failed: {response.status}")
                    return False
            
            # APPROVE - Test expense approval
            print("  Testing APPROVE operation...")
            approval_data = {
                "expense_status_id": 2,  # Approved
                "approval_comments": "Integration test approval"
            }
            
            async with self.session.patch(
                f"{self.base_url}/expenses/{expense_id}/approve",
                headers=self.get_headers(),
                json=approval_data
            ) as response:
                if response.status == 200:
                    approved_expense = await response.json()
                    if approved_expense["expense_status_id"] == 2:
                        print("    ✓ Expense approved successfully")
                    else:
                        print("    ✗ Approval status not updated")
                        return False
                else:
                    print(f"    ✗ Approval failed: {response.status}")
                    return False
            
            # DELETE - Test expense deletion (create a new one first since approved ones can't be deleted)
            print("  Testing DELETE operation...")
            
            # Create a new expense for deletion
            delete_expense_data = {**expense_data, "description": "Expense for deletion test"}
            async with self.session.post(
                f"{self.base_url}/expenses/",
                headers=self.get_headers(),
                json=delete_expense_data
            ) as response:
                if response.status == 200:
                    delete_expense = await response.json()
                    delete_expense_id = delete_expense["id"]
                    
                    # Now delete it
                    async with self.session.delete(
                        f"{self.base_url}/expenses/{delete_expense_id}",
                        headers=self.get_headers()
                    ) as delete_response:
                        if delete_response.status == 200:
                            print("    ✓ Expense deleted successfully")
                        else:
                            print(f"    ✗ Delete failed: {delete_response.status}")
                            return False
                else:
                    print("    ✗ Could not create expense for deletion test")
                    return False
            
            self.test_results.append(("Expense CRUD Operations", True))
            return True
            
        except Exception as e:
            print(f"  ✗ CRUD test error: {e}")
            self.test_results.append(("Expense CRUD Operations", False))
            return False
    
    async def test_expense_filtering(self):
        """Test expense filtering functionality"""
        print("\n🧪 Testing Expense Filtering...")
        
        try:
            # Test basic filtering
            filters = {
                "expense_category_id": 1,
                "page": 1,
                "per_page": 10
            }
            
            async with self.session.get(
                f"{self.base_url}/expenses/",
                headers=self.get_headers(),
                params=filters
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check response structure
                    required_keys = ["expenses", "total", "page", "per_page", "total_pages", "summary"]
                    for key in required_keys:
                        if key not in data:
                            print(f"    ✗ Missing key in response: {key}")
                            return False
                    
                    print(f"    ✓ Filtering returned {len(data['expenses'])} expenses")
                    print(f"    ✓ Total expenses: {data['total']}")
                    
                    self.test_results.append(("Expense Filtering", True))
                    return True
                else:
                    print(f"    ✗ Filtering failed: {response.status}")
                    self.test_results.append(("Expense Filtering", False))
                    return False
                    
        except Exception as e:
            print(f"  ✗ Filtering test error: {e}")
            self.test_results.append(("Expense Filtering", False))
            return False
    
    async def test_expense_statistics(self):
        """Test expense statistics endpoint"""
        print("\n🧪 Testing Expense Statistics...")
        
        try:
            async with self.session.get(
                f"{self.base_url}/expenses/statistics",
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    stats = await response.json()
                    
                    # Check required statistics
                    required_stats = [
                        "total_expenses", "approved_expenses", "pending_expenses", 
                        "rejected_expenses", "total_amount", "category_breakdown"
                    ]
                    
                    for stat in required_stats:
                        if stat in stats:
                            print(f"    ✓ {stat}: {stats[stat]}")
                        else:
                            print(f"    ✗ Missing statistic: {stat}")
                            return False
                    
                    self.test_results.append(("Expense Statistics", True))
                    return True
                else:
                    print(f"    ✗ Statistics failed: {response.status}")
                    self.test_results.append(("Expense Statistics", False))
                    return False
                    
        except Exception as e:
            print(f"  ✗ Statistics test error: {e}")
            self.test_results.append(("Expense Statistics", False))
            return False
    
    async def test_vendor_management(self):
        """Test vendor management functionality"""
        print("\n🧪 Testing Vendor Management...")
        
        vendor_data = {
            "vendor_name": "Integration Test Vendor",
            "vendor_code": "ITV001",
            "contact_person": "Test Contact",
            "phone": "9876543210",
            "email": "test@integrationvendor.com",
            "address_line1": "123 Test Street",
            "city": "Test City",
            "state": "Test State",
            "postal_code": "123456",
            "country": "India",
            "gst_number": "27TEST1234G1H2",
            "is_active": True,
            "credit_limit": 50000.00,
            "credit_days": 30
        }
        
        try:
            # Create vendor
            async with self.session.post(
                f"{self.base_url}/expenses/vendors/",
                headers=self.get_headers(),
                json=vendor_data
            ) as response:
                if response.status == 200:
                    vendor = await response.json()
                    print(f"    ✓ Vendor created: {vendor['vendor_name']}")
                    
                    # Get active vendors
                    async with self.session.get(
                        f"{self.base_url}/expenses/vendors/active",
                        headers=self.get_headers()
                    ) as get_response:
                        if get_response.status == 200:
                            vendors = await get_response.json()
                            print(f"    ✓ Retrieved {len(vendors)} active vendors")
                            
                            self.test_results.append(("Vendor Management", True))
                            return True
                        else:
                            print(f"    ✗ Get vendors failed: {get_response.status}")
                            return False
                else:
                    print(f"    ✗ Vendor creation failed: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"  ✗ Vendor management test error: {e}")
            self.test_results.append(("Vendor Management", False))
            return False
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("🧪 EXPENSE MANAGEMENT SYSTEM TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)
        
        for test_name, result in self.test_results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status:<8} {test_name}")
        
        print("-"*60)
        print(f"TOTAL: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Expense management system is working correctly.")
            return True
        else:
            print("❌ Some tests failed. Please check the system configuration.")
            return False


async def main():
    """Main test runner"""
    print("🚀 Starting Expense Management System Integration Tests")
    print("="*60)
    
    tester = ExpenseSystemTester()
    
    try:
        await tester.setup()
        
        # Run all tests
        tests = [
            tester.test_configuration_endpoint(),
            tester.test_expense_crud_operations(),
            tester.test_expense_filtering(),
            tester.test_expense_statistics(),
            tester.test_vendor_management()
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
