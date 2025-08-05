#!/usr/bin/env python3
"""
Script to identify and fix orphaned student records that have email/phone but no user_id link.

This script:
1. Identifies students with email/phone but no user_id
2. Attempts to link them to existing users with matching email
3. Creates new user accounts if no matching user exists
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
from app.models.metadata import UserType
from app.core.security import get_password_hash
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


async def identify_orphaned_students(db: AsyncSession) -> List[Student]:
    """Identify students that should have user accounts but don't"""
    query = select(Student).where(
        Student.user_id.is_(None),
        (Student.email.isnot(None)) | (Student.phone.isnot(None)),
        Student.is_active == True,  # Only active students
        (Student.is_deleted.is_(None)) | (Student.is_deleted == False)  # Not soft deleted
    )
    
    result = await db.execute(query)
    return result.scalars().all()


async def get_student_user_type(db: AsyncSession) -> UserType:
    """Get the STUDENT user type"""
    result = await db.execute(select(UserType).where(UserType.name == "STUDENT"))
    user_type = result.scalar_one_or_none()
    if not user_type:
        raise ValueError("STUDENT user type not found in database")
    return user_type


async def fix_orphaned_student(db: AsyncSession, student: Student, student_user_type: UserType, dry_run: bool = True) -> Dict[str, Any]:
    """Fix a single orphaned student record"""
    result = {
        "student_id": student.id,
        "admission_number": student.admission_number,
        "name": f"{student.first_name} {student.last_name}",
        "email": student.email,
        "phone": student.phone,
        "action": None,
        "user_id": None,
        "success": False,
        "error": None
    }
    
    try:
        # Determine email to use for user account - use new email generation logic
        user_email = student.email
        if not user_email:
            # Generate proper email using name and DOB
            from app.utils.email_generator import generate_student_email
            user_email = await generate_student_email(
                db, student.first_name, student.last_name, student.date_of_birth
            )
            # Also update the student record with the generated email
            if not dry_run:
                student.email = user_email
        
        # Check if user with this email already exists
        existing_user_result = await db.execute(select(User).where(User.email == user_email))
        existing_user = existing_user_result.scalar_one_or_none()
        
        if existing_user:
            # Link to existing user
            result["action"] = "link_existing"
            result["user_id"] = existing_user.id
            
            if not dry_run:
                student.user_id = existing_user.id
                result["success"] = True
        else:
            # Create new user
            result["action"] = "create_new"
            
            if not dry_run:
                new_user = User(
                    email=user_email,
                    hashed_password=get_password_hash("Sunrise@001"),
                    first_name=student.first_name,
                    last_name=student.last_name,
                    phone=student.phone,
                    user_type_id=student_user_type.id,
                    is_active=True,
                    is_verified=False
                )
                db.add(new_user)
                await db.flush()  # Get the user ID
                
                student.user_id = new_user.id
                result["user_id"] = new_user.id
                result["success"] = True
    
    except Exception as e:
        result["error"] = str(e)
    
    return result


async def fix_orphaned_students(dry_run: bool = True):
    """Main function to fix orphaned students"""
    print("🔍 ORPHANED STUDENTS REPAIR TOOL")
    print("=" * 50)
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
    print()
    
    async for db in get_db():
        try:
            # Get student user type
            student_user_type = await get_student_user_type(db)
            print(f"✅ Found STUDENT user type (ID: {student_user_type.id})")
            
            # Identify orphaned students
            orphaned_students = await identify_orphaned_students(db)
            print(f"🔍 Found {len(orphaned_students)} orphaned student(s)")
            
            if not orphaned_students:
                print("✅ No orphaned students found!")
                return
            
            print("\n📋 ORPHANED STUDENTS:")
            for student in orphaned_students:
                print(f"   - {student.first_name} {student.last_name} (ID: {student.id})")
                print(f"     Admission: {student.admission_number}")
                print(f"     Email: {student.email}")
                print(f"     Phone: {student.phone}")
                print()
            
            if dry_run:
                print("🧪 DRY RUN - Simulating fixes...")
            else:
                print("🚀 LIVE EXECUTION - Applying fixes...")
            
            results = []
            for student in orphaned_students:
                result = await fix_orphaned_student(db, student, student_user_type, dry_run)
                results.append(result)
                
                status = "✅" if result["success"] else "❌"
                print(f"{status} {result['name']} ({result['admission_number']})")
                print(f"    Action: {result['action']}")
                if result["user_id"]:
                    print(f"    User ID: {result['user_id']}")
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
            linked_existing = len([r for r in results if r["action"] == "link_existing"])
            created_new = len([r for r in results if r["action"] == "create_new"])
            
            print("\n📊 SUMMARY:")
            print(f"   Total processed: {len(results)}")
            print(f"   Successful: {successful}")
            print(f"   Failed: {failed}")
            print(f"   Linked to existing users: {linked_existing}")
            print(f"   Created new users: {created_new}")
            
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


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix orphaned student records")
    parser.add_argument("--execute", action="store_true", 
                       help="Execute the fixes (default is dry run)")
    
    args = parser.parse_args()
    
    asyncio.run(fix_orphaned_students(dry_run=not args.execute))
