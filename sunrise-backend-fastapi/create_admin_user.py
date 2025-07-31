#!/usr/bin/env python3
"""
Script to create an admin user for testing
"""
import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash


async def create_admin_user():
    """Create admin user for testing"""
    async with AsyncSessionLocal() as session:
        try:
            print("Creating/updating test users...")

            # Update all test users with correct passwords
            from sqlalchemy import select

            test_users = [
                ("admin@sunriseschool.edu", "admin123", "Admin"),
                ("teacher@sunriseschool.edu", "admin123", "Teacher"),
                ("student@sunriseschool.edu", "admin123", "Student")
            ]

            for email, password, user_type in test_users:
                result = await session.execute(
                    select(User).where(User.email == email)
                )
                existing_user = result.scalar_one_or_none()

                if existing_user:
                    print(f"⚠️  {user_type} user already exists! Updating password...")
                    print(f"   Email: {existing_user.email}")
                    print(f"   Name: {existing_user.first_name} {existing_user.last_name}")
                    print(f"   User Type ID: {existing_user.user_type_id}")

                    # Update the password with a fresh hash
                    existing_user.hashed_password = get_password_hash(password)
                    await session.commit()
                    print(f"✅ {user_type} password updated successfully!")
                else:
                    print(f"❌ {user_type} user not found: {email}")

            return
            
            # Create admin user with new structure
            admin_user = User(
                first_name="Admin",
                last_name="User",
                email="admin@sunriseschool.edu",
                hashed_password=get_password_hash("admin123"),
                phone="1234567890",
                user_type_id=1,  # Assuming 1 = Admin in metadata table
                is_active=True,
                is_verified=True
            )
            
            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)
            
            print("✅ Admin user created successfully!")
            print(f"   Email: {admin_user.email}")
            print(f"   Password: admin123")
            print(f"   Name: {admin_user.first_name} {admin_user.last_name}")
            print(f"   User Type ID: {admin_user.user_type_id}")
            print(f"   ID: {admin_user.id}")
            
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            await session.rollback()
            raise


async def main():
    """Main function"""
    print("🚀 Creating admin user for Sunrise School Management System")
    print("=" * 60)
    
    try:
        await create_admin_user()
        print("=" * 60)
        print("✅ Admin user setup complete!")
        print("\n📝 Login credentials:")
        print("   Email: admin@sunriseschool.edu")
        print("   Password: admin123")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
