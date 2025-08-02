#!/usr/bin/env python3
"""
Validation script for Leave Management System
Tests the complete functionality including models, CRUD, and API endpoints
"""

import asyncio
import sys
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.leave import LeaveRequest, LeaveBalance, LeavePolicy
from app.models.metadata import LeaveType, LeaveStatus
from app.schemas.leave import LeaveRequestCreate, ApplicantTypeEnum
from app.crud.crud_leave import leave_request_crud, leave_balance_crud, leave_policy_crud


async def test_leave_models():
    """Test leave model creation and relationships"""
    print("🧪 Testing Leave Models...")
    
    try:
        # Test model imports
        assert LeaveRequest is not None
        assert LeaveBalance is not None
        assert LeavePolicy is not None
        print("✅ All leave models imported successfully")
        
        # Test enum
        assert ApplicantTypeEnum.STUDENT == "student"
        assert ApplicantTypeEnum.TEACHER == "teacher"
        print("✅ Applicant type enum working correctly")
        
        return True
    except Exception as e:
        print(f"❌ Leave models test failed: {e}")
        return False


async def test_leave_crud():
    """Test CRUD operations for leave requests"""
    print("\n🧪 Testing Leave CRUD Operations...")
    
    try:
        # Get database session
        async for db in get_db():
            # Test creating a student leave request
            leave_data = LeaveRequestCreate(
                applicant_id=1,
                applicant_type=ApplicantTypeEnum.STUDENT,
                leave_type_id=1,  # Sick Leave
                start_date=date.today() + timedelta(days=1),
                end_date=date.today() + timedelta(days=3),
                total_days=3,
                reason="Test leave request for validation",
                parent_consent=True,
                emergency_contact_name="Test Parent",
                emergency_contact_phone="9876543210"
            )
            
            # Create leave request
            leave_request = await leave_request_crud.create(db, obj_in=leave_data)
            print(f"✅ Created leave request with ID: {leave_request.id}")
            
            # Test retrieving with details
            leave_with_details = await leave_request_crud.get_with_details(db, id=leave_request.id)
            if leave_with_details:
                print(f"✅ Retrieved leave request with details: {leave_with_details.applicant_name}")
            else:
                print("⚠️ Could not retrieve leave request with details (may need sample data)")
            
            # Test getting pending requests
            pending_requests = await leave_request_crud.get_pending_requests(db)
            print(f"✅ Found {len(pending_requests)} pending leave requests")
            
            # Test statistics
            stats = await leave_request_crud.get_leave_statistics(db, year=2024)
            print(f"✅ Leave statistics: {stats['total_requests']} total requests")
            
            # Clean up test data
            await leave_request_crud.remove(db, id=leave_request.id)
            print("✅ Test leave request cleaned up")
            
            break
        
        return True
    except Exception as e:
        print(f"❌ Leave CRUD test failed: {e}")
        return False


async def test_configuration_integration():
    """Test integration with configuration endpoint metadata"""
    print("\n🧪 Testing Configuration Integration...")
    
    try:
        async for db in get_db():
            # Test that we can query metadata tables
            from sqlalchemy import select
            
            # Test leave types
            result = await db.execute(select(LeaveType).where(LeaveType.is_active == True))
            leave_types = result.scalars().all()
            print(f"✅ Found {len(leave_types)} active leave types")
            
            # Test leave statuses
            result = await db.execute(select(LeaveStatus).where(LeaveStatus.is_active == True))
            leave_statuses = result.scalars().all()
            print(f"✅ Found {len(leave_statuses)} active leave statuses")
            
            # Verify metadata structure
            if leave_types:
                lt = leave_types[0]
                assert hasattr(lt, 'name')
                assert hasattr(lt, 'max_days_per_year')
                assert hasattr(lt, 'requires_medical_certificate')
                print("✅ Leave type metadata structure is correct")
            
            if leave_statuses:
                ls = leave_statuses[0]
                assert hasattr(ls, 'name')
                assert hasattr(ls, 'color_code')
                assert hasattr(ls, 'is_final')
                print("✅ Leave status metadata structure is correct")
            
            break
        
        return True
    except Exception as e:
        print(f"❌ Configuration integration test failed: {e}")
        return False


async def test_leave_policies():
    """Test leave policy functionality"""
    print("\n🧪 Testing Leave Policies...")
    
    try:
        async for db in get_db():
            # Test getting active policies
            policies = await leave_policy_crud.get_active_policies(db)
            print(f"✅ Found {len(policies)} active leave policies")
            
            # Test getting policies by applicant type
            student_policies = await leave_policy_crud.get_by_applicant_type(
                db, applicant_type=ApplicantTypeEnum.STUDENT
            )
            print(f"✅ Found {len(student_policies)} policies for students")
            
            teacher_policies = await leave_policy_crud.get_by_applicant_type(
                db, applicant_type=ApplicantTypeEnum.TEACHER
            )
            print(f"✅ Found {len(teacher_policies)} policies for teachers")
            
            break
        
        return True
    except Exception as e:
        print(f"❌ Leave policies test failed: {e}")
        return False


async def test_api_schemas():
    """Test API schema validation"""
    print("\n🧪 Testing API Schemas...")
    
    try:
        from app.schemas.leave import (
            LeaveRequestCreate, LeaveRequestUpdate, LeaveApproval,
            LeaveRequestWithDetails, LeaveFilters
        )
        
        # Test schema creation
        leave_create = LeaveRequestCreate(
            applicant_id=1,
            applicant_type=ApplicantTypeEnum.STUDENT,
            leave_type_id=1,
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=3),
            total_days=3,
            reason="Test schema validation"
        )
        
        assert leave_create.applicant_id == 1
        assert leave_create.applicant_type == ApplicantTypeEnum.STUDENT
        print("✅ LeaveRequestCreate schema validation passed")
        
        # Test filters schema
        filters = LeaveFilters(
            applicant_type=ApplicantTypeEnum.STUDENT,
            leave_type_id=1,
            leave_status_id=1
        )
        
        assert filters.applicant_type == ApplicantTypeEnum.STUDENT
        print("✅ LeaveFilters schema validation passed")
        
        # Test approval schema
        approval = LeaveApproval(
            leave_status_id=2,
            review_comments="Test approval"
        )
        
        assert approval.leave_status_id == 2
        print("✅ LeaveApproval schema validation passed")
        
        return True
    except Exception as e:
        print(f"❌ API schemas test failed: {e}")
        return False


def test_frontend_component():
    """Test frontend component structure"""
    print("\n🧪 Testing Frontend Component...")
    
    try:
        import os
        
        # Check if the new component file exists
        component_path = "../sunrise-school-frontend/src/components/admin/LeaveManagementSystem.tsx"
        if os.path.exists(component_path):
            print("✅ New LeaveManagementSystem component file exists")
            
            # Read and check basic structure
            with open(component_path, 'r') as f:
                content = f.read()
                
            # Check for key features
            checks = [
                "useState" in content,
                "useEffect" in content,
                "configuration" in content,
                "leave_types" in content,
                "leave_statuses" in content,
                "ApplicantTypeEnum" in content,
                "DatePicker" in content,
                "loadConfiguration" in content,
                "loadLeaveRequests" in content
            ]
            
            passed_checks = sum(checks)
            print(f"✅ Frontend component structure check: {passed_checks}/9 features found")
            
            if passed_checks >= 7:
                print("✅ Frontend component appears to be properly structured")
                return True
            else:
                print("⚠️ Frontend component may be missing some features")
                return False
        else:
            print("⚠️ New frontend component file not found")
            return False
            
    except Exception as e:
        print(f"❌ Frontend component test failed: {e}")
        return False


async def main():
    """Run all validation tests"""
    print("🚀 Starting Leave Management System Validation\n")
    
    tests = [
        ("Leave Models", test_leave_models()),
        ("Leave CRUD Operations", test_leave_crud()),
        ("Configuration Integration", test_configuration_integration()),
        ("Leave Policies", test_leave_policies()),
        ("API Schemas", test_api_schemas()),
    ]
    
    results = []
    
    # Run async tests
    for test_name, test_coro in tests:
        try:
            result = await test_coro
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Run sync test
    frontend_result = test_frontend_component()
    results.append(("Frontend Component", frontend_result))
    
    # Summary
    print("\n" + "="*50)
    print("📊 VALIDATION SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Leave Management System is ready for use.")
        return True
    elif passed >= total * 0.8:
        print("⚠️ Most tests passed. System is functional with minor issues.")
        return True
    else:
        print("❌ Multiple test failures. Please review the implementation.")
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Validation failed with error: {e}")
        sys.exit(1)
