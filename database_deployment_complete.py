#!/usr/bin/env python3
"""
Complete Database Deployment Script
Deploys the complete database structure with all 21 tables
"""

import asyncio
import asyncpg
import os
from datetime import datetime

# Database connection parameters
DATABASE_URL = "postgresql://sunrise_user:1234@localhost:5432/sunrise_school_db"

async def connect_to_database():
    """Connect to the database"""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database successfully")
        
        # Set search path to sunrise schema
        await conn.execute("SET search_path TO sunrise, public;")
        print("✅ Set search path to sunrise schema")
        
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        raise

async def deploy_complete_database(conn: asyncpg.Connection):
    """Deploy complete database structure from SQL file"""
    print("\n🚀 Starting complete database deployment...")
    
    # Read and execute the complete database setup script
    script_path = "Database/Init/00_complete_database_setup.sql"
    print(f"📄 Reading SQL script: {script_path}")
    
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"SQL script not found: {script_path}")
    
    with open(script_path, 'r', encoding='utf-8') as file:
        sql_content = file.read()
    
    # Remove PostgreSQL-specific commands that don't work with asyncpg
    sql_content = sql_content.replace('\\echo', '-- \\echo')
    
    # Split into individual statements and execute
    statements = []
    current_statement = ""
    
    for line in sql_content.split('\n'):
        line = line.strip()
        if line and not line.startswith('--'):
            current_statement += line + " "
            if line.endswith(';'):
                statements.append(current_statement.strip())
                current_statement = ""
    
    print(f"🔧 Executing {len(statements)} SQL statements...")
    
    success_count = 0
    for i, statement in enumerate(statements, 1):
        if statement.strip() and not statement.strip().startswith('-- \\echo'):
            try:
                await conn.execute(statement)
                success_count += 1
                if i % 10 == 0:  # Progress indicator
                    print(f"   ✅ Executed {i}/{len(statements)} statements")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"   ℹ️  Statement {i}: Already exists")
                    success_count += 1
                else:
                    print(f"   ❌ Error in statement {i}: {e}")
                    print(f"   Statement: {statement[:100]}...")
                    continue
    
    print(f"✅ Database structure deployment completed! ({success_count}/{len(statements)} successful)")
    
    # Verify table creation
    result = await conn.fetch("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'sunrise' AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    
    print(f"\n📊 Created {len(result)} tables:")
    for row in result:
        print(f"   - {row['table_name']}")
    
    return len(result)

async def load_metadata(conn: asyncpg.Connection):
    """Load metadata from SQL file"""
    print("\n🔄 Loading metadata...")
    
    script_path = "Database/Init/01_load_metadata.sql"
    if not os.path.exists(script_path):
        print(f"⚠️  Metadata script not found: {script_path}")
        return False
    
    with open(script_path, 'r', encoding='utf-8') as file:
        sql_content = file.read()
    
    # Remove PostgreSQL-specific commands
    sql_content = sql_content.replace('\\echo', '-- \\echo')
    
    try:
        await conn.execute(sql_content)
        print("✅ Metadata loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to load metadata: {e}")
        return False

async def create_admin_user(conn: asyncpg.Connection):
    """Create admin user from SQL file"""
    print("\n👤 Creating admin user...")
    
    script_path = "Database/Init/02_create_admin_user.sql"
    if not os.path.exists(script_path):
        print(f"⚠️  Admin user script not found: {script_path}")
        return False
    
    with open(script_path, 'r', encoding='utf-8') as file:
        sql_content = file.read()
    
    # Remove PostgreSQL-specific commands
    sql_content = sql_content.replace('\\echo', '-- \\echo')
    
    try:
        await conn.execute(sql_content)
        print("✅ Admin user created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        return False

async def verify_deployment(conn: asyncpg.Connection):
    """Verify the deployment"""
    print("\n🔍 Verifying deployment...")
    
    # Check table count
    result = await conn.fetch("""
        SELECT COUNT(*) as table_count
        FROM information_schema.tables 
        WHERE table_schema = 'sunrise' AND table_type = 'BASE TABLE'
    """)
    table_count = result[0]['table_count']
    
    # Check metadata records
    metadata_counts = await conn.fetch("""
        SELECT 'user_types' as table_name, COUNT(*) as count FROM user_types
        UNION ALL SELECT 'session_years', COUNT(*) FROM session_years
        UNION ALL SELECT 'classes', COUNT(*) FROM classes
        UNION ALL SELECT 'expense_categories', COUNT(*) FROM expense_categories
        ORDER BY table_name
    """)
    
    # Check admin user
    admin_user = await conn.fetchrow("""
        SELECT email FROM users WHERE email = 'admin@sunriseschool.edu'
    """)
    
    print(f"📊 Verification Results:")
    print(f"   - Tables created: {table_count}")
    print(f"   - Metadata records:")
    for row in metadata_counts:
        print(f"     • {row['table_name']}: {row['count']} records")
    print(f"   - Admin user: {'✅ Created' if admin_user else '❌ Missing'}")
    
    return table_count >= 21 and admin_user is not None

async def main():
    """Main deployment function"""
    print("🚀 Complete Database Deployment Script")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Database: {DATABASE_URL}")
    print("=" * 50)
    
    conn = None
    try:
        # Connect to database
        conn = await connect_to_database()
        
        # Deploy complete database structure
        table_count = await deploy_complete_database(conn)
        
        # Load metadata
        await load_metadata(conn)
        
        # Create admin user
        await create_admin_user(conn)
        
        # Verify deployment
        success = await verify_deployment(conn)
        
        if success:
            print("\n🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
            print("=" * 50)
            print("Next steps:")
            print("1. Start the FastAPI backend server")
            print("2. Test the endpoints")
            print("3. Login with admin@sunriseschool.edu / admin123")
        else:
            print("\n⚠️  DEPLOYMENT COMPLETED WITH ISSUES")
            print("Please check the logs above for details")
        
    except Exception as e:
        print(f"\n❌ DEPLOYMENT FAILED: {e}")
        raise
    finally:
        if conn:
            await conn.close()
            print("🔌 Database connection closed")

if __name__ == "__main__":
    asyncio.run(main())
