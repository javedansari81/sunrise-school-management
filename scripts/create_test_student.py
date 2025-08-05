#!/usr/bin/env python3
"""
Script to create test student user for dashboard testing
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import from the app
sys.path.append(str(Path(__file__).parent.parent / "sunrise-backend-fastapi"))

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.student import Student
from app.core.security import get_password_hash
from sqlalchemy import select

async def create_test_student():
    """Create test student user for dashboard testing"""
    async with AsyncSessionLocal() as db:
        try:
            print("🔍 Checking if test student user already exists...")
            
            # Check if user already exists
            result = await db.execute(
                select(User).where(User.email == "javed.ansari81@gmail.com")
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"✅ User already exists with ID: {existing_user.id}")
                print(f"   Email: {existing_user.email}")
                print(f"   Role ID: {existing_user.user_type_id}")
                print(f"   Active: {existing_user.is_active}")
                return existing_user
            
            print("👤 Creating new test student user...")
            
            # Create new user
            new_user = User(
                first_name="Javed",
                last_name="Ansari",
                email="javed.ansari81@gmail.com",
                hashed_password=get_password_hash("Sunrise@001"),
                phone="7842350875",
                user_type_id=3,  # STUDENT role
                is_active=True,
                is_verified=True
            )
            
            db.add(new_user)
            await db.flush()  # Get the user ID
            
            print(f"✅ User created with ID: {new_user.id}")
            
            # Create student record
            print("🎓 Creating student record...")
            
            # Get first available class and session year
            from app.models.class_model import Class
            from app.models.session_year import SessionYear
            from app.models.gender import Gender
            
            class_result = await db.execute(
                select(Class).where(Class.is_active == True).limit(1)
            )
            class_obj = class_result.scalar_one_or_none()
            
            session_result = await db.execute(
                select(SessionYear).where(SessionYear.is_active == True).order_by(SessionYear.start_date.desc()).limit(1)
            )
            session_obj = session_result.scalar_one_or_none()
            
            gender_result = await db.execute(
                select(Gender).where(Gender.name == "Male").limit(1)
            )
            gender_obj = gender_result.scalar_one_or_none()
            
            if not class_obj or not session_obj or not gender_obj:
                print("❌ Missing required data (class, session year, or gender)")
                await db.rollback()
                return None
            
            new_student = Student(
                user_id=new_user.id,
                admission_number="STU2024001",
                first_name="Javed",
                last_name="Ansari",
                date_of_birth="2008-03-15",
                gender_id=gender_obj.id,
                class_id=class_obj.id,
                session_year_id=session_obj.id,
                roll_number=1,
                section="A",
                phone="7842350875",
                email="javed.ansari81@gmail.com",
                address="123 Test Street, Test City",
                city="Test City",
                state="Test State",
                postal_code="123456",
                father_name="Mohammad Ansari",
                father_phone="7842350876",
                father_email="mohammad.ansari@gmail.com",
                mother_name="Fatima Ansari",
                mother_phone="7842350877",
                mother_email="fatima.ansari@gmail.com",
                emergency_contact_name="Mohammad Ansari",
                emergency_contact_phone="7842350876",
                emergency_contact_relation="Father",
                admission_date="2024-01-01",
                is_active=True
            )
            
            db.add(new_student)
            await db.commit()
            
            print("✅ Test student created successfully!")
            print("📧 Email: javed.ansari81@gmail.com")
            print("🔑 Password: Sunrise@001")
            print("👤 Role: STUDENT")
            print(f"🆔 User ID: {new_user.id}")
            print(f"🎓 Admission Number: {new_student.admission_number}")
            print(f"📚 Class: {class_obj.name}")
            print(f"📅 Session: {session_obj.name}")
            
            return new_user
            
        except Exception as e:
            print(f"❌ Error creating test student: {e}")
            await db.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(create_test_student())
