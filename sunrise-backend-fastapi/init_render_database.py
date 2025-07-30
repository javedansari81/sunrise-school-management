#!/usr/bin/env python3
"""
Initialize Render PostgreSQL database with schema and sample data
"""
import asyncio
import asyncpg
import os
from pathlib import Path

# Database connection details
DATABASE_URL = "postgresql://sunrise_admin:sajG5az4NYzqfc28Is87wd3flrztdKiy@dpg-d24v8hffte5s73cvojog-a.singapore-postgres.render.com/sunrise_school_db"

async def init_render_database():
    """Initialize the Render database with schema and sample data"""
    print("🏫 Initializing Render PostgreSQL Database...")
    print("=" * 60)
    
    try:
        # Connect to database
        print("🔗 Connecting to Render PostgreSQL...")
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected successfully!")
        
        # Check if database is already initialized
        try:
            user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
            if user_count > 0:
                print(f"ℹ️  Database already initialized with {user_count} users")
                await conn.close()
                return
        except:
            print("📋 Database not initialized, proceeding with setup...")
        
        # Read and execute schema
        print("📋 Creating database schema...")
        schema_file = Path(__file__).parent / "database_schema.sql"
        if schema_file.exists():
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            await conn.execute(schema_sql)
            print("✅ Schema created successfully!")
        else:
            print("❌ Schema file not found!")
            return
        
        # Read and execute sample data
        print("📊 Inserting sample data...")
        sample_data_file = Path(__file__).parent / "sample_data.sql"
        if sample_data_file.exists():
            with open(sample_data_file, 'r', encoding='utf-8') as f:
                sample_sql = f.read()
            await conn.execute(sample_sql)
            print("✅ Sample data inserted successfully!")
        else:
            print("❌ Sample data file not found!")
            return
        
        # Verify data
        user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        student_count = await conn.fetchval("SELECT COUNT(*) FROM students")
        teacher_count = await conn.fetchval("SELECT COUNT(*) FROM teachers")
        
        print("\n📊 Database Statistics:")
        print(f"   👥 Users: {user_count}")
        print(f"   👨‍🎓 Students: {student_count}")
        print(f"   👨‍🏫 Teachers: {teacher_count}")
        
        # Close connection
        await conn.close()
        
        print("\n🎉 Database initialization completed successfully!")
        print("\n💡 Login Credentials:")
        print("   👨‍💼 Admin: admin@sunriseschool.edu / admin123")
        print("   👨‍🏫 Teacher: teacher@sunriseschool.edu / admin123")
        print("   👨‍🎓 Student: student@sunriseschool.edu / admin123")
        
        print("\n" + "=" * 60)
        print("🚀 Database is ready for the application!")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(init_render_database())
