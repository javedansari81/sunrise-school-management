#!/usr/bin/env python3
"""
Migration script to convert enum columns to varchar columns
This fixes the type mismatch between SQLAlchemy models and PostgreSQL database
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def migrate_database():
    """Migrate enum columns to varchar columns"""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return
    
    print("🔄 Starting database migration...")
    print(f"📍 Database URL: {database_url[:50]}...")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(database_url)
        print("✅ Connected to database")
        
        # Start transaction
        async with conn.transaction():
            print("🔄 Starting transaction...")
            
            # 1. Alter fee_records table columns
            print("🔄 Migrating fee_records table...")
            
            # Change session_year from enum to varchar
            await conn.execute("""
                ALTER TABLE fee_records 
                ALTER COLUMN session_year TYPE VARCHAR(10) 
                USING session_year::text;
            """)
            print("✅ Migrated session_year column")
            
            # Change payment_type from enum to varchar  
            await conn.execute("""
                ALTER TABLE fee_records 
                ALTER COLUMN payment_type TYPE VARCHAR(20) 
                USING payment_type::text;
            """)
            print("✅ Migrated payment_type column")
            
            # Change status from enum to varchar
            await conn.execute("""
                ALTER TABLE fee_records 
                ALTER COLUMN status TYPE VARCHAR(20) 
                USING status::text;
            """)
            print("✅ Migrated status column")
            
            # Change payment_method from enum to varchar (nullable)
            await conn.execute("""
                ALTER TABLE fee_records 
                ALTER COLUMN payment_method TYPE VARCHAR(20) 
                USING payment_method::text;
            """)
            print("✅ Migrated payment_method column")
            
            # 2. Alter fee_payments table columns
            print("🔄 Migrating fee_payments table...")
            
            # Change payment_method from enum to varchar
            await conn.execute("""
                ALTER TABLE fee_payments 
                ALTER COLUMN payment_method TYPE VARCHAR(20) 
                USING payment_method::text;
            """)
            print("✅ Migrated fee_payments.payment_method column")
            
            print("✅ All columns migrated successfully!")
            
        print("✅ Transaction committed successfully!")
        
        # Verify the changes
        print("🔍 Verifying migration...")
        
        # Check fee_records table structure
        result = await conn.fetch("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'fee_records' 
            AND column_name IN ('session_year', 'payment_type', 'status', 'payment_method')
            ORDER BY column_name;
        """)
        
        print("📋 fee_records table structure:")
        for row in result:
            print(f"   {row['column_name']}: {row['data_type']} ({'NULL' if row['is_nullable'] == 'YES' else 'NOT NULL'})")
        
        # Check fee_payments table structure
        result = await conn.fetch("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'fee_payments' 
            AND column_name = 'payment_method'
            ORDER BY column_name;
        """)
        
        print("📋 fee_payments table structure:")
        for row in result:
            print(f"   {row['column_name']}: {row['data_type']} ({'NULL' if row['is_nullable'] == 'YES' else 'NOT NULL'})")
        
        # Test a sample query
        print("🔍 Testing sample query...")
        result = await conn.fetchrow("""
            SELECT COUNT(*) as count 
            FROM fee_records 
            WHERE session_year = '2024-25';
        """)
        print(f"✅ Found {result['count']} records for session year 2024-25")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        await conn.close()
        print("🔌 Database connection closed")

if __name__ == "__main__":
    asyncio.run(migrate_database())
