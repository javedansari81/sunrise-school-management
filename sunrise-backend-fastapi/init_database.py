#!/usr/bin/env python3
"""
Smart Database Initialization Script for Render
Only creates tables and data if they don't already exist
"""

import asyncio
import asyncpg
import os
from urllib.parse import urlparse

async def check_table_exists(conn, table_name):
    """Check if a table exists in the database"""
    result = await conn.fetchval(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)",
        table_name
    )
    return result

async def init_database():
    """Initialize database only if needed"""
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment variables")
        return
    
    print("🏫 Initializing Sunrise School Management System Database...")
    print("=" * 60)
    
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database successfully!")
        
        # Check if main tables exist
        users_exists = await check_table_exists(conn, 'users')
        students_exists = await check_table_exists(conn, 'students')
        
        if users_exists and students_exists:
            print("✅ Database tables already exist!")
            
            # Check if we have sample data
            user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
            student_count = await conn.fetchval("SELECT COUNT(*) FROM students")
            
            if user_count > 0 and student_count > 0:
                print("✅ Sample data already exists!")
                print(f"   📋 Users: {user_count} records")
                print(f"   📋 Students: {student_count} records")
                print("\n🎉 Database is ready!")
            else:
                print("📊 Adding sample data...")
                try:
                    with open('sample_data.sql', 'r') as f:
                        sample_sql = f.read()
                    await conn.execute(sample_sql)
                    print("✅ Sample data added successfully!")
                except Exception as e:
                    print(f"⚠️ Could not add sample data: {e}")
        else:
            print("🔧 Creating database schema...")
            try:
                with open('database_schema.sql', 'r') as f:
                    schema_sql = f.read()
                await conn.execute(schema_sql)
                print("✅ Database schema created!")
                
                print("📊 Adding sample data...")
                with open('sample_data.sql', 'r') as f:
                    sample_sql = f.read()
                await conn.execute(sample_sql)
                print("✅ Sample data added!")
                
            except Exception as e:
                print(f"❌ Error creating schema: {e}")
                return
        
        # Final verification
        print("\n📈 Database Status:")
        tables = ['users', 'students', 'teachers', 'fee_structures', 'fee_records']
        for table in tables:
            try:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                print(f"   📋 {table}: {count} records")
            except:
                print(f"   ❌ {table}: Not found")
        
        await conn.close()
        
        print("\n💡 Login Credentials:")
        print("   👨‍💼 Admin: admin@sunriseschool.edu / admin123")
        print("   👨‍🏫 Teacher: teacher@sunriseschool.edu / admin123")
        print("   👨‍🎓 Student: student@sunriseschool.edu / admin123")
        
        print("\n🚀 Database initialization complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(init_database())
