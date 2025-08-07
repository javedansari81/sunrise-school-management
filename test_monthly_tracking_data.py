#!/usr/bin/env python3
"""
Test script to check the monthly tracking data and debug the missing button issue.
This script will query the database directly to see what data is being returned.
"""

import asyncio
import sys
import os
from pathlib import Path
import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_monthly_tracking_data():
    """Test the monthly tracking data from the database"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not found!")
        return False
    
    try:
        # Connect to database
        print("🔗 Connecting to database...")
        conn = await asyncpg.connect(database_url)
        
        # Test 1: Check if the enhanced_student_fee_status view exists
        print("\n1️⃣ Checking if enhanced_student_fee_status view exists...")
        view_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.views 
                WHERE table_name = 'enhanced_student_fee_status'
            )
        """)
        print(f"   View exists: {view_exists}")
        
        if not view_exists:
            print("❌ The enhanced_student_fee_status view does not exist!")
            print("   Please run the complete_monthly_tracking_fix.sql script first.")
            return False
        
        # Test 2: Check sample data from the view
        print("\n2️⃣ Checking sample data from enhanced_student_fee_status view...")
        sample_data = await conn.fetch("""
            SELECT 
                student_id, student_name, class_name, session_year,
                fee_record_id, has_monthly_tracking, total_months_tracked
            FROM enhanced_student_fee_status 
            WHERE session_year = '2025-26'
            LIMIT 5
        """)
        
        if sample_data:
            print(f"   Found {len(sample_data)} sample records:")
            for row in sample_data:
                print(f"   - Student {row['student_id']}: {row['student_name']} | "
                      f"Fee Record: {row['fee_record_id']} | "
                      f"Has Tracking: {row['has_monthly_tracking']} | "
                      f"Months Tracked: {row['total_months_tracked']}")
        else:
            print("   No data found for session year 2025-26")
        
        # Test 3: Check students without monthly tracking
        print("\n3️⃣ Checking students without monthly tracking...")
        students_without_tracking = await conn.fetch("""
            SELECT 
                student_id, student_name, class_name,
                fee_record_id, has_monthly_tracking, total_months_tracked
            FROM enhanced_student_fee_status 
            WHERE session_year = '2025-26' 
            AND has_monthly_tracking = false
            AND fee_record_id IS NOT NULL
            LIMIT 10
        """)
        
        if students_without_tracking:
            print(f"   Found {len(students_without_tracking)} students eligible for monthly tracking:")
            for row in students_without_tracking:
                print(f"   - Student {row['student_id']}: {row['student_name']} | "
                      f"Fee Record: {row['fee_record_id']} | "
                      f"Class: {row['class_name']}")
        else:
            print("   No students found without monthly tracking (or all students already have tracking enabled)")
        
        # Test 4: Check fee_records table
        print("\n4️⃣ Checking fee_records table...")
        fee_records = await conn.fetch("""
            SELECT 
                fr.id, fr.student_id, fr.is_monthly_tracked,
                s.first_name || ' ' || s.last_name as student_name
            FROM fee_records fr
            JOIN students s ON fr.student_id = s.id
            WHERE fr.session_year_id = 4  -- 2025-26
            LIMIT 5
        """)
        
        if fee_records:
            print(f"   Found {len(fee_records)} fee records:")
            for row in fee_records:
                print(f"   - Fee Record {row['id']}: Student {row['student_id']} ({row['student_name']}) | "
                      f"Monthly Tracked: {row['is_monthly_tracked']}")
        else:
            print("   No fee records found for session year 2025-26")
        
        # Test 5: Check monthly_fee_tracking table
        print("\n5️⃣ Checking monthly_fee_tracking table...")
        monthly_tracking = await conn.fetch("""
            SELECT 
                mft.fee_record_id, mft.student_id, 
                COUNT(*) as tracking_records,
                s.first_name || ' ' || s.last_name as student_name
            FROM monthly_fee_tracking mft
            JOIN students s ON mft.student_id = s.id
            WHERE mft.session_year_id = 4  -- 2025-26
            GROUP BY mft.fee_record_id, mft.student_id, s.first_name, s.last_name
            LIMIT 5
        """)
        
        if monthly_tracking:
            print(f"   Found {len(monthly_tracking)} students with monthly tracking records:")
            for row in monthly_tracking:
                print(f"   - Student {row['student_id']} ({row['student_name']}): "
                      f"{row['tracking_records']} monthly records")
        else:
            print("   No monthly tracking records found")
        
        # Test 6: Check the view logic specifically
        print("\n6️⃣ Testing view logic for has_monthly_tracking...")
        view_logic_test = await conn.fetch("""
            SELECT 
                s.id as student_id,
                s.first_name || ' ' || s.last_name as student_name,
                fr.id as fee_record_id,
                fr.is_monthly_tracked,
                COALESCE(monthly_stats.total_months_tracked, 0) as total_months_tracked,
                CASE 
                    WHEN monthly_stats.total_months_tracked > 0 THEN true
                    WHEN fr.is_monthly_tracked = true THEN true
                    ELSE false
                END as has_monthly_tracking_calculated
            FROM students s
            LEFT JOIN fee_records fr ON s.id = fr.student_id AND s.session_year_id = fr.session_year_id
            LEFT JOIN (
                SELECT 
                    mft.student_id,
                    mft.session_year_id,
                    COUNT(*) as total_months_tracked
                FROM monthly_fee_tracking mft
                GROUP BY mft.student_id, mft.session_year_id
            ) monthly_stats ON s.id = monthly_stats.student_id AND s.session_year_id = monthly_stats.session_year_id
            WHERE s.session_year_id = 4  -- 2025-26
            AND s.is_active = true
            AND (s.is_deleted = false OR s.is_deleted IS NULL)
            LIMIT 5
        """)
        
        if view_logic_test:
            print(f"   View logic test results:")
            for row in view_logic_test:
                print(f"   - Student {row['student_id']} ({row['student_name']}): "
                      f"Fee Record: {row['fee_record_id']} | "
                      f"is_monthly_tracked: {row['is_monthly_tracked']} | "
                      f"total_months_tracked: {row['total_months_tracked']} | "
                      f"has_monthly_tracking: {row['has_monthly_tracking_calculated']}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error testing data: {str(e)}")
        return False

async def main():
    """Main function"""
    print("🔍 Monthly Tracking Data Test")
    print("=" * 50)
    
    success = await test_monthly_tracking_data()
    
    if success:
        print("\n✅ Data test completed!")
        print("\n📋 Next Steps:")
        print("1. Check the console output above for any issues")
        print("2. Look at the browser console when using the Fee Management UI")
        print("3. Verify that students have fee_record_id and correct has_monthly_tracking values")
        print("4. If no eligible students are found, create some fee records first")
    else:
        print("\n❌ Data test failed!")
        print("Please check the error messages above and ensure the database is properly set up.")

if __name__ == "__main__":
    asyncio.run(main())
