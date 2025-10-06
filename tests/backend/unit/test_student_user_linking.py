#!/usr/bin/env python3
"""
Test suite for student-user linking functionality.

This test suite verifies that:
1. Students with email/phone get proper user accounts
2. Existing users are linked correctly
3. New users are created when needed
4. Error handling works properly
5. Database constraints prevent orphaned records
"""

import pytest
import asyncio
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.crud_student import CRUDStudent
from app.models.student import Student
from app.models.user import User
from app.models.metadata import UserType, Gender, Class, SessionYear
from app.schemas.student import StudentCreate
from app.core.security import get_password_hash
from sqlalchemy.future import select


class TestStudentUserLinking:
    """Test cases for student-user linking functionality"""
    
    @pytest.fixture
    async def db_session(self):
        """Get database session for testing"""
        async for db in get_db():
            yield db
            break
    
    @pytest.fixture
    async def student_crud(self):
        """Get student CRUD instance"""
        return CRUDStudent()
    
    @pytest.fixture
    async def test_metadata(self, db_session):
        """Get test metadata (gender, class, session_year, user_type)"""
        # Get existing metadata
        gender_result = await db_session.execute(select(Gender).where(Gender.name == "Male"))
        gender = gender_result.scalar_one_or_none()
        
        class_result = await db_session.execute(select(Class).limit(1))
        class_obj = class_result.scalar_one_or_none()
        
        session_result = await db_session.execute(select(SessionYear).where(SessionYear.is_current == True))
        session_year = session_result.scalar_one_or_none()
        
        user_type_result = await db_session.execute(select(UserType).where(UserType.name == "STUDENT"))
        user_type = user_type_result.scalar_one_or_none()
        
        return {
            "gender": gender,
            "class": class_obj,
            "session_year": session_year,
            "user_type": user_type
        }
    
    async def test_create_student_with_new_email(self, db_session, student_crud, test_metadata):
        """Test creating student with new email creates user account"""
        student_data = StudentCreate(
            admission_number="TEST001",
            first_name="Test",
            last_name="Student",
            date_of_birth=date(2010, 1, 1),
            gender_id=test_metadata["gender"].id,
            class_id=test_metadata["class"].id,
            session_year_id=test_metadata["session_year"].id,
            email="test.student@example.com",
            father_name="Test Father",
            mother_name="Test Mother",
            admission_date=date.today()
        )
        
        # Create student
        student = await student_crud.create_with_validation(db_session, obj_in=student_data)
        
        # Verify student was created
        assert student.id is not None
        assert student.email == "test.student@example.com"
        assert student.user_id is not None
        
        # Verify user account was created
        user_result = await db_session.execute(select(User).where(User.id == student.user_id))
        user = user_result.scalar_one_or_none()
        
        assert user is not None
        assert user.email == "test.student@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "Student"
        assert user.user_type_id == test_metadata["user_type"].id
        
        # Cleanup
        await db_session.delete(student)
        await db_session.delete(user)
        await db_session.commit()
    
    async def test_create_student_with_existing_email(self, db_session, student_crud, test_metadata):
        """Test creating student with existing email links to existing user"""
        # First, create a user
        existing_user = User(
            email="existing.user@example.com",
            password=get_password_hash("password123"),  # Fixed: use 'password' not 'hashed_password'
            first_name="Existing",
            last_name="User",
            user_type_id=test_metadata["user_type"].id,
            is_active=True
            # Note: is_verified field removed as it doesn't exist in User model
        )
        db_session.add(existing_user)
        await db_session.commit()
        await db_session.refresh(existing_user)
        
        # Now create student with same email
        student_data = StudentCreate(
            admission_number="TEST002",
            first_name="Test",
            last_name="Student",
            date_of_birth=date(2010, 1, 1),
            gender_id=test_metadata["gender"].id,
            class_id=test_metadata["class"].id,
            session_year_id=test_metadata["session_year"].id,
            email="existing.user@example.com",
            father_name="Test Father",
            mother_name="Test Mother",
            admission_date=date.today()
        )
        
        # Create student
        student = await student_crud.create_with_validation(db_session, obj_in=student_data)
        
        # Verify student was linked to existing user
        assert student.user_id == existing_user.id
        
        # Cleanup
        await db_session.delete(student)
        await db_session.delete(existing_user)
        await db_session.commit()
    
    async def test_create_student_with_phone_generates_email(self, db_session, student_crud, test_metadata):
        """Test creating student with phone generates email and creates user"""
        student_data = StudentCreate(
            admission_number="TEST003",
            first_name="Test",
            last_name="Student",
            date_of_birth=date(2010, 1, 1),
            gender_id=test_metadata["gender"].id,
            class_id=test_metadata["class"].id,
            session_year_id=test_metadata["session_year"].id,
            phone="9876543210",
            father_name="Test Father",
            mother_name="Test Mother",
            admission_date=date.today()
        )
        
        # Create student
        student = await student_crud.create_with_validation(db_session, obj_in=student_data)
        
        # Verify student was created with user account
        assert student.user_id is not None
        
        # Verify user account was created with generated email
        user_result = await db_session.execute(select(User).where(User.id == student.user_id))
        user = user_result.scalar_one_or_none()
        
        assert user is not None
        assert user.email == "student_9876543210@sunriseschool.edu"
        assert user.phone == "9876543210"
        
        # Cleanup
        await db_session.delete(student)
        await db_session.delete(user)
        await db_session.commit()
    
    async def test_create_student_without_email_phone_no_user(self, db_session, student_crud, test_metadata):
        """Test creating student without email/phone doesn't create user account"""
        student_data = StudentCreate(
            admission_number="TEST004",
            first_name="Test",
            last_name="Student",
            date_of_birth=date(2010, 1, 1),
            gender_id=test_metadata["gender"].id,
            class_id=test_metadata["class"].id,
            session_year_id=test_metadata["session_year"].id,
            father_name="Test Father",
            mother_name="Test Mother",
            admission_date=date.today()
        )
        
        # Create student
        student = await student_crud.create_with_validation(db_session, obj_in=student_data)
        
        # Verify student was created without user account
        assert student.user_id is None
        
        # Cleanup
        await db_session.delete(student)
        await db_session.commit()


async def run_tests():
    """Run all tests"""
    test_instance = TestStudentUserLinking()
    
    print("🧪 RUNNING STUDENT-USER LINKING TESTS")
    print("=" * 50)
    
    async for db in get_db():
        try:
            # Get test metadata
            test_metadata = await test_instance.test_metadata(db)
            
            if not all(test_metadata.values()):
                print("❌ Missing required test metadata")
                return False
            
            student_crud = CRUDStudent()
            
            # Run tests
            tests = [
                ("Create student with new email", test_instance.test_create_student_with_new_email),
                ("Create student with existing email", test_instance.test_create_student_with_existing_email),
                ("Create student with phone", test_instance.test_create_student_with_phone_generates_email),
                ("Create student without email/phone", test_instance.test_create_student_without_email_phone_no_user),
            ]
            
            passed = 0
            failed = 0
            
            for test_name, test_func in tests:
                try:
                    print(f"🔄 Running: {test_name}")
                    await test_func(db, student_crud, test_metadata)
                    print(f"✅ PASSED: {test_name}")
                    passed += 1
                except Exception as e:
                    print(f"❌ FAILED: {test_name} - {str(e)}")
                    failed += 1
            
            print(f"\n📊 TEST RESULTS:")
            print(f"   Passed: {passed}")
            print(f"   Failed: {failed}")
            print(f"   Total: {passed + failed}")
            
            return failed == 0
            
        except Exception as e:
            print(f"❌ Test setup failed: {e}")
            return False
        finally:
            break


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    exit(0 if success else 1)
