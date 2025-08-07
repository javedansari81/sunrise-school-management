#!/usr/bin/env python3
"""
Direct test of the enable_monthly_tracking_complete database function.
This bypasses the API and tests the database function directly.
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

async def test_database_function():
    """Test the database function directly"""
    
    try:
        import asyncpg
        
        # Load environment variables
        load_dotenv()
        
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL environment variable not found!")
            print("Please set DATABASE_URL in your .env file")
            return False
        
        # Connect to database
        print("🔗 Connecting to database...")
        conn = await asyncpg.connect(database_url)
        
        # Test 1: Check if function exists
        print("\n1️⃣ Checking if function exists...")
        function_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM pg_proc 
                WHERE proname = 'enable_monthly_tracking_complete'
            )
        """)
        
        if not function_exists:
            print("❌ Function enable_monthly_tracking_complete does not exist!")
            print("Please run the SQL script: enable_monthly_tracking_complete_function.sql")
            return False
        
        print("✅ Function exists")
        
        # Test 2: Get a sample student ID
        print("\n2️⃣ Getting sample student ID...")
        student_id = await conn.fetchval("""
            SELECT id FROM students 
            WHERE is_active = true 
            AND (is_deleted = false OR is_deleted IS NULL)
            LIMIT 1
        """)
        
        if not student_id:
            print("❌ No active students found in database!")
            return False
        
        print(f"✅ Found student ID: {student_id}")
        
        # Test 3: Check if fee structure exists
        print("\n3️⃣ Checking fee structure...")
        fee_structure = await conn.fetchrow("""
            SELECT fs.*, s.class_id, s.first_name, s.last_name
            FROM students s
            LEFT JOIN fee_structures fs ON s.class_id = fs.class_id AND fs.session_year_id = 4
            WHERE s.id = $1
        """, student_id)
        
        if not fee_structure or not fee_structure['id']:
            print(f"❌ No fee structure found for student {student_id}")
            print("This student's class doesn't have a fee structure for session year 4 (2025-26)")
            print("You need to create fee structures first")
            return False
        
        print(f"✅ Fee structure found: {fee_structure['total_annual_fee']}")
        
        # Test 4: Call the function
        print("\n4️⃣ Testing the database function...")
        try:
            results = await conn.fetch("""
                SELECT * FROM enable_monthly_tracking_complete(
                    ARRAY[$1]::INTEGER[], 
                    4, 
                    4, 
                    2025
                )
            """, student_id)
            
            print(f"✅ Function executed successfully!")
            print(f"Results: {len(results)} records returned")
            
            for result in results:
                print(f"   Student {result['student_id']} ({result['student_name']}):")
                print(f"   - Success: {result['success']}")
                print(f"   - Fee Record Created: {result['fee_record_created']}")
                print(f"   - Monthly Records Created: {result['monthly_records_created']}")
                print(f"   - Message: {result['message']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Function call failed: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            return False
        
        await conn.close()
        
    except ImportError:
        print("❌ asyncpg not installed. Install with: pip install asyncpg")
        return False
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

async def main():
    """Main function"""
    print("🔍 Direct Database Function Test")
    print("=" * 50)
    
    success = await test_database_function()
    
    if success:
        print("\n✅ Database function test passed!")
        print("The issue is likely in the API endpoint, not the database function.")
    else:
        print("\n❌ Database function test failed!")
        print("Fix the database issues before testing the API.")

if __name__ == "__main__":
    asyncio.run(main())
