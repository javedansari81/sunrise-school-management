#!/usr/bin/env python3
"""
Debug script to check user_types table and student creation issue
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the path
backend_path = Path(__file__).parent / "sunrise-backend-fastapi"
sys.path.append(str(backend_path))

try:
    from app.core.database import AsyncSessionLocal
    from app.models.metadata import UserType
    from app.models.student import Student
    from app.schemas.student import StudentCreate
    from sqlalchemy import text, select
    print("✅ Successfully imported required modules")
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    sys.exit(1)

async def check_user_types():
    """Check if user_types table has the required data"""
    print("🔍 Checking user_types table...")
    
    async with AsyncSessionLocal() as db:
        try:
            # Check if user_types table exists and has data
            result = await db.execute(select(UserType))
            user_types = result.scalars().all()
            
            if not user_types:
                print("❌ No user types found in database!")
                return False
            
            print(f"✅ Found {len(user_types)} user types:")
            for ut in user_types:
                print(f"   - ID: {ut.id}, Name: {ut.name}, Active: {ut.is_active}")
            
            # Specifically check for STUDENT user type
            student_type = await db.execute(select(UserType).where(UserType.name == "STUDENT"))
            student_type_obj = student_type.scalar_one_or_none()
            
            if student_type_obj:
                print(f"✅ STUDENT user type found with ID: {student_type_obj.id}")
                return True
            else:
                print("❌ STUDENT user type not found!")
                return False
                
        except Exception as e:
            print(f"❌ Error checking user_types: {e}")
            return False

async def test_student_creation_logic():
    """Test the student creation logic with the problematic payload"""
    
    # Your original payload
    test_payload = {
        "admission_number": "STU002",
        "roll_number": "2",
        "first_name": "Javed",
        "last_name": "Ansari",
        "class_id": 1,
        "session_year_id": 4,
        "section": "A",
        "date_of_birth": "2019-01-04",
        "gender_id": 1,
        "blood_group": None,
        "phone": None,  # This is None
        "email": None,  # This is None
        "aadhar_no": "",
        "address": None,
        "city": None,
        "state": None,
        "postal_code": None,
        "country": "India",
        "father_name": "Shahid Ansari",
        "father_phone": None,
        "father_email": None,
        "father_occupation": None,
        "mother_name": "Hamida Khatoon",
        "mother_phone": None,
        "mother_email": None,
        "mother_occupation": None,
        "emergency_contact_name": None,
        "emergency_contact_phone": None,
        "emergency_contact_relation": None,
        "admission_date": "2025-08-01",
        "previous_school": None,
        "is_active": True
    }
    
    print("\n🧪 Testing student creation logic...")
    
    try:
        # Test schema validation first
        student_data = StudentCreate(**test_payload)
        print("✅ Schema validation passed")
        
        # Check if user account creation should be triggered
        should_create_user = student_data.email or student_data.phone
        print(f"📧 Email: {student_data.email}")
        print(f"📱 Phone: {student_data.phone}")
        print(f"🔄 Should create user account: {should_create_user}")
        
        if not should_create_user:
            print("✅ User account creation should be skipped (both email and phone are None)")
        else:
            print("⚠️  User account creation would be attempted")
            
        return True
        
    except Exception as e:
        print(f"❌ Error in student creation logic: {e}")
        return False

async def check_metadata_tables():
    """Check if all required metadata tables have data"""
    print("\n🔍 Checking metadata tables...")
    
    async with AsyncSessionLocal() as db:
        try:
            # Check genders table
            genders_result = await db.execute(text("SELECT COUNT(*) FROM genders"))
            genders_count = genders_result.scalar()
            print(f"📊 Genders: {genders_count} records")
            
            # Check classes table
            classes_result = await db.execute(text("SELECT COUNT(*) FROM classes"))
            classes_count = classes_result.scalar()
            print(f"📊 Classes: {classes_count} records")
            
            # Check session_years table
            session_years_result = await db.execute(text("SELECT COUNT(*) FROM session_years"))
            session_years_count = session_years_result.scalar()
            print(f"📊 Session Years: {session_years_count} records")
            
            # Check user_types table
            user_types_result = await db.execute(text("SELECT COUNT(*) FROM user_types"))
            user_types_count = user_types_result.scalar()
            print(f"📊 User Types: {user_types_count} records")
            
            # Check if the specific IDs from the payload exist
            print("\n🔍 Checking specific metadata IDs from payload...")
            
            # Check gender_id = 1
            gender_check = await db.execute(text("SELECT name FROM genders WHERE id = 1"))
            gender_name = gender_check.scalar()
            print(f"   Gender ID 1: {gender_name or 'NOT FOUND'}")
            
            # Check class_id = 1
            class_check = await db.execute(text("SELECT display_name FROM classes WHERE id = 1"))
            class_name = class_check.scalar()
            print(f"   Class ID 1: {class_name or 'NOT FOUND'}")
            
            # Check session_year_id = 4
            session_check = await db.execute(text("SELECT name FROM session_years WHERE id = 4"))
            session_name = session_check.scalar()
            print(f"   Session Year ID 4: {session_name or 'NOT FOUND'}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error checking metadata tables: {e}")
            return False

async def main():
    """Main debug function"""
    print("=" * 60)
    print("🔧 Student Creation Debug Script")
    print("=" * 60)
    
    # Check user types
    user_types_ok = await check_user_types()
    
    # Check metadata tables
    metadata_ok = await check_metadata_tables()
    
    # Test student creation logic
    logic_ok = await test_student_creation_logic()
    
    print("\n" + "=" * 60)
    print("📋 Debug Summary:")
    print(f"   User Types: {'✅ OK' if user_types_ok else '❌ ISSUE'}")
    print(f"   Metadata Tables: {'✅ OK' if metadata_ok else '❌ ISSUE'}")
    print(f"   Creation Logic: {'✅ OK' if logic_ok else '❌ ISSUE'}")
    
    if user_types_ok and metadata_ok and logic_ok:
        print("\n🎉 All checks passed! The issue might be elsewhere.")
        print("\nPossible causes:")
        print("1. Database connection issues during API call")
        print("2. Transaction rollback due to constraint violations")
        print("3. Missing metadata data that should be loaded")
        print("\nNext steps:")
        print("1. Check if metadata data is actually loaded in your database")
        print("2. Try the API call again and check detailed error logs")
        print("3. Verify database constraints and foreign keys")
    else:
        print("\n❌ Issues found! Please resolve the above problems.")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
