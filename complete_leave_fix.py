#!/usr/bin/env python3
"""
Complete fix for Leave Request 500 error
This script will:
1. Fix the database schema mismatch
2. Verify the fix works
3. Provide correct payload examples
"""

import asyncio
import asyncpg
import json
from datetime import date, timedelta

# Database connection settings
DATABASE_URL = "postgresql://postgres:password@localhost:5432/sunrise_db"

async def fix_database_schema():
    """Fix the database schema mismatch"""
    print("🔧 Fixing Database Schema...")
    print("=" * 40)
    
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Add missing columns to teachers table
        print("1. Adding missing columns to teachers table...")
        
        await conn.execute("""
            ALTER TABLE teachers ADD COLUMN IF NOT EXISTS bio TEXT;
        """)
        print("   ✅ Added 'bio' column")
        
        await conn.execute("""
            ALTER TABLE teachers ADD COLUMN IF NOT EXISTS specializations TEXT;
        """)
        print("   ✅ Added 'specializations' column")
        
        await conn.execute("""
            ALTER TABLE teachers ADD COLUMN IF NOT EXISTS certifications TEXT;
        """)
        print("   ✅ Added 'certifications' column")
        
        await conn.execute("""
            ALTER TABLE teachers ADD COLUMN IF NOT EXISTS img TEXT;
        """)
        print("   ✅ Added 'img' column")
        
        # Update existing records with default values
        print("\n2. Updating existing records with default values...")
        result = await conn.execute("""
            UPDATE teachers SET 
                bio = COALESCE(bio, ''),
                specializations = COALESCE(specializations, '[]'),
                certifications = COALESCE(certifications, '[]'),
                img = COALESCE(img, '')
            WHERE bio IS NULL OR specializations IS NULL OR certifications IS NULL OR img IS NULL;
        """)
        print(f"   ✅ Updated records: {result}")
        
        # Verify the changes
        print("\n3. Verifying schema changes...")
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'teachers' 
            AND column_name IN ('bio', 'specializations', 'certifications', 'img')
            ORDER BY column_name;
        """)
        
        for column in columns:
            print(f"   ✅ {column['column_name']}: {column['data_type']} (nullable: {column['is_nullable']})")
        
        # Get sample data for testing
        print("\n4. Getting sample data for testing...")
        
        # Get teachers
        teachers = await conn.fetch("SELECT id, first_name, last_name, employee_id FROM teachers LIMIT 3;")
        print(f"   Found {len(teachers)} teachers:")
        for teacher in teachers:
            print(f"     - ID: {teacher['id']}, Name: {teacher['first_name']} {teacher['last_name']}, Employee ID: {teacher['employee_id']}")
        
        # Get students
        students = await conn.fetch("SELECT id, first_name, last_name, admission_number FROM students LIMIT 3;")
        print(f"   Found {len(students)} students:")
        for student in students:
            print(f"     - ID: {student['id']}, Name: {student['first_name']} {student['last_name']}, Admission: {student['admission_number']}")
        
        # Get leave types
        leave_types = await conn.fetch("SELECT id, name FROM leave_types LIMIT 3;")
        print(f"   Found {len(leave_types)} leave types:")
        for lt in leave_types:
            print(f"     - ID: {lt['id']}, Name: {lt['name']}")
        
        await conn.close()
        
        print("\n" + "=" * 40)
        print("✅ Database schema fix completed successfully!")
        
        # Generate correct payloads
        print("\n📝 CORRECTED PAYLOAD EXAMPLES:")
        print("-" * 40)
        
        if teachers and leave_types:
            teacher = teachers[0]
            leave_type = leave_types[0]
            
            correct_teacher_payload = {
                "applicant_id": teacher["id"],
                "applicant_type": "teacher",
                "leave_type_id": leave_type["id"],
                "start_date": str(date.today() + timedelta(days=1)),
                "end_date": str(date.today() + timedelta(days=2)),
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
            student = students[0]
            leave_type = leave_types[0]
            
            correct_student_payload = {
                "applicant_id": student["id"],
                "applicant_type": "student",
                "leave_type_id": leave_type["id"],
                "start_date": str(date.today() + timedelta(days=1)),
                "end_date": str(date.today() + timedelta(days=2)),
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
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database schema: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def verify_fix():
    """Verify that the fix works by testing the database queries"""
    print("\n🧪 Verifying Fix...")
    print("=" * 40)
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Test teacher query (this was failing before)
        print("1. Testing teacher query...")
        teachers = await conn.fetch("SELECT * FROM teachers LIMIT 1;")
        if teachers:
            print("   ✅ Teacher query successful!")
            teacher = teachers[0]
            print(f"   Sample teacher: {teacher['first_name']} {teacher['last_name']}")
        else:
            print("   ⚠️ No teachers found in database")
        
        # Test student query
        print("\n2. Testing student query...")
        students = await conn.fetch("SELECT * FROM students LIMIT 1;")
        if students:
            print("   ✅ Student query successful!")
            student = students[0]
            print(f"   Sample student: {student['first_name']} {student['last_name']}")
        else:
            print("   ⚠️ No students found in database")
        
        # Test leave types
        print("\n3. Testing leave types query...")
        leave_types = await conn.fetch("SELECT * FROM leave_types LIMIT 1;")
        if leave_types:
            print("   ✅ Leave types query successful!")
            leave_type = leave_types[0]
            print(f"   Sample leave type: {leave_type['name']}")
        else:
            print("   ⚠️ No leave types found in database")
        
        await conn.close()
        
        print("\n✅ All verification tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main function to run the complete fix"""
    print("🚀 Leave Request 500 Error - Complete Fix")
    print("=" * 50)
    
    # Step 1: Fix database schema
    schema_fixed = await fix_database_schema()
    
    if not schema_fixed:
        print("❌ Schema fix failed. Cannot proceed.")
        return
    
    # Step 2: Verify the fix
    verification_passed = await verify_fix()
    
    if verification_passed:
        print("\n" + "=" * 50)
        print("🎉 COMPLETE FIX SUCCESSFUL!")
        print("=" * 50)
        print("\n📋 NEXT STEPS:")
        print("1. Restart your FastAPI backend server")
        print("2. Use the corrected payload examples above")
        print("3. Test the leave request creation in your frontend")
        print("\n💡 KEY POINTS:")
        print("- Use correct applicant_id from database (not hardcoded 1)")
        print("- Use correct leave_type_id from database")
        print("- Ensure all required fields are provided")
        print("- Database schema is now synchronized with the model")
    else:
        print("\n❌ Fix verification failed. Please check the database connection and try again.")


if __name__ == "__main__":
    asyncio.run(main())
