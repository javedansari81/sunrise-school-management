#!/usr/bin/env python3
"""
Test script for the FIXED enable_monthly_tracking_complete function.
This tests the function after fixing the ambiguous column reference error.
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

async def test_fixed_function():
    """Test the fixed database function"""
    
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
        
        # Test 1: Get a sample student ID with fee structure
        print("\n1️⃣ Finding student with fee structure...")
        student_data = await conn.fetchrow("""
            SELECT s.id, s.first_name || ' ' || s.last_name as name, 
                   s.class_id, fs.total_annual_fee
            FROM students s
            JOIN fee_structures fs ON s.class_id = fs.class_id AND fs.session_year_id = 4
            WHERE s.is_active = true 
            AND (s.is_deleted = false OR s.is_deleted IS NULL)
            LIMIT 1
        """)
        
        if not student_data:
            print("❌ No students found with fee structures!")
            print("Please ensure you have:")
            print("1. Active students in the database")
            print("2. Fee structures for session year 4 (2025-26)")
            return False
        
        student_id = student_data['id']
        student_name = student_data['name']
        annual_fee = student_data['total_annual_fee']
        
        print(f"✅ Found student: {student_name} (ID: {student_id})")
        print(f"   Annual fee: ₹{annual_fee}")
        
        # Test 2: Check current state
        print("\n2️⃣ Checking current state...")
        current_fee_record = await conn.fetchrow("""
            SELECT id, is_monthly_tracked FROM fee_records 
            WHERE student_id = $1 AND session_year_id = 4
        """, student_id)
        
        if current_fee_record:
            print(f"   Existing fee record: {current_fee_record['id']}")
            print(f"   Currently tracked: {current_fee_record['is_monthly_tracked']}")
        else:
            print("   No existing fee record - will be created")
        
        # Test 3: Call the FIXED function
        print("\n3️⃣ Testing the FIXED function...")
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
                print(f"\n📊 Student {result['student_id']} ({result['student_name']}):")
                print(f"   Success: {result['success']}")
                print(f"   Fee Record ID: {result['fee_record_id']}")
                print(f"   Fee Record Created: {result['fee_record_created']}")
                print(f"   Monthly Records Created: {result['monthly_records_created']}")
                print(f"   Message: {result['message']}")
                
                if result['success']:
                    # Verify the records were actually created
                    monthly_count = await conn.fetchval("""
                        SELECT COUNT(*) FROM monthly_fee_tracking 
                        WHERE fee_record_id = $1
                    """, result['fee_record_id'])
                    
                    print(f"   ✅ Verified: {monthly_count} monthly records in database")
                    
                    # Check fee record status
                    fee_status = await conn.fetchrow("""
                        SELECT is_monthly_tracked, total_amount, balance_amount 
                        FROM fee_records WHERE id = $1
                    """, result['fee_record_id'])
                    
                    if fee_status:
                        print(f"   ✅ Fee record status: tracked={fee_status['is_monthly_tracked']}")
                        print(f"   ✅ Total amount: ₹{fee_status['total_amount']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Function call failed: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            
            if "ambiguous" in str(e).lower():
                print("\n🔧 Still has ambiguous column reference!")
                print("The function needs further fixes.")
            elif "does not exist" in str(e).lower():
                print("\n🔧 Function doesn't exist!")
                print("Please run: fixed_enable_monthly_tracking_function.sql")
            
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
    print("🔍 Testing FIXED Enable Monthly Tracking Function")
    print("=" * 60)
    
    success = await test_fixed_function()
    
    if success:
        print("\n✅ FIXED function test passed!")
        print("\n📋 Next Steps:")
        print("1. The database function is now working correctly")
        print("2. Test the API endpoint through the UI")
        print("3. Should see successful monthly tracking enablement")
        print("4. Students should show 'Enabled' status")
    else:
        print("\n❌ FIXED function test failed!")
        print("\n🔧 Troubleshooting:")
        print("1. Run the fixed SQL script: fixed_enable_monthly_tracking_function.sql")
        print("2. Ensure fee structures exist for session year 4")
        print("3. Check that students are active and not deleted")

if __name__ == "__main__":
    asyncio.run(main())
