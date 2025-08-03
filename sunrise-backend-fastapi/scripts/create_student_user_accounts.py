#!/usr/bin/env python3
"""
Migration script to create user accounts for existing students
"""
import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.student import Student
from app.models.metadata import UserType
from app.core.security import get_password_hash


async def create_student_user_accounts():
    """Create user accounts for existing students who don't have them"""
    async with AsyncSessionLocal() as db:
        try:
            print("🔍 Finding students without user accounts...")
            
            # Get all students who don't have user accounts
            students_without_users = await db.execute(
                select(Student).where(Student.user_id.is_(None))
            )
            students = students_without_users.scalars().all()
            
            if not students:
                print("✅ All students already have user accounts!")
                return
            
            print(f"📊 Found {len(students)} students without user accounts")
            
            # Get STUDENT user type
            student_user_type = await db.execute(
                select(UserType).where(UserType.name == "STUDENT")
            )
            student_user_type_obj = student_user_type.scalar_one_or_none()
            
            if not student_user_type_obj:
                print("❌ STUDENT user type not found in database!")
                return
            
            print(f"✅ Found STUDENT user type with ID: {student_user_type_obj.id}")
            
            created_count = 0
            skipped_count = 0
            
            for student in students:
                try:
                    # Determine login email
                    user_email = student.email
                    if not user_email and student.phone:
                        # Generate email from phone for login purposes
                        user_email = f"student_{student.phone}@sunriseschool.edu"
                    elif not user_email:
                        # Generate email from admission number as fallback
                        user_email = f"student_{student.admission_number}@sunriseschool.edu"
                    
                    # Check if user with this email already exists
                    existing_user = await db.execute(
                        select(User).where(User.email == user_email)
                    )
                    if existing_user.scalar_one_or_none():
                        print(f"⚠️  User with email {user_email} already exists, skipping student {student.admission_number}")
                        skipped_count += 1
                        continue
                    
                    # Create user account
                    user_account = User(
                        email=user_email,
                        hashed_password=get_password_hash("Sunrise@001"),  # Default password
                        first_name=student.first_name,
                        last_name=student.last_name,
                        phone=student.phone,
                        user_type_id=student_user_type_obj.id,
                        is_active=student.is_active,
                        is_verified=False
                    )
                    
                    db.add(user_account)
                    await db.flush()  # Get the user ID
                    
                    # Link user account to student
                    student.user_id = user_account.id
                    
                    print(f"✅ Created user account for {student.first_name} {student.last_name} (Admission: {student.admission_number})")
                    print(f"   📧 Email: {user_email}")
                    print(f"   📱 Phone: {student.phone or 'Not provided'}")
                    print(f"   🔑 Password: Sunrise@001")
                    
                    created_count += 1
                    
                except Exception as e:
                    print(f"❌ Error creating user for student {student.admission_number}: {e}")
                    continue
            
            # Commit all changes
            await db.commit()
            
            print(f"\n🎉 Migration completed!")
            print(f"   ✅ Created: {created_count} user accounts")
            print(f"   ⚠️  Skipped: {skipped_count} students (email conflicts)")
            print(f"   📊 Total processed: {len(students)} students")
            
            if created_count > 0:
                print(f"\n📋 Summary of created accounts:")
                print(f"   🔑 Default password for all students: Sunrise@001")
                print(f"   📧 Students can login with their email or phone number")
                print(f"   🏫 Students can access their profile at /profile after login")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            await db.rollback()
            raise


async def verify_student_accounts():
    """Verify that student accounts were created correctly"""
    async with AsyncSessionLocal() as db:
        try:
            print("\n🔍 Verifying student user accounts...")
            
            # Count students with and without user accounts
            total_students = await db.execute(select(Student))
            total_count = len(total_students.scalars().all())
            
            students_with_users = await db.execute(
                select(Student).where(Student.user_id.is_not(None))
            )
            with_users_count = len(students_with_users.scalars().all())
            
            students_without_users = await db.execute(
                select(Student).where(Student.user_id.is_(None))
            )
            without_users_count = len(students_without_users.scalars().all())
            
            print(f"📊 Verification Results:")
            print(f"   📚 Total students: {total_count}")
            print(f"   ✅ Students with user accounts: {with_users_count}")
            print(f"   ❌ Students without user accounts: {without_users_count}")
            
            if without_users_count == 0:
                print(f"🎉 All students have user accounts!")
            else:
                print(f"⚠️  {without_users_count} students still need user accounts")
                
        except Exception as e:
            print(f"❌ Verification failed: {e}")


async def main():
    """Main function"""
    print("🚀 Starting student user account migration...")
    print("=" * 60)
    
    try:
        # Create user accounts for students
        await create_student_user_accounts()
        
        # Verify the results
        await verify_student_accounts()
        
        print("=" * 60)
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
