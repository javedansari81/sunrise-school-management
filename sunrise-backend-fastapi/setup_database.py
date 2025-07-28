#!/usr/bin/env python3
"""
Database Setup Script for Sunrise School Management System
This script creates the database schema and inserts sample data
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def setup_database():
    """Set up the database with schema and sample data"""
    
    # Get database connection details from environment
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment variables")
        return
    
    print("🏫 Setting up Sunrise School Management System Database...")
    print("=" * 60)
    
    try:
        # Parse DATABASE_URL using urllib.parse for better compatibility
        from urllib.parse import urlparse

        parsed = urlparse(DATABASE_URL)

        username = parsed.username
        password = parsed.password
        host = parsed.hostname
        port = parsed.port or 5432  # Default PostgreSQL port
        database = parsed.path.lstrip('/')  # Remove leading slash
        
        print(f"📡 Connecting to database: {host}:{port}/{database}")
        
        # Connect to database
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database=database
        )
        
        print("✅ Connected to database successfully!")
        
        # Read and execute schema file
        print("\n🔧 Creating database schema...")
        with open('database_schema.sql', 'r') as f:
            schema_sql = f.read()
        
        await conn.execute(schema_sql)
        print("✅ Database schema created successfully!")
        
        # Read and execute sample data file
        print("\n📊 Inserting sample data...")
        with open('sample_data.sql', 'r') as f:
            sample_sql = f.read()
        
        await conn.execute(sample_sql)
        print("✅ Sample data inserted successfully!")
        
        # Verify the setup by checking table counts
        print("\n📈 Verifying database setup...")
        
        tables_to_check = [
            'users', 'students', 'teachers', 'fee_structures', 
            'fee_records', 'fee_payments', 'leave_requests', 'expenses'
        ]
        
        for table in tables_to_check:
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
            print(f"   📋 {table}: {count} records")
        
        # Close connection
        await conn.close()
        
        print("\n🎉 Database setup completed successfully!")
        print("\n💡 Login Credentials:")
        print("   👨‍💼 Admin: admin@sunriseschool.edu / admin123")
        print("   👨‍🏫 Teacher: teacher@sunriseschool.edu / admin123")
        print("   👨‍🎓 Student: student@sunriseschool.edu / admin123")
        
        print("\n🔗 Sample Data Includes:")
        print("   • 15 Students across different classes")
        print("   • 5 Teachers with different subjects")
        print("   • Fee structures for all classes")
        print("   • Fee records with various payment statuses")
        print("   • Leave requests with different statuses")
        print("   • Expense records for school operations")
        
        print("\n" + "=" * 60)
        print("🚀 You can now start the server and test the application!")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        import traceback
        traceback.print_exc()

async def reset_database():
    """Reset the database by dropping all tables and recreating them"""
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment variables")
        return
    
    print("⚠️  RESETTING DATABASE - This will delete all existing data!")
    confirm = input("Are you sure you want to continue? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("❌ Database reset cancelled")
        return
    
    try:
        # Parse DATABASE_URL using urllib.parse for better compatibility
        from urllib.parse import urlparse

        parsed = urlparse(DATABASE_URL)

        username = parsed.username
        password = parsed.password
        host = parsed.hostname
        port = parsed.port or 5432  # Default PostgreSQL port
        database = parsed.path.lstrip('/')  # Remove leading slash
        
        # Connect to database
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database=database
        )
        
        print("🔄 Resetting database...")
        
        # Drop all tables
        drop_sql = """
        DROP TABLE IF EXISTS fee_payments CASCADE;
        DROP TABLE IF EXISTS fee_records CASCADE;
        DROP TABLE IF EXISTS fee_structures CASCADE;
        DROP TABLE IF EXISTS leave_requests CASCADE;
        DROP TABLE IF EXISTS expenses CASCADE;
        DROP TABLE IF EXISTS students CASCADE;
        DROP TABLE IF EXISTS teachers CASCADE;
        DROP TABLE IF EXISTS users CASCADE;
        
        -- Drop ENUM types
        DROP TYPE IF EXISTS user_type_enum CASCADE;
        DROP TYPE IF EXISTS gender_enum CASCADE;
        DROP TYPE IF EXISTS class_enum CASCADE;
        DROP TYPE IF EXISTS qualification_enum CASCADE;
        DROP TYPE IF EXISTS employment_status_enum CASCADE;
        DROP TYPE IF EXISTS session_year_enum CASCADE;
        DROP TYPE IF EXISTS payment_type_enum CASCADE;
        DROP TYPE IF EXISTS payment_status_enum CASCADE;
        DROP TYPE IF EXISTS payment_method_enum CASCADE;
        DROP TYPE IF EXISTS leave_type_enum CASCADE;
        DROP TYPE IF EXISTS leave_status_enum CASCADE;
        DROP TYPE IF EXISTS expense_category_enum CASCADE;
        DROP TYPE IF EXISTS expense_status_enum CASCADE;
        """
        
        await conn.execute(drop_sql)
        print("✅ All tables dropped")
        
        await conn.close()
        
        # Now recreate everything
        await setup_database()
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'reset':
        asyncio.run(reset_database())
    else:
        asyncio.run(setup_database())

if __name__ == "__main__":
    main()
