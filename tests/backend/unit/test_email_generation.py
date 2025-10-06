#!/usr/bin/env python3
"""
Test suite for email generation functionality.

This test suite verifies that:
1. Email generation works correctly for students and teachers
2. Email uniqueness is maintained
3. Generated emails follow the correct format
4. Edge cases are handled properly
"""

import pytest
import asyncio
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.utils.email_generator import (
    sanitize_name,
    format_date_for_email,
    generate_base_email,
    ensure_unique_email,
    generate_student_email,
    generate_teacher_email,
    validate_generated_email,
    extract_info_from_generated_email
)
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy.future import select


class TestEmailGeneration:
    """Test cases for email generation functionality"""
    
    def test_sanitize_name(self):
        """Test name sanitization"""
        assert sanitize_name("John") == "john"
        assert sanitize_name("John Smith") == "johnsmith"
        assert sanitize_name("John-Paul") == "johnpaul"
        assert sanitize_name("José") == "jos"  # Special characters removed
        assert sanitize_name("John123") == "john123"
        assert sanitize_name("  John  ") == "john"
        assert sanitize_name("") == ""
        assert sanitize_name("John@#$%") == "john"
    
    def test_format_date_for_email(self):
        """Test date formatting for email"""
        test_date = date(1995, 3, 15)
        assert format_date_for_email(test_date) == "15031995"
        
        test_date2 = date(2000, 12, 31)
        assert format_date_for_email(test_date2) == "31122000"
        
        test_date3 = date(1985, 1, 1)
        assert format_date_for_email(test_date3) == "01011985"
    
    def test_generate_base_email(self):
        """Test base email generation"""
        email = generate_base_email("John", "Smith", date(1995, 3, 15))
        assert email == "john.smith.15031995@sunriseschool.edu"
        
        email2 = generate_base_email("Mary Jane", "O'Connor", date(2000, 12, 31))
        assert email2 == "maryjane.oconnor.31122000@sunriseschool.edu"
        
        email3 = generate_base_email("José", "García", date(1985, 1, 1))
        assert email3 == "jos.garca.01011985@sunriseschool.edu"
    
    def test_validate_generated_email(self):
        """Test email validation"""
        # Valid emails
        assert validate_generated_email("john.smith.15031995@sunriseschool.edu") == True
        assert validate_generated_email("mary.jane.31122000@sunriseschool.edu") == True
        assert validate_generated_email("john.smith.15031995.2@sunriseschool.edu") == True
        assert validate_generated_email("a.b.01011985@sunriseschool.edu") == True
        
        # Invalid emails
        assert validate_generated_email("john.smith@sunriseschool.edu") == False  # Missing date
        assert validate_generated_email("john.smith.1995@sunriseschool.edu") == False  # Wrong date format
        assert validate_generated_email("john.smith.15031995@gmail.com") == False  # Wrong domain
        assert validate_generated_email("john@sunriseschool.edu") == False  # Missing lastname and date
        assert validate_generated_email("john.smith.15031995@sunriseschool.com") == False  # Wrong TLD
    
    def test_extract_info_from_generated_email(self):
        """Test extracting information from generated emails"""
        info = extract_info_from_generated_email("john.smith.15031995@sunriseschool.edu")
        assert info is not None
        assert info['first_name'] == 'john'
        assert info['last_name'] == 'smith'
        assert info['date_of_birth'] == date(1995, 3, 15)
        assert info['suffix'] is None
        assert info['is_generated'] == True
        
        info2 = extract_info_from_generated_email("mary.jane.31122000.2@sunriseschool.edu")
        assert info2 is not None
        assert info2['first_name'] == 'mary'
        assert info2['last_name'] == 'jane'
        assert info2['date_of_birth'] == date(2000, 12, 31)
        assert info2['suffix'] == '2'
        
        # Invalid email
        info3 = extract_info_from_generated_email("invalid@email.com")
        assert info3 is None


async def test_email_generation_integration():
    """Integration test for email generation with database"""
    print("🧪 TESTING EMAIL GENERATION INTEGRATION")
    print("=" * 50)
    
    async for db in get_db():
        try:
            # Test student email generation
            print("\n📧 Testing student email generation...")
            student_email = await generate_student_email(
                db, "Test", "Student", date(1995, 3, 15)
            )
            print(f"Generated student email: {student_email}")
            assert validate_generated_email(student_email)
            assert "test.student.15031995" in student_email
            
            # Test teacher email generation
            print("\n👨‍🏫 Testing teacher email generation...")
            teacher_email = await generate_teacher_email(
                db, "Test", "Teacher", date(1985, 12, 25)
            )
            print(f"Generated teacher email: {teacher_email}")
            assert validate_generated_email(teacher_email)
            assert "test.teacher.25121985" in teacher_email
            
            # Test uniqueness - create a user with the base email
            print("\n🔄 Testing email uniqueness...")
            base_email = "duplicate.test.01011990@sunriseschool.edu"
            
            # Create a user with this email
            existing_user = User(
                email=base_email,
                password=get_password_hash("password123"),  # Fixed: use 'password' not 'hashed_password'
                first_name="Existing",
                last_name="User",
                user_type_id=3,  # STUDENT
                is_active=True
                # Note: is_verified field removed as it doesn't exist in User model
            )
            db.add(existing_user)
            await db.commit()
            await db.refresh(existing_user)
            print(f"Created existing user with email: {base_email}")
            
            # Now try to generate email for someone with same name and DOB
            unique_email = await generate_student_email(
                db, "Duplicate", "Test", date(1990, 1, 1)
            )
            print(f"Generated unique email: {unique_email}")
            assert unique_email != base_email
            assert "duplicate.test.01011990.2@sunriseschool.edu" == unique_email
            
            # Test edge cases
            print("\n🔍 Testing edge cases...")
            
            # Names with special characters
            special_email = await generate_student_email(
                db, "José María", "García-López", date(2000, 6, 15)
            )
            print(f"Special characters email: {special_email}")
            assert validate_generated_email(special_email)
            assert "josmara.garcalopez.15062000" in special_email
            
            # Very long names
            long_email = await generate_teacher_email(
                db, "VeryLongFirstName", "VeryLongLastName", date(1975, 11, 30)
            )
            print(f"Long names email: {long_email}")
            assert validate_generated_email(long_email)
            assert "verylongfirstname.verylonglastname.30111975" in long_email
            
            print("\n✅ All email generation tests passed!")
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            break


async def test_student_creation_with_email_generation():
    """Test student creation with automatic email generation"""
    print("\n🎓 TESTING STUDENT CREATION WITH EMAIL GENERATION")
    print("=" * 50)
    
    from app.crud.crud_student import CRUDStudent
    from app.schemas.student import StudentCreate
    from app.models.metadata import Gender, Class, SessionYear
    
    async for db in get_db():
        try:
            student_crud = CRUDStudent()
            
            # Get required metadata
            gender_result = await db.execute(select(Gender).where(Gender.name == 'Male'))
            gender = gender_result.scalar_one_or_none()
            
            class_result = await db.execute(select(Class).limit(1))
            class_obj = class_result.scalar_one_or_none()
            
            session_result = await db.execute(select(SessionYear).where(SessionYear.is_current == True))
            session_year = session_result.scalar_one_or_none()
            
            if not all([gender, class_obj, session_year]):
                print("❌ Missing required metadata")
                return False
            
            # Create student without email (should auto-generate)
            student_data = StudentCreate(
                admission_number='TEST_EMAIL_GEN_001',
                first_name='AutoEmail',
                last_name='TestStudent',
                date_of_birth=date(2010, 5, 20),
                gender_id=gender.id,
                class_id=class_obj.id,
                session_year_id=session_year.id,
                father_name='Test Father',
                mother_name='Test Mother',
                admission_date=date.today()
                # Note: No email provided - should be auto-generated
            )
            
            student = await student_crud.create_with_validation(db, obj_in=student_data)
            
            print(f"✅ Student created: {student.first_name} {student.last_name}")
            print(f"   Student ID: {student.id}")
            print(f"   Auto-generated email: {student.email}")
            print(f"   User ID: {student.user_id}")
            
            # Verify email was generated correctly
            expected_email_base = "autoemail.teststudent.20052010@sunriseschool.edu"
            assert student.email is not None
            assert validate_generated_email(student.email)
            assert "autoemail.teststudent.20052010" in student.email
            
            # Verify user account was created and linked
            assert student.user_id is not None
            
            user_result = await db.execute(select(User).where(User.id == student.user_id))
            user = user_result.scalar_one_or_none()
            assert user is not None
            assert user.email == student.email
            
            print("✅ Student creation with email generation successful!")
            return True
            
        except Exception as e:
            print(f"❌ Student creation test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            break


if __name__ == "__main__":
    # Run unit tests
    test_instance = TestEmailGeneration()
    
    print("🧪 RUNNING EMAIL GENERATION TESTS")
    print("=" * 50)
    
    unit_tests = [
        ("Name sanitization", test_instance.test_sanitize_name),
        ("Date formatting", test_instance.test_format_date_for_email),
        ("Base email generation", test_instance.test_generate_base_email),
        ("Email validation", test_instance.test_validate_generated_email),
        ("Email info extraction", test_instance.test_extract_info_from_generated_email),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in unit_tests:
        try:
            print(f"🔄 Running: {test_name}")
            test_func()
            print(f"✅ PASSED: {test_name}")
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {test_name} - {str(e)}")
            failed += 1
    
    print(f"\n📊 UNIT TEST RESULTS:")
    print(f"   Passed: {passed}")
    print(f"   Failed: {failed}")
    
    # Run integration tests
    integration_success = asyncio.run(test_email_generation_integration())
    student_creation_success = asyncio.run(test_student_creation_with_email_generation())
    
    total_success = failed == 0 and integration_success and student_creation_success
    
    print(f"\n🎯 OVERALL RESULT: {'✅ ALL TESTS PASSED' if total_success else '❌ SOME TESTS FAILED'}")
    
    exit(0 if total_success else 1)
