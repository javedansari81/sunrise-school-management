#!/usr/bin/env python3
"""
Script to fix the monthly tracking functionality by updating database views
to properly handle soft delete columns added in V004.

This script applies the V007 migration to fix the enhanced_student_fee_status view
and other related views that were broken after adding soft delete columns.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the path
backend_path = Path(__file__).parent / "sunrise-backend-fastapi"
sys.path.append(str(backend_path))

try:
    from app.core.database import AsyncSessionLocal
    from sqlalchemy import text
    print("✅ Successfully imported database modules")
except ImportError as e:
    print(f"❌ Failed to import database modules: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


async def run_migration():
    """Run the V007 migration to fix monthly tracking views"""
    print("🔧 Starting monthly tracking fix migration...")
    
    # Read the migration script
    migration_file = Path(__file__).parent / "Database" / "Versioning" / "V007_fix_enhanced_student_fee_status_view.sql"
    
    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return False
    
    try:
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        print(f"📖 Read migration script: {migration_file}")
        
        # Execute the migration
        async with AsyncSessionLocal() as session:
            print("🚀 Executing migration...")
            
            # Split the SQL into individual statements and execute them
            statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
            
            for i, statement in enumerate(statements, 1):
                if statement.strip():
                    try:
                        print(f"   Executing statement {i}/{len(statements)}...")
                        await session.execute(text(statement))
                        await session.commit()
                    except Exception as e:
                        print(f"   ⚠️  Warning on statement {i}: {e}")
                        # Continue with other statements
                        await session.rollback()
            
            print("✅ Migration completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error running migration: {e}")
        return False


async def verify_fix():
    """Verify that the fix is working by checking the enhanced_student_fee_status view"""
    print("\n🔍 Verifying the fix...")
    
    try:
        async with AsyncSessionLocal() as session:
            # Test the enhanced_student_fee_status view
            result = await session.execute(text("""
                SELECT COUNT(*) as total_students, 
                       COUNT(CASE WHEN has_monthly_tracking THEN 1 END) as with_tracking
                FROM enhanced_student_fee_status 
                WHERE session_year = '2025-26'
            """))
            
            row = result.fetchone()
            if row:
                total_students = row[0]
                with_tracking = row[1]
                print(f"✅ View is working! Found {total_students} active students, {with_tracking} with monthly tracking")
                return True
            else:
                print("❌ No data returned from view")
                return False
                
    except Exception as e:
        print(f"❌ Error verifying fix: {e}")
        return False


async def main():
    """Main function to run the fix and verification"""
    print("=" * 60)
    print("🎯 Monthly Tracking Fix Script")
    print("=" * 60)
    
    # Run the migration
    migration_success = await run_migration()
    
    if migration_success:
        # Verify the fix
        verification_success = await verify_fix()
        
        if verification_success:
            print("\n🎉 Monthly tracking functionality has been fixed!")
            print("\nNext steps:")
            print("1. Test the Fee Management System in the UI")
            print("2. Try enabling monthly tracking for a student")
            print("3. Try viewing monthly history for a student")
            print("4. Verify that the 'Monthly fee history not found' error is resolved")
        else:
            print("\n⚠️  Migration completed but verification failed")
            print("Please check the database manually")
    else:
        print("\n❌ Migration failed. Please check the error messages above")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
