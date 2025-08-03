#!/usr/bin/env python3
"""
Debug script to investigate and fix the Leave Request 500 error
"""

import asyncio
import json
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Import the FastAPI app components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'sunrise-backend-fastapi'))

from app.core.database import get_db, async_engine
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.user import User
from app.models.metadata import LeaveType, LeaveStatus
from app.schemas.leave import LeaveRequestCreate, ApplicantTypeEnum
from app.crud.crud_leave import leave_request_crud
from app.crud import teacher_crud, student_crud


async def debug_leave_request_issue():
    """Debug the leave request creation issue"""
    print("🔍 Debugging Leave Request 500 Error...")
    print("=" * 60)
    
    async with async_engine.begin() as conn:
        # Create a session
        async_session = AsyncSession(bind=conn)
        
        try:
            # 1. Check if teachers exist in database
            print("\n1. Checking Teachers in Database:")
            teachers_result = await async_session.execute(select(Teacher))
            teachers = teachers_result.scalars().all()
            
            if not teachers:
                print("❌ No teachers found in database!")
                return
            
            print(f"✅ Found {len(teachers)} teachers:")
            for teacher in teachers[:3]:  # Show first 3
                print(f"   - ID: {teacher.id}, Employee ID: {teacher.employee_id}, Name: {teacher.full_name}")
            
            # 2. Check if students exist in database
            print("\n2. Checking Students in Database:")
            students_result = await async_session.execute(select(Student))
            students = students_result.scalars().all()
            
            if students:
                print(f"✅ Found {len(students)} students:")
                for student in students[:3]:  # Show first 3
                    print(f"   - ID: {student.id}, Admission No: {student.admission_number}, Name: {student.full_name}")
            else:
                print("❌ No students found in database!")
            
            # 3. Check leave types
            print("\n3. Checking Leave Types:")
            leave_types_result = await async_session.execute(select(LeaveType))
            leave_types = leave_types_result.scalars().all()
            
            if not leave_types:
                print("❌ No leave types found in database!")
                return
            
            print(f"✅ Found {len(leave_types)} leave types:")
            for lt in leave_types[:3]:
                print(f"   - ID: {lt.id}, Name: {lt.name}")
            
            # 4. Check leave statuses
            print("\n4. Checking Leave Statuses:")
            leave_statuses_result = await async_session.execute(select(LeaveStatus))
            leave_statuses = leave_statuses_result.scalars().all()
            
            if not leave_statuses:
                print("❌ No leave statuses found in database!")
                return
            
            print(f"✅ Found {len(leave_statuses)} leave statuses:")
            for ls in leave_statuses[:3]:
                print(f"   - ID: {ls.id}, Name: {ls.name}")
            
            # 5. Test creating a teacher leave request with correct data
            print("\n5. Testing Teacher Leave Request Creation:")
            
            if teachers and leave_types:
                teacher = teachers[0]  # Use first teacher
                leave_type = leave_types[0]  # Use first leave type
                
                # Create proper leave request data
                leave_data = LeaveRequestCreate(
                    applicant_id=teacher.id,  # Use teacher's ID, not user ID
                    applicant_type=ApplicantTypeEnum.TEACHER,
                    leave_type_id=leave_type.id,
                    start_date=date.today() + timedelta(days=1),
                    end_date=date.today() + timedelta(days=2),
                    total_days=2,
                    reason="Test teacher leave request for debugging",
                    # Optional fields that might be causing issues
                    medical_certificate_url=None,
                    supporting_document_url=None,
                    substitute_teacher_id=None,
                    substitute_arranged=False,
                    parent_consent=False,
                    emergency_contact_name="",
                    emergency_contact_phone="",
                    is_half_day=False,
                    half_day_session=None,
                    applied_to=None
                )
                
                print(f"   Using Teacher ID: {teacher.id} ({teacher.full_name})")
                print(f"   Using Leave Type ID: {leave_type.id} ({leave_type.name})")
                print(f"   Leave Data: {leave_data.dict()}")
                
                try:
                    # Test the CRUD operation directly
                    leave_request = await leave_request_crud.create(async_session, obj_in=leave_data)
                    print(f"✅ Successfully created leave request with ID: {leave_request.id}")
                    
                    # Clean up - delete the test record
                    await async_session.delete(leave_request)
                    await async_session.commit()
                    print("✅ Test record cleaned up")
                    
                except Exception as e:
                    print(f"❌ Error creating leave request: {str(e)}")
                    print(f"   Error type: {type(e).__name__}")
                    import traceback
                    traceback.print_exc()
            
            # 6. Test creating a student leave request
            print("\n6. Testing Student Leave Request Creation:")
            
            if students and leave_types:
                student = students[0]  # Use first student
                leave_type = leave_types[0]  # Use first leave type
                
                # Create proper leave request data for student
                leave_data = LeaveRequestCreate(
                    applicant_id=student.id,  # Use student's ID
                    applicant_type=ApplicantTypeEnum.STUDENT,
                    leave_type_id=leave_type.id,
                    start_date=date.today() + timedelta(days=1),
                    end_date=date.today() + timedelta(days=2),
                    total_days=2,
                    reason="Test student leave request for debugging",
                    # Student-specific fields
                    parent_consent=True,
                    emergency_contact_name="Parent Name",
                    emergency_contact_phone="9876543210",
                    # Optional fields
                    medical_certificate_url=None,
                    supporting_document_url=None,
                    substitute_teacher_id=None,
                    substitute_arranged=False,
                    is_half_day=False,
                    half_day_session=None,
                    applied_to=None
                )
                
                print(f"   Using Student ID: {student.id} ({student.full_name})")
                print(f"   Using Leave Type ID: {leave_type.id} ({leave_type.name})")
                
                try:
                    # Test the CRUD operation directly
                    leave_request = await leave_request_crud.create(async_session, obj_in=leave_data)
                    print(f"✅ Successfully created student leave request with ID: {leave_request.id}")
                    
                    # Clean up - delete the test record
                    await async_session.delete(leave_request)
                    await async_session.commit()
                    print("✅ Test record cleaned up")
                    
                except Exception as e:
                    print(f"❌ Error creating student leave request: {str(e)}")
                    print(f"   Error type: {type(e).__name__}")
                    import traceback
                    traceback.print_exc()
            
            print("\n" + "=" * 60)
            print("🎯 RECOMMENDATIONS:")
            print("=" * 60)
            
            if teachers:
                print(f"✅ For TEACHER leave requests, use applicant_id: {teachers[0].id}")
            if students:
                print(f"✅ For STUDENT leave requests, use applicant_id: {students[0].id}")
            if leave_types:
                print(f"✅ Use valid leave_type_id from: {[lt.id for lt in leave_types[:3]]}")
            
            print("\n📝 CORRECTED PAYLOAD EXAMPLES:")
            print("-" * 40)
            
            if teachers and leave_types:
                correct_teacher_payload = {
                    "applicant_id": teachers[0].id,
                    "applicant_type": "teacher",
                    "leave_type_id": leave_types[0].id,
                    "start_date": "2025-08-04",
                    "end_date": "2025-08-05",
                    "reason": "Personal work",
                    "parent_consent": False,
                    "emergency_contact_name": "",
                    "emergency_contact_phone": "",
                    "substitute_teacher_id": None,
                    "substitute_arranged": False,
                    "total_days": 2
                }
                print("TEACHER Request:")
                print(json.dumps(correct_teacher_payload, indent=2))
            
            if students and leave_types:
                correct_student_payload = {
                    "applicant_id": students[0].id,
                    "applicant_type": "student",
                    "leave_type_id": leave_types[0].id,
                    "start_date": "2025-08-04",
                    "end_date": "2025-08-05",
                    "reason": "Family function",
                    "parent_consent": True,
                    "emergency_contact_name": "Parent Name",
                    "emergency_contact_phone": "9876543210",
                    "substitute_teacher_id": None,
                    "substitute_arranged": False,
                    "total_days": 2
                }
                print("\nSTUDENT Request:")
                print(json.dumps(correct_student_payload, indent=2))
                
        except Exception as e:
            print(f"❌ Database connection error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            await async_session.close()


if __name__ == "__main__":
    asyncio.run(debug_leave_request_issue())
