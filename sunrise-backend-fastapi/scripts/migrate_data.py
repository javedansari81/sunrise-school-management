#!/usr/bin/env python3
"""
Data migration script to transfer data from MongoDB JSON files to PostgreSQL
"""
import asyncio
import json
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal, async_engine, Base
from app.models.user import User
from app.models.teacher import Teacher
from app.core.security import get_password_hash


async def create_tables():
    """Create all database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully")


async def migrate_users(session: AsyncSession):
    """Migrate users from JSON to PostgreSQL"""
    data_file = Path(__file__).parent.parent / "data" / "sunrise-db.user.json"
    
    if not data_file.exists():
        print("❌ User data file not found")
        return
    
    with open(data_file, 'r', encoding='utf-8') as f:
        users_data = json.load(f)
    
    for user_data in users_data:
        # Check if user already exists
        existing_user = await session.get(User, user_data.get('_id', {}).get('$oid'))
        if existing_user:
            continue
            
        # Hash password if it's not already hashed
        password = user_data.get('password', '')
        if not password.startswith('$2b$'):
            password = get_password_hash(password)
        
        user = User(
            first_name=user_data.get('firstName', ''),
            last_name=user_data.get('lastName', ''),
            mobile=user_data.get('mobile', ''),
            email=user_data.get('email', ''),
            password=password,
            user_type=user_data.get('userType', 'user'),
            is_active=bool(user_data.get('IsActive', 1))
        )
        
        session.add(user)
    
    await session.commit()
    print("✅ Users migrated successfully")


async def migrate_teachers(session: AsyncSession):
    """Migrate teachers from JSON to PostgreSQL"""
    data_file = Path(__file__).parent.parent / "data" / "sunrise-db.teacher.json"
    
    if not data_file.exists():
        print("❌ Teacher data file not found")
        return
    
    with open(data_file, 'r', encoding='utf-8') as f:
        teachers_data = json.load(f)
    
    for teacher_data in teachers_data:
        teacher = Teacher(
            name=teacher_data.get('name', ''),
            age=teacher_data.get('age', 0),
            gender=teacher_data.get('gender', ''),
            position=teacher_data.get('position', ''),
            img=teacher_data.get('img', ''),
            is_active=bool(teacher_data.get('isActive', 1))
        )
        
        session.add(teacher)
    
    await session.commit()
    print("✅ Teachers migrated successfully")





async def main():
    """Main migration function"""
    print("🚀 Starting data migration from MongoDB JSON to PostgreSQL...")
    
    # Create tables
    await create_tables()
    
    # Create session
    async with AsyncSessionLocal() as session:
        try:
            await migrate_users(session)
            await migrate_teachers(session)

            print("🎉 Data migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
