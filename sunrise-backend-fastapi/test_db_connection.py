#!/usr/bin/env python3
"""
Test database connection and initialize tables
"""
import asyncio
import asyncpg
from app.core.config import settings

async def test_connection():
    """Test PostgreSQL connection"""
    try:
        # Parse DATABASE_URL
        db_url = settings.DATABASE_URL
        print(f"Testing connection to: {db_url}")
        
        # Extract connection parameters
        # postgresql://postgres:1234@localhost:5432/sunrise_db
        parts = db_url.replace("postgresql://", "").split("@")
        user_pass = parts[0].split(":")
        host_db = parts[1].split("/")
        host_port = host_db[0].split(":")
        
        user = user_pass[0]
        password = user_pass[1]
        host = host_port[0]
        port = int(host_port[1])
        database = host_db[1]
        
        print(f"Connecting to: host={host}, port={port}, database={database}, user={user}")
        
        # Test connection
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        # Test query
        result = await conn.fetchval("SELECT version()")
        print(f"✅ Connection successful!")
        print(f"PostgreSQL version: {result}")
        
        # Check if tables exist
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        print(f"\n📊 Existing tables ({len(tables)}):")
        for table in tables:
            print(f"  - {table['table_name']}")
        
        # Check sample data
        if tables:
            try:
                students_count = await conn.fetchval("SELECT COUNT(*) FROM students")
                users_count = await conn.fetchval("SELECT COUNT(*) FROM users")
                leaves_count = await conn.fetchval("SELECT COUNT(*) FROM leave_requests")
                expenses_count = await conn.fetchval("SELECT COUNT(*) FROM expenses")
                
                print(f"\n📈 Data counts:")
                print(f"  - Students: {students_count}")
                print(f"  - Users: {users_count}")
                print(f"  - Leave Requests: {leaves_count}")
                print(f"  - Expenses: {expenses_count}")
                
            except Exception as e:
                print(f"⚠️  Could not fetch data counts: {e}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

async def main():
    print("🐘 Testing PostgreSQL Database Connection")
    print("=" * 50)
    
    success = await test_connection()
    
    if success:
        print("\n🎉 Database is ready!")
        print("You can now start the FastAPI server.")
    else:
        print("\n💡 Next steps:")
        print("1. Make sure PostgreSQL is running")
        print("2. Create the 'sunrise_db' database")
        print("3. Run the SQL scripts to create tables and insert data")

if __name__ == "__main__":
    asyncio.run(main())
