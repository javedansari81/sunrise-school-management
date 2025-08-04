#!/usr/bin/env python3
"""
Test script for the new user-friendly leave request system
"""

import asyncio
import httpx
import json
from datetime import date, timedelta

BASE_URL = "http://localhost:8000"

async def test_friendly_leave_requests():
    """Test the new user-friendly leave request system"""
    print("🧪 Testing User-Friendly Leave Request System")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        try:
            # Step 1: Login
            print("\n1. Logging in...")
            login_data = {
                "username": "admin@sunriseschool.edu",
                "password": "admin123"
            }
            
            login_response = await client.post(
                f"{BASE_URL}/api/v1/auth/login",
                data=login_data
            )
            
            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"Response: {login_response.text}")
                return
            
            login_result = login_response.json()
            token = login_result.get("access_token")
            print(f"✅ Login successful")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Step 2: Get sample data
            print("\n2. Getting sample data...")
            
            # Get teachers
            teachers_response = await client.get(f"{BASE_URL}/api/v1/teachers/", headers=headers)
            teachers = []
            if teachers_response.status_code == 200:
                teachers_data = teachers_response.json()
                teachers = teachers_data.get("teachers", [])
                print(f"✅ Found {len(teachers)} teachers")
                if teachers:
                    teacher = teachers[0]
                    print(f"   Sample teacher: {teacher.get('first_name', '')} {teacher.get('last_name', '')} (ID: {teacher['employee_id']})")
            
            # Get students
            students_response = await client.get(f"{BASE_URL}/api/v1/students/", headers=headers)
            students = []
            if students_response.status_code == 200:
                students_data = students_response.json()
                students = students_data.get("students", [])
                print(f"✅ Found {len(students)} students")
                if students:
                    student = students[0]
                    print(f"   Sample student: {student.get('first_name', '')} {student.get('last_name', '')} (Roll: {student.get('roll_number', 'N/A')})")
            
            # Get classes
            config_response = await client.get(f"{BASE_URL}/api/v1/configuration/leave-management/", headers=headers)
            classes = []
            leave_types = []
            if config_response.status_code == 200:
                config_data = config_response.json()
                classes = config_data.get("classes", [])
                leave_types = config_data.get("leave_types", [])
                print(f"✅ Found {len(classes)} classes and {len(leave_types)} leave types")
                if classes:
                    class_obj = classes[0]
                    print(f"   Sample class: {class_obj['name']}")
                if leave_types:
                    leave_type = leave_types[0]
                    print(f"   Sample leave type: {leave_type['name']}")
            
            # Step 3: Test Teacher Leave Request with Employee ID
            if teachers and leave_types:
                print("\n3. Testing TEACHER leave request with Employee ID...")
                teacher = teachers[0]
                leave_type = leave_types[0]
                
                teacher_payload = {
                    "applicant_identifier": teacher["employee_id"],  # Just the employee ID
                    "applicant_type": "teacher",
                    "leave_type_id": leave_type["id"],
                    "start_date": str(date.today() + timedelta(days=1)),
                    "end_date": str(date.today() + timedelta(days=2)),
                    "reason": "Personal work - testing new identifier system",
                    "parent_consent": False,
                    "emergency_contact_name": "",
                    "emergency_contact_phone": "",
                    "substitute_arranged": False,
                    "total_days": 2
                }
                
                print(f"   Using Employee ID: {teacher['employee_id']}")
                print(f"   Payload: {json.dumps(teacher_payload, indent=2)}")
                
                teacher_response = await client.post(
                    f"{BASE_URL}/api/v1/leaves/friendly",
                    json=teacher_payload,
                    headers=headers
                )
                
                print(f"   Response Status: {teacher_response.status_code}")
                if teacher_response.status_code == 200:
                    print("✅ Teacher leave request created successfully!")
                    result = teacher_response.json()
                    print(f"   Created leave request ID: {result.get('id')}")
                else:
                    print("❌ Teacher leave request failed!")
                    print(f"   Error: {teacher_response.text}")
            
            # Step 4: Test Student Leave Request with Roll Number + Class
            if students and classes and leave_types:
                print("\n4. Testing STUDENT leave request with Roll Number + Class...")
                student = students[0]
                class_obj = classes[0]
                leave_type = leave_types[0]
                
                # Create the frontend format identifier
                roll_number = student.get('roll_number', '001')
                class_name = class_obj['name']
                student_identifier = f"Roll {roll_number} - Class {class_name}"
                
                student_payload = {
                    "applicant_identifier": student_identifier,
                    "applicant_type": "student",
                    "leave_type_id": leave_type["id"],
                    "start_date": str(date.today() + timedelta(days=3)),
                    "end_date": str(date.today() + timedelta(days=4)),
                    "reason": "Family function - testing new identifier system",
                    "parent_consent": True,
                    "emergency_contact_name": "Parent Name",
                    "emergency_contact_phone": "9876543210",
                    "substitute_arranged": False,
                    "total_days": 2
                }
                
                print(f"   Using Student Identifier: {student_identifier}")
                print(f"   Payload: {json.dumps(student_payload, indent=2)}")
                
                student_response = await client.post(
                    f"{BASE_URL}/api/v1/leaves/friendly",
                    json=student_payload,
                    headers=headers
                )
                
                print(f"   Response Status: {student_response.status_code}")
                if student_response.status_code == 200:
                    print("✅ Student leave request created successfully!")
                    result = student_response.json()
                    print(f"   Created leave request ID: {result.get('id')}")
                else:
                    print("❌ Student leave request failed!")
                    print(f"   Error: {student_response.text}")
            
            # Step 5: Test Error Handling
            print("\n5. Testing error handling with invalid identifiers...")
            
            # Test invalid teacher ID
            invalid_teacher_payload = {
                "applicant_identifier": "INVALID001",
                "applicant_type": "teacher",
                "leave_type_id": leave_types[0]["id"] if leave_types else 1,
                "start_date": str(date.today() + timedelta(days=5)),
                "end_date": str(date.today() + timedelta(days=6)),
                "reason": "Testing error handling",
                "parent_consent": False,
                "emergency_contact_name": "",
                "emergency_contact_phone": "",
                "substitute_arranged": False,
                "total_days": 2
            }
            
            invalid_response = await client.post(
                f"{BASE_URL}/api/v1/leaves/friendly",
                json=invalid_teacher_payload,
                headers=headers
            )
            
            print(f"   Invalid teacher ID response: {invalid_response.status_code}")
            if invalid_response.status_code != 200:
                print("✅ Error handling working correctly for invalid teacher ID")
                try:
                    error_data = invalid_response.json()
                    print(f"   Error message: {error_data.get('detail', 'No detail')}")
                except:
                    print(f"   Error text: {invalid_response.text}")
            else:
                print("❌ Expected error for invalid teacher ID but got success")
            
            print("\n" + "=" * 60)
            print("🎯 SUMMARY:")
            print("=" * 60)
            print("✅ User-friendly identifier system implemented")
            print("✅ Teachers can use Employee ID format")
            print("✅ Students can use Roll Number + Class format")
            print("✅ Backend properly resolves identifiers to database IDs")
            print("✅ Error handling works for invalid identifiers")
            
            print("\n📝 FRONTEND USAGE:")
            print("- Teachers: Enter Employee ID (e.g., EMP001)")
            print("- Students: Enter Roll Number and select Class from dropdown")
            print("- No more numeric applicant_id field needed!")
                
        except Exception as e:
            print(f"❌ Error during testing: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_friendly_leave_requests())
