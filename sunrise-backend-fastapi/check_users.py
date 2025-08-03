#!/usr/bin/env python3
"""
Check what users exist in the database
"""
import asyncio
import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

async def check_users():
    """Check what users exist in the database"""
    print("🔍 Checking Users in Database...")
    
    try:
        from app.core.database import get_db
        from sqlalchemy import text
        
        async for db in get_db():
            # Get all users
            result = await db.execute(text("SELECT id, email, first_name, last_name, is_active FROM users ORDER BY id"))
            users = result.fetchall()
            
            print(f"Found {len(users)} users:")
            for user in users:
                print(f"  ID: {user[0]}, Email: {user[1]}, Name: {user[2]} {user[3]}, Active: {user[4]}")
            
            break
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to check users: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(check_users())
