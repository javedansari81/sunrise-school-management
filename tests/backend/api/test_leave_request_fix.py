#!/usr/bin/env python3
"""
Test script to reproduce and fix the Leave Request 500 error
"""

import asyncio
import httpx
import json
from datetime import date, timedelta

# Test data
BASE_URL = "http://localhost:8000"

async def test_leave_request_api():
    """Test the leave request API endpoint directly"""
    print("🧪 Testing Leave Request API Endpoint")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            # Step 1: Login to get authentication token
            print("\n1. Attempting to login...")
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
            print(f"✅ Login successful, token: {token[:20]}...")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Step 2: Get available teachers and students
            print("\n2. Getting available teachers...")
            teachers_response = await client.get(
                f"{BASE_URL}/api/v1/teachers/",
                headers=headers
            )
            
            if teachers_response.status_code == 200:
                teachers_data = teachers_response.json()
                teachers = teachers_data.get("teachers", [])
                print(f"✅ Found {len(teachers)} teachers")
                if teachers:
                    teacher = teachers[0]
                    print(f"   First teacher: ID={teacher['id']}, Name={teacher.get('first_name', '')} {teacher.get('last_name', '')}")
            else:
                print(f"❌ Failed to get teachers: {teachers_response.status_code}")
                teachers = []
            
            print("\n3. Getting available students...")
            students_response = await client.get(
                f"{BASE_URL}/api/v1/students/",
                headers=headers
            )
            
            if students_response.status_code == 200:
                students_data = students_response.json()
                students = students_data.get("students", [])
                print(f"✅ Found {len(students)} students")
                if students:
                    student = students[0]
                    print(f"   First student: ID={student['id']}, Name={student.get('first_name', '')} {student.get('last_name', '')}")
            else:
                print(f"❌ Failed to get students: {students_response.status_code}")
                students = []
            
            # Step 3: Get leave types
            print("\n4. Getting leave types...")
            config_response = await client.get(
                f"{BASE_URL}/api/v1/configuration/leave-management/",
                headers=headers
            )
            
            if config_response.status_code == 200:
                config_data = config_response.json()
                leave_types = config_data.get("leave_types", [])
                print(f"✅ Found {len(leave_types)} leave types")
                if leave_types:
                    leave_type = leave_types[0]
                    print(f"   First leave type: ID={leave_type['id']}, Name={leave_type['name']}")
            else:
                print(f"❌ Failed to get configuration: {config_response.status_code}")
                leave_types = []
            
            # Step 4: Test teacher leave request (if we have data)
            if teachers and leave_types:
                print("\n5. Testing TEACHER leave request...")
                teacher = teachers[0]
                leave_type = leave_types[0]
                
                teacher_payload = {
                    "applicant_id": teacher["id"],
                    "applicant_type": "teacher",
                    "leave_type_id": leave_type["id"],
                    "start_date": str(date.today() + timedelta(days=1)),
                    "end_date": str(date.today() + timedelta(days=2)),
                    "reason": "Personal work - testing API",
                    "parent_consent": False,
                    "emergency_contact_name": "",
                    "emergency_contact_phone": "",
                    "substitute_teacher_id": None,
                    "substitute_arranged": False,
                    "total_days": 2
                }
                
                print(f"   Payload: {json.dumps(teacher_payload, indent=2)}")
                
                teacher_response = await client.post(
                    f"{BASE_URL}/api/v1/leaves/",
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
            
            # Step 5: Test student leave request (if we have data)
            if students and leave_types:
                print("\n6. Testing STUDENT leave request...")
                student = students[0]
                leave_type = leave_types[0]
                
                student_payload = {
                    "applicant_id": student["id"],
                    "applicant_type": "student",
                    "leave_type_id": leave_type["id"],
                    "start_date": str(date.today() + timedelta(days=3)),
                    "end_date": str(date.today() + timedelta(days=4)),
                    "reason": "Family function - testing API",
                    "parent_consent": True,
                    "emergency_contact_name": "Parent Name",
                    "emergency_contact_phone": "9876543210",
                    "substitute_teacher_id": None,
                    "substitute_arranged": False,
                    "total_days": 2
                }
                
                print(f"   Payload: {json.dumps(student_payload, indent=2)}")
                
                student_response = await client.post(
                    f"{BASE_URL}/api/v1/leaves/",
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
            
            # Step 6: Test the original failing payload
            print("\n7. Testing ORIGINAL FAILING payload...")
            original_payload = {
                "applicant_id": 1,
                "applicant_type": "teacher",
                "leave_type_id": 1,
                "start_date": "2025-08-03",
                "end_date": "2025-08-04",
                "reason": "sdfsd",
                "parent_consent": False,
                "emergency_contact_name": "",
                "emergency_contact_phone": "",
                "substitute_teacher_id": "",
                "substitute_arranged": False,
                "total_days": 2
            }
            
            print(f"   Original Payload: {json.dumps(original_payload, indent=2)}")
            
            original_response = await client.post(
                f"{BASE_URL}/api/v1/leaves/",
                json=original_payload,
                headers=headers
            )
            
            print(f"   Response Status: {original_response.status_code}")
            if original_response.status_code == 200:
                print("✅ Original payload worked!")
                result = original_response.json()
                print(f"   Created leave request ID: {result.get('id')}")
            else:
                print("❌ Original payload failed (as expected)!")
                print(f"   Error: {original_response.text}")
                
                # Try to parse the error for more details
                try:
                    error_data = original_response.json()
                    print(f"   Error details: {json.dumps(error_data, indent=2)}")
                except:
                    pass
            
            print("\n" + "=" * 50)
            print("🎯 SUMMARY AND RECOMMENDATIONS:")
            print("=" * 50)
            
            if teachers and leave_types:
                print(f"✅ Use teacher ID: {teachers[0]['id']} for teacher requests")
            if students and leave_types:
                print(f"✅ Use student ID: {students[0]['id']} for student requests")
            if leave_types:
                print(f"✅ Use leave type ID: {leave_types[0]['id']}")
            
            print("\n📝 CORRECTED PAYLOADS:")
            if teachers and leave_types:
                correct_teacher = {
                    "applicant_id": teachers[0]["id"],
                    "applicant_type": "teacher",
                    "leave_type_id": leave_types[0]["id"],
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
                print(f"\nTeacher Request:\n{json.dumps(correct_teacher, indent=2)}")
            
            if students and leave_types:
                correct_student = {
                    "applicant_id": students[0]["id"],
                    "applicant_type": "student",
                    "leave_type_id": leave_types[0]["id"],
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
                print(f"\nStudent Request:\n{json.dumps(correct_student, indent=2)}")
                
        except Exception as e:
            print(f"❌ Error during testing: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_leave_request_api())
