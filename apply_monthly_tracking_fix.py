#!/usr/bin/env python3
"""
Simple script to apply the monthly tracking fix directly to the database.
This script connects to the database and runs the fix_monthly_tracking.sql file.
"""

import asyncio
import asyncpg
import os
from pathlib import Path

async def apply_fix():
    """Apply the monthly tracking fix to the database"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not found")
        print("Please set DATABASE_URL in your .env file or environment")
        return False
    
    print("🔧 Applying Monthly Tracking Fix...")
    print(f"📡 Connecting to database...")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(database_url)
        print("✅ Connected to database successfully")
        
        # Read the complete SQL fix file
        sql_file = Path(__file__).parent / "complete_monthly_tracking_fix.sql"
        if not sql_file.exists():
            print(f"❌ SQL file not found: {sql_file}")
            print("Falling back to fix_monthly_tracking.sql...")
            sql_file = Path(__file__).parent / "fix_monthly_tracking.sql"
            if not sql_file.exists():
                print(f"❌ Fallback SQL file not found: {sql_file}")
                return False

        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("📖 Read SQL fix file")
        
        # Execute the SQL
        print("🚀 Executing fix...")
        await conn.execute(sql_content)
        print("✅ Fix applied successfully!")
        
        # Test the fix
        print("\n🧪 Testing the fix...")
        result = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_students,
                COUNT(CASE WHEN has_monthly_tracking THEN 1 END) as with_tracking
            FROM enhanced_student_fee_status 
            WHERE session_year = '2025-26'
        """)
        
        if result:
            print(f"✅ Found {result['total_students']} active students")
            print(f"✅ {result['with_tracking']} students have monthly tracking enabled")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error applying fix: {e}")
        return False

async def main():
    """Main function"""
    print("=" * 60)
    print("🎯 Monthly Tracking Fix Application")
    print("=" * 60)
    
    success = await apply_fix()
    
    if success:
        print("\n🎉 Monthly tracking fix applied successfully!")
        print("\nWhat was fixed:")
        print("• Frontend now passes fee_record_id instead of student_id")
        print("• Database function properly counts created records")
        print("• View correctly determines has_monthly_tracking status")
        print("• Only students without tracking can be selected for enabling")
        print("• Updated enhanced_student_fee_status view to exclude soft-deleted students")
        print("\nNext steps:")
        print("1. Restart your FastAPI backend server")
        print("2. Clear your browser cache")
        print("3. Test the Fee Management System")
        print("4. Try enabling monthly tracking for students")
        print("5. Verify the status changes from 'Disabled' to 'Enabled'")
    else:
        print("\n❌ Fix application failed")
        print("Please check the error messages above and try again")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
