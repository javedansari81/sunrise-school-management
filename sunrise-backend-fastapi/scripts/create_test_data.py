#!/usr/bin/env python3
"""
Script to create test data for the API
"""
import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.teacher import Teacher
from app.core.security import get_password_hash


async def create_test_users(session: AsyncSession):
    """Create test users"""
    print("Creating test users...")
    
    # Admin user
    admin_user = User(
        first_name="Admin",
        last_name="User",
        mobile="1234567890",
        email="admin@sunrise.com",
        password=get_password_hash("admin123"),
        user_type="admin",
        is_active=True
    )
    
    # Regular user
    regular_user = User(
        first_name="John",
        last_name="Doe",
        mobile="0987654321",
        email="john@sunrise.com",
        password=get_password_hash("user123"),
        user_type="user",
        is_active=True
    )
    
    # Test user for API validation
    test_user = User(
        first_name="Test",
        last_name="User",
        mobile="5555555555",
        email="test@example.com",
        password=get_password_hash("testpassword"),
        user_type="admin",
        is_active=True
    )
    
    session.add_all([admin_user, regular_user, test_user])
    await session.commit()
    print("✅ Test users created successfully")


async def create_test_teachers(session: AsyncSession):
    """Create test teachers"""
    print("Creating test teachers...")
    
    teachers = [
        Teacher(
            name="Sarah Johnson",
            age=32,
            gender="Female",
            position="Math Teacher",
            is_active=True
        ),
        Teacher(
            name="Michael Brown",
            age=28,
            gender="Male",
            position="Science Teacher",
            is_active=True
        ),
        Teacher(
            name="Emily Davis",
            age=35,
            gender="Female",
            position="English Teacher",
            is_active=True
        )
    ]
    
    session.add_all(teachers)
    await session.commit()
    print("✅ Test teachers created successfully")


async def main():
    """Main function to create test data"""
    print("🚀 Creating test data for Sunrise Backend FastAPI...")
    
    async with AsyncSessionLocal() as session:
        try:
            await create_test_users(session)
            await create_test_teachers(session)
            
            print("\n🎉 Test data creation completed successfully!")
            print("\n📋 Test Credentials:")
            print("Admin User: admin@sunrise.com / admin123")
            print("Regular User: john@sunrise.com / user123")
            print("Test User: test@example.com / testpassword")
            
        except Exception as e:
            print(f"❌ Test data creation failed: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
