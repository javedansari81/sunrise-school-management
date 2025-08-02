#!/usr/bin/env python3
"""
Direct API test for leave request creation
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.leave import LeaveRequestCreate, ApplicantTypeEnum
from app.crud.crud_leave import leave_request_crud
from app.crud import student_crud
from datetime import date

async def test_leave_creation_direct():
    """Test leave creation directly using CRUD operations"""
    
    print("Testing leave request creation directly...")
    
    # Get database session
    async for db in get_db():
        try:
            # First, check if student exists
            print("Checking if student with ID 5 exists...")
            student = await student_crud.get(db, id=5)
            if not student:
                print("❌ Student with ID 5 not found")
                return False
            
            print(f"✅ Student found: {student.first_name} {student.last_name}")
            
            # Create leave request data
            leave_data = LeaveRequestCreate(
                applicant_id=5,
                applicant_type=ApplicantTypeEnum.STUDENT,
                leave_type_id=1,
                start_date=date(2025, 8, 1),
                end_date=date(2025, 8, 2),
                total_days=2,
                reason="Personal Time Off",
                parent_consent=False,
                emergency_contact_name="",
                emergency_contact_phone="",
                substitute_teacher_id=None,
                substitute_arranged=False
            )
            
            print("Creating leave request...")
            leave_request = await leave_request_crud.create(db, obj_in=leave_data)
            print(f"✅ Leave request created successfully with ID: {leave_request.id}")
            print(f"   Applicant: {leave_request.applicant_type} ID {leave_request.applicant_id}")
            print(f"   Dates: {leave_request.start_date} to {leave_request.end_date}")
            print(f"   Reason: {leave_request.reason}")
            print(f"   Status: {leave_request.leave_status_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating leave request: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        break  # Only use first session

if __name__ == "__main__":
    success = asyncio.run(test_leave_creation_direct())
    if success:
        print("\n🎉 Direct leave creation test passed!")
    else:
        print("\n💥 Direct leave creation test failed!")
        sys.exit(1)
