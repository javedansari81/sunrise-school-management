#!/usr/bin/env python3
"""
Direct database test to check if teachers data exists
"""

import asyncio
import asyncpg
import os
import json
from datetime import datetime

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://sunrise_admin:sajG5az4NYzqfc28Is87wd3flrztdKiy@dpg-d24v8hffte5s73cvojog-a.singapore-postgres.render.com/sunrise_school_db')

async def test_database_connection():
    """Test database connection and fetch teachers"""
    print("🏫 SUNRISE SCHOOL - DIRECT DATABASE TEST")
    print("=" * 60)
    
    try:
        # Connect to database
        print(f"Connecting to: {DATABASE_URL}")
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Database connection successful")
        
        # Test basic query
        result = await conn.fetchval("SELECT 1")
        print(f"✅ Basic query test: {result}")
        
        # Check if teachers table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'teachers'
            )
        """)
        print(f"Teachers table exists: {table_exists}")
        
        if not table_exists:
            print("❌ Teachers table does not exist!")
            await conn.close()
            return False
        
        # Get table structure
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'teachers'
            ORDER BY ordinal_position
        """)
        
        print(f"\n📊 Teachers table structure ({len(columns)} columns):")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
        
        # Count total teachers
        total_count = await conn.fetchval("SELECT COUNT(*) FROM teachers")
        print(f"\n👥 Total teachers in database: {total_count}")
        
        # Count active teachers
        active_count = await conn.fetchval("""
            SELECT COUNT(*) FROM teachers 
            WHERE is_active = true AND (is_deleted IS NULL OR is_deleted = false)
        """)
        print(f"👥 Active teachers: {active_count}")
        
        # Fetch sample teachers
        if active_count > 0:
            teachers = await conn.fetch("""
                SELECT 
                    id, first_name, last_name, employee_id, position, 
                    department, subjects, experience_years, is_active,
                    email, phone, joining_date
                FROM teachers 
                WHERE is_active = true AND (is_deleted IS NULL OR is_deleted = false)
                ORDER BY first_name, last_name
                LIMIT 5
            """)
            
            print(f"\n📋 Sample teachers ({len(teachers)}):")
            for i, teacher in enumerate(teachers, 1):
                subjects = []
                if teacher['subjects']:
                    try:
                        subjects = json.loads(teacher['subjects'])
                    except:
                        subjects = [teacher['subjects']]
                
                print(f"  {i}. {teacher['first_name']} {teacher['last_name']} ({teacher['employee_id']})")
                print(f"     Position: {teacher['position']}")
                print(f"     Department: {teacher['department'] or 'Not specified'}")
                print(f"     Experience: {teacher['experience_years']} years")
                print(f"     Subjects: {subjects}")
                print(f"     Email: {teacher['email'] or 'Not provided'}")
                print(f"     Phone: {teacher['phone'] or 'Not provided'}")
                print()
        
        # Test the exact query used by the API
        print("🔍 Testing API query...")
        api_teachers = await conn.fetch("""
            SELECT
                t.*,
                g.name as gender_name,
                q.name as qualification_name,
                es.name as employment_status_name,
                c.name as class_teacher_of_name
            FROM teachers t
            LEFT JOIN genders g ON t.gender_id = g.id
            LEFT JOIN qualifications q ON t.qualification_id = q.id
            LEFT JOIN employment_statuses es ON t.employment_status_id = es.id
            LEFT JOIN classes c ON t.class_teacher_of_id = c.id
            WHERE (t.is_deleted IS NULL OR t.is_deleted = FALSE) AND t.is_active = true
            ORDER BY t.first_name, t.last_name
            LIMIT 10
        """)
        
        print(f"✅ API query returned {len(api_teachers)} teachers")
        
        if api_teachers:
            teacher = api_teachers[0]
            print(f"First teacher from API query:")
            print(f"  Name: {teacher['first_name']} {teacher['last_name']}")
            print(f"  Employee ID: {teacher['employee_id']}")
            print(f"  Position: {teacher['position']}")
            print(f"  Qualification: {teacher['qualification_name']}")
            print(f"  Active: {teacher['is_active']}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

async def main():
    """Main test function"""
    success = await test_database_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Database test completed successfully")
        print("🎯 Teachers data is available in the database")
    else:
        print("❌ Database test failed")
        print("🔧 Check database connection and table structure")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
