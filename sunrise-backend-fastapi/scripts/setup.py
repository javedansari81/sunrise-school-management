#!/usr/bin/env python3
"""
Setup script for the FastAPI application
"""
import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import init_db, get_db
from app.crud.crud_user import user_crud
from app.schemas.user import UserCreate


async def create_default_admin():
    """Create default admin user if it doesn't exist"""
    print("👤 Creating default admin user...")

    async for db in get_db():
        try:
            # Check if admin user already exists
            existing_admin = await user_crud.get_by_email(db, email="admin@sunriseschool.edu")

            if existing_admin:
                print("ℹ️  Default admin user already exists")
                return

            # Create default admin user
            admin_data = UserCreate(
                first_name="Admin",
                last_name="User",
                mobile="1234567890",
                email="admin@sunriseschool.edu",
                password="admin123",
                user_type="admin"
            )

            admin_user = await user_crud.create(db, obj_in=admin_data)
            print(f"✅ Default admin user created: {admin_user.email}")

        except Exception as e:
            print(f"❌ Failed to create admin user: {e}")
            raise


async def main():
    """Initialize the database and create default data"""
    print("🚀 Setting up the database...")

    try:
        await init_db()
        print("✅ Database setup completed successfully!")

        await create_default_admin()
        print("✅ Setup completed successfully!")

    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
