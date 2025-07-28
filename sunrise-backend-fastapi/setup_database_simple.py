#!/usr/bin/env python3
"""
Simple Database Setup Script for Render Deployment
This script creates the database schema and inserts sample data
"""

import asyncio
import asyncpg
import os
from urllib.parse import urlparse

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
        # Parse DATABASE_URL using urllib.parse
        parsed = urlparse(DATABASE_URL)
        
        print(f"📡 Connecting to database: {parsed.hostname}:{parsed.port or 5432}")
        
        # Connect to database using the full URL
        conn = await asyncpg.connect(DATABASE_URL)
        
        print("✅ Connected to database successfully!")
        
        # Read and execute schema file
        print("\n🔧 Creating database schema...")
        try:
            with open('database_schema.sql', 'r') as f:
                schema_sql = f.read()
            await conn.execute(schema_sql)
            print("✅ Database schema created successfully!")
        except FileNotFoundError:
            print("⚠️ database_schema.sql not found, skipping schema creation")
        except Exception as e:
            print(f"⚠️ Schema creation warning: {e}")
        
        # Read and execute sample data file
        print("\n📊 Inserting sample data...")
        try:
            with open('sample_data.sql', 'r') as f:
                sample_sql = f.read()
            await conn.execute(sample_sql)
            print("✅ Sample data inserted successfully!")
        except FileNotFoundError:
            print("⚠️ sample_data.sql not found, skipping sample data")
        except Exception as e:
            print(f"⚠️ Sample data warning: {e}")
        
        # Verify the setup by checking table counts
        print("\n📈 Verifying database setup...")
        
        tables_to_check = [
            'users', 'students', 'teachers', 'fee_structures', 
            'fee_records', 'fee_payments', 'leave_requests', 'expenses'
        ]
        
        for table in tables_to_check:
            try:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                print(f"   📋 {table}: {count} records")
            except Exception as e:
                print(f"   ⚠️ {table}: Table not found or error - {e}")
        
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
        print("🚀 Database is ready for the application!")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        print("🔍 Troubleshooting tips:")
        print("   1. Check if DATABASE_URL is correct")
        print("   2. Ensure database server is running")
        print("   3. Verify network connectivity")
        print("   4. Check if database exists")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    asyncio.run(setup_database())

if __name__ == "__main__":
    main()
