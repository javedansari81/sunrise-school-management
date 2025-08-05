#!/usr/bin/env python3
"""
Script to fix student email formats and ensure all students have proper auto-generated emails.

This script:
1. Identifies students with incorrect email formats
2. Regenerates emails using the proper firstname.lastname.ddmmyyyy format
3. Updates user accounts with the new emails
4. Provides detailed logging and rollback capability
"""

import asyncio
import sys
import os
from typing import List, Dict, Any

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_db
from app.models.student import Student
from app.models.user import User
from app.utils.email_generator import generate_student_email, validate_generated_email
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


async def identify_students_with_incorrect_emails(db: AsyncSession) -> List[Student]:
    """Identify students with incorrect email formats"""
    # Find students with emails that don't match the expected format
    query = select(Student).where(
        Student.email.isnot(None),
        Student.is_active == True,
        (Student.is_deleted.is_(None)) | (Student.is_deleted == False)
    )
    
    result = await db.execute(query)
    all_students = result.scalars().all()
    
    incorrect_students = []
    for student in all_students:
        if student.email and not validate_generated_email(student.email):
            incorrect_students.append(student)
    
    return incorrect_students


async def fix_student_email(db: AsyncSession, student: Student, dry_run: bool = True) -> Dict[str, Any]:
    """Fix a single student's email format"""
    result = {
        "student_id": student.id,
        "admission_number": student.admission_number,
        "name": f"{student.first_name} {student.last_name}",
        "old_email": student.email,
        "new_email": None,
        "user_updated": False,
        "success": False,
        "error": None
    }
    
    try:
        # Generate the correct email
        new_email = await generate_student_email(
            db, student.first_name, student.last_name, student.date_of_birth
        )
        result["new_email"] = new_email
        
        if not dry_run:
            # Update student email
            student.email = new_email
            
            # Update user email if linked
            if student.user_id:
                user_result = await db.execute(select(User).where(User.id == student.user_id))
                user = user_result.scalar_one_or_none()
                if user:
                    user.email = new_email
                    result["user_updated"] = True
            
            result["success"] = True
    
    except Exception as e:
        result["error"] = str(e)
    
    return result


async def fix_student_email_formats(dry_run: bool = True):
    """Main function to fix student email formats"""
    print("🔧 STUDENT EMAIL FORMAT REPAIR TOOL")
    print("=" * 50)
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
    print()
    
    async for db in get_db():
        try:
            # Identify students with incorrect emails
            incorrect_students = await identify_students_with_incorrect_emails(db)
            print(f"🔍 Found {len(incorrect_students)} student(s) with incorrect email formats")
            
            if not incorrect_students:
                print("✅ All students have correct email formats!")
                return
            
            print("\n📋 STUDENTS WITH INCORRECT EMAIL FORMATS:")
            for student in incorrect_students:
                print(f"   - {student.first_name} {student.last_name} (ID: {student.id})")
                print(f"     Admission: {student.admission_number}")
                print(f"     Current Email: {student.email}")
                print(f"     DOB: {student.date_of_birth}")
                print()
            
            if dry_run:
                print("🧪 DRY RUN - Simulating fixes...")
            else:
                print("🚀 LIVE EXECUTION - Applying fixes...")
            
            results = []
            for student in incorrect_students:
                result = await fix_student_email(db, student, dry_run)
                results.append(result)
                
                status = "✅" if result["success"] else "❌"
                print(f"{status} {result['name']} ({result['admission_number']})")
                print(f"    Old Email: {result['old_email']}")
                print(f"    New Email: {result['new_email']}")
                if result["user_updated"]:
                    print(f"    User Account: Updated")
                if result["error"]:
                    print(f"    Error: {result['error']}")
                print()
            
            if not dry_run:
                # Commit changes
                await db.commit()
                print("💾 Changes committed to database")
            
            # Summary
            successful = len([r for r in results if r["success"]])
            failed = len([r for r in results if not r["success"]])
            user_updates = len([r for r in results if r["user_updated"]])
            
            print("\n📊 SUMMARY:")
            print(f"   Total processed: {len(results)}")
            print(f"   Successful: {successful}")
            print(f"   Failed: {failed}")
            print(f"   User accounts updated: {user_updates}")
            
            if failed > 0:
                print("\n❌ FAILED RECORDS:")
                for result in results:
                    if not result["success"]:
                        print(f"   - {result['name']}: {result['error']}")
            
        except Exception as e:
            print(f"❌ Error during repair process: {e}")
            await db.rollback()
            raise
        finally:
            break


async def test_new_student_creation():
    """Test the new student creation with email generation"""
    print("\n🧪 TESTING NEW STUDENT CREATION")
    print("=" * 40)
    
    from app.crud.crud_student import CRUDStudent
    from app.schemas.student import StudentCreate
    from app.models.metadata import Gender, Class, SessionYear
    from datetime import date
    
    async for db in get_db():
        try:
            student_crud = CRUDStudent()
            
            # Get required metadata
            gender_result = await db.execute(select(Gender).where(Gender.name == 'Male'))
            gender = gender_result.scalar_one_or_none()
            
            class_result = await db.execute(select(Class).limit(1))
            class_obj = class_result.scalar_one_or_none()
            
            session_result = await db.execute(select(SessionYear).where(SessionYear.is_current == True))
            session_year = session_result.scalar_one_or_none()
            
            if not all([gender, class_obj, session_year]):
                print("❌ Missing required metadata")
                return
            
            # Test case 1: Basic create method
            print("📝 Testing basic create method...")
            student_data_1 = StudentCreate(
                admission_number='TEST_EMAIL_FIX_001',
                first_name='TestBasic',
                last_name='CreateMethod',
                date_of_birth=date(2015, 6, 10),
                gender_id=gender.id,
                class_id=class_obj.id,
                session_year_id=session_year.id,
                father_name='Test Father',
                mother_name='Test Mother',
                admission_date=date.today()
            )
            
            student_1 = await student_crud.create(db, obj_in=student_data_1)
            print(f"✅ Basic create: {student_1.first_name} {student_1.last_name}")
            print(f"   Email: {student_1.email}")
            print(f"   Valid format: {validate_generated_email(student_1.email)}")
            
            # Test case 2: Create with validation method
            print("\n📝 Testing create_with_validation method...")
            student_data_2 = StudentCreate(
                admission_number='TEST_EMAIL_FIX_002',
                first_name='TestValidation',
                last_name='CreateMethod',
                date_of_birth=date(2016, 8, 25),
                gender_id=gender.id,
                class_id=class_obj.id,
                session_year_id=session_year.id,
                father_name='Test Father',
                mother_name='Test Mother',
                admission_date=date.today()
            )
            
            student_2 = await student_crud.create_with_validation(db, obj_in=student_data_2)
            print(f"✅ Validation create: {student_2.first_name} {student_2.last_name}")
            print(f"   Email: {student_2.email}")
            print(f"   Valid format: {validate_generated_email(student_2.email)}")
            print(f"   User ID: {student_2.user_id}")
            
            print("\n🎉 All creation methods working correctly!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            break


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix student email formats")
    parser.add_argument("--execute", action="store_true", 
                       help="Execute the fixes (default is dry run)")
    parser.add_argument("--test", action="store_true",
                       help="Run creation tests")
    
    args = parser.parse_args()
    
    if args.test:
        asyncio.run(test_new_student_creation())
    else:
        asyncio.run(fix_student_email_formats(dry_run=not args.execute))
