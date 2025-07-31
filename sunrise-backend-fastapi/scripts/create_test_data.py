#!/usr/bin/env python3
"""
Script to create test data for the API
"""
import asyncio
import sys
from pathlib import Path
from datetime import date, datetime, timedelta
from decimal import Decimal

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.fee import FeeStructure, FeeRecord
from app.models.metadata import Gender, Class, SessionYear, PaymentType, PaymentStatus, PaymentMethod
from app.core.security import get_password_hash


async def create_test_users(session: AsyncSession):
    """Create test users"""
    print("Creating test users...")

    # Check if admin user already exists
    existing_admin = await session.execute(select(User).where(User.email == "admin@sunrise.com"))
    if existing_admin.scalar_one_or_none():
        print("✅ Test users already exist, skipping user creation")
        return

    # Get user types from metadata
    from app.models.metadata import UserType

    admin_type = await session.execute(select(UserType).where(UserType.name == "ADMIN"))
    admin_type_obj = admin_type.scalar_one_or_none()
    if not admin_type_obj:
        print("❌ ADMIN user type not found. Please ensure metadata is initialized.")
        return

    # Admin user
    admin_user = User(
        first_name="Admin",
        last_name="User",
        phone="1234567890",
        email="admin@sunrise.com",
        hashed_password=get_password_hash("admin123"),
        user_type_id=admin_type_obj.id,
        is_active=True
    )

    # Regular user (also admin for testing)
    regular_user = User(
        first_name="John",
        last_name="Doe",
        phone="0987654321",
        email="john@sunrise.com",
        hashed_password=get_password_hash("user123"),
        user_type_id=admin_type_obj.id,
        is_active=True
    )

    # Test user for API validation
    test_user = User(
        first_name="Test",
        last_name="User",
        phone="5555555555",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        user_type_id=admin_type_obj.id,
        is_active=True
    )

    session.add_all([admin_user, regular_user, test_user])
    await session.commit()
    print("✅ Test users created successfully")


async def create_test_teachers(session: AsyncSession):
    """Create test teachers"""
    print("Creating test teachers...")

    # Get gender metadata
    female_gender = await session.execute(select(Gender).where(Gender.name == "Female"))
    male_gender = await session.execute(select(Gender).where(Gender.name == "Male"))
    female_id = female_gender.scalar_one_or_none()
    male_id = male_gender.scalar_one_or_none()

    if not female_id or not male_id:
        print("❌ Gender metadata not found. Please ensure metadata is initialized.")
        return

    from datetime import date

    teachers = [
        Teacher(
            employee_id="EMP001",
            first_name="Sarah",
            last_name="Johnson",
            date_of_birth=date(1992, 3, 15),
            gender_id=female_id.id,
            phone="9876543301",
            email="sarah.johnson@sunrise.com",
            address="123 Teacher Colony, Delhi",
            city="Delhi",
            state="Delhi",
            postal_code="110001",
            position="Math Teacher",
            department="Mathematics",
            subjects='["Mathematics", "Statistics"]',
            experience_years=8,
            joining_date=date(2016, 6, 1),
            salary=45000.0,
            is_active=True
        ),
        Teacher(
            employee_id="EMP002",
            first_name="Michael",
            last_name="Brown",
            date_of_birth=date(1996, 7, 22),
            gender_id=male_id.id,
            phone="9876543302",
            email="michael.brown@sunrise.com",
            address="456 Faculty Street, Mumbai",
            city="Mumbai",
            state="Maharashtra",
            postal_code="400001",
            position="Science Teacher",
            department="Science",
            subjects='["Physics", "Chemistry"]',
            experience_years=4,
            joining_date=date(2020, 8, 15),
            salary=42000.0,
            is_active=True
        ),
        Teacher(
            employee_id="EMP003",
            first_name="Emily",
            last_name="Davis",
            date_of_birth=date(1989, 11, 8),
            gender_id=female_id.id,
            phone="9876543303",
            email="emily.davis@sunrise.com",
            address="789 Education Avenue, Bangalore",
            city="Bangalore",
            state="Karnataka",
            postal_code="560001",
            position="English Teacher",
            department="Languages",
            subjects='["English", "Literature"]',
            experience_years=10,
            joining_date=date(2014, 4, 10),
            salary=48000.0,
            is_active=True
        )
    ]

    session.add_all(teachers)
    await session.commit()
    print("✅ Test teachers created successfully")


async def create_test_students(session: AsyncSession):
    """Create test students with proper metadata relationships"""
    print("Creating test students...")

    # Check if students already exist
    existing_student = await session.execute(select(Student).where(Student.admission_number == "STU001"))
    if existing_student.scalar_one_or_none():
        print("✅ Test students already exist, skipping student creation")
        return

    # Get current session year (2025-26)
    current_session = await session.execute(
        select(SessionYear).where(SessionYear.name == "2025-26")
    )
    session_year = current_session.scalar_one_or_none()
    if not session_year:
        print("❌ Session year 2025-26 not found. Please ensure metadata is initialized.")
        return

    # Get genders
    male_gender = await session.execute(select(Gender).where(Gender.name == "Male"))
    female_gender = await session.execute(select(Gender).where(Gender.name == "Female"))
    male_id = male_gender.scalar_one().id
    female_id = female_gender.scalar_one().id

    # Get classes
    classes = await session.execute(select(Class))
    class_list = classes.scalars().all()

    if not class_list:
        print("❌ No classes found. Please ensure metadata is initialized.")
        return

    # Sample student data
    students_data = [
        {
            "admission_number": "STU001",
            "first_name": "Aarav",
            "last_name": "Sharma",
            "date_of_birth": date(2008, 5, 15),
            "gender_id": male_id,
            "class_id": class_list[0].id,  # First class
            "section": "A",
            "roll_number": "001",
            "blood_group": "O+",
            "phone": "9876543210",
            "email": "aarav.sharma@email.com",
            "address": "123 Main Street, Delhi",
            "city": "Delhi",
            "state": "Delhi",
            "postal_code": "110001",
            "father_name": "Rajesh Sharma",
            "father_phone": "9876543211",
            "father_email": "rajesh.sharma@email.com",
            "father_occupation": "Engineer",
            "mother_name": "Priya Sharma",
            "mother_phone": "9876543212",
            "mother_email": "priya.sharma@email.com",
            "mother_occupation": "Teacher",
            "emergency_contact_name": "Uncle Ram",
            "emergency_contact_phone": "9876543213",
            "emergency_contact_relation": "Uncle",
            "admission_date": date(2020, 4, 1),
            "previous_school": "ABC Primary School"
        },
        {
            "admission_number": "STU002",
            "first_name": "Ananya",
            "last_name": "Patel",
            "date_of_birth": date(2009, 8, 22),
            "gender_id": female_id,
            "class_id": class_list[1].id if len(class_list) > 1 else class_list[0].id,
            "section": "B",
            "roll_number": "002",
            "blood_group": "A+",
            "phone": "9876543220",
            "email": "ananya.patel@email.com",
            "address": "456 Park Avenue, Mumbai",
            "city": "Mumbai",
            "state": "Maharashtra",
            "postal_code": "400001",
            "father_name": "Amit Patel",
            "father_phone": "9876543221",
            "father_email": "amit.patel@email.com",
            "father_occupation": "Doctor",
            "mother_name": "Sunita Patel",
            "mother_phone": "9876543222",
            "mother_email": "sunita.patel@email.com",
            "mother_occupation": "Nurse",
            "emergency_contact_name": "Aunt Meera",
            "emergency_contact_phone": "9876543223",
            "emergency_contact_relation": "Aunt",
            "admission_date": date(2021, 6, 15),
            "previous_school": "XYZ Kindergarten"
        },
        {
            "admission_number": "STU003",
            "first_name": "Arjun",
            "last_name": "Singh",
            "date_of_birth": date(2007, 12, 10),
            "gender_id": male_id,
            "class_id": class_list[2].id if len(class_list) > 2 else class_list[0].id,
            "section": "A",
            "roll_number": "003",
            "blood_group": "B+",
            "phone": "9876543230",
            "email": "arjun.singh@email.com",
            "address": "789 Garden Road, Bangalore",
            "city": "Bangalore",
            "state": "Karnataka",
            "postal_code": "560001",
            "father_name": "Vikram Singh",
            "father_phone": "9876543231",
            "father_email": "vikram.singh@email.com",
            "father_occupation": "Business Owner",
            "mother_name": "Kavita Singh",
            "mother_phone": "9876543232",
            "mother_email": "kavita.singh@email.com",
            "mother_occupation": "Homemaker",
            "emergency_contact_name": "Grandfather",
            "emergency_contact_phone": "9876543233",
            "emergency_contact_relation": "Grandfather",
            "admission_date": date(2019, 3, 20),
            "previous_school": "DEF Public School"
        }
    ]

    # Create students
    for student_data in students_data:
        student_data["session_year_id"] = session_year.id
        student = Student(**student_data)
        session.add(student)

    await session.commit()
    print("✅ Test students created successfully")


async def main():
    """Main function to create test data"""
    print("🚀 Creating test data for Sunrise Backend FastAPI...")

    async with AsyncSessionLocal() as session:
        try:
            await create_test_users(session)
            # Skip teachers for now due to schema mismatch
            # await create_test_teachers(session)
            await create_test_students(session)

            print("\n🎉 Test data creation completed successfully!")
            print("\n📋 Test Credentials:")
            print("Admin User: admin@sunrise.com / admin123")
            print("Regular User: john@sunrise.com / user123")
            print("Test User: test@example.com / testpassword")
            print("\n📚 Test Students:")
            print("- Aarav Sharma (STU001)")
            print("- Ananya Patel (STU002)")
            print("- Arjun Singh (STU003)")

        except Exception as e:
            print(f"❌ Test data creation failed: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
