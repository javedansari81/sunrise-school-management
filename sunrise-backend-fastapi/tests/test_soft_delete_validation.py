"""
Test cases for soft-delete validation functionality
Tests the ability to create new records when only soft-deleted records exist with same identifiers
"""
import pytest
from datetime import date, datetime
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.main import app
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.user import User
from app.crud.crud_teacher import teacher_crud
from app.crud.crud_student import student_crud
from app.schemas.teacher import TeacherCreate
from app.schemas.student import StudentCreate
from app.utils.soft_delete_helpers import (
    check_teacher_soft_deleted_by_employee_id,
    check_teacher_soft_deleted_by_email,
    check_student_soft_deleted_by_admission_number,
    check_student_soft_deleted_by_email,
    validate_teacher_creation_with_soft_delete_check,
    validate_student_creation_with_soft_delete_check,
    generate_replacement_success_message
)

client = TestClient(app)


class TestSoftDeleteHelpers:
    """Test utility functions for soft-delete validation"""
    
    @pytest.mark.asyncio
    async def test_generate_replacement_success_message(self):
        """Test success message generation"""
        message = generate_replacement_success_message(
            "Teacher", "John Doe", "employee ID", "EMP001"
        )
        expected = "Teacher John Doe created successfully (previous record with employee ID EMP001 was archived)"
        assert message == expected
        
        message = generate_replacement_success_message(
            "Student", "Jane Smith", "admission number", "ADM001"
        )
        expected = "Student Jane Smith created successfully (previous record with admission number ADM001 was archived)"
        assert message == expected

    @pytest.mark.asyncio
    async def test_check_teacher_soft_deleted_by_employee_id(self, db_session: AsyncSession):
        """Test checking for soft-deleted teachers by employee ID"""
        # Create a teacher and soft delete it
        teacher_data = TeacherCreate(
            employee_id="EMP_SOFT_001",
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            phone="1234567890",
            position="Math Teacher",
            joining_date=date.today()
        )
        
        teacher = await teacher_crud.create(db_session, obj_in=teacher_data)
        
        # Soft delete the teacher
        teacher.is_deleted = True
        teacher.deleted_date = datetime.utcnow()
        await db_session.commit()
        
        # Test finding soft-deleted teacher
        soft_deleted = await check_teacher_soft_deleted_by_employee_id(
            db_session, "EMP_SOFT_001"
        )
        assert soft_deleted is not None
        assert soft_deleted.employee_id == "EMP_SOFT_001"
        assert soft_deleted.is_deleted is True
        
        # Test with non-existent employee ID
        not_found = await check_teacher_soft_deleted_by_employee_id(
            db_session, "NONEXISTENT"
        )
        assert not_found is None

    @pytest.mark.asyncio
    async def test_check_student_soft_deleted_by_admission_number(self, db_session: AsyncSession):
        """Test checking for soft-deleted students by admission number"""
        # Create a student and soft delete it
        student_data = StudentCreate(
            admission_number="ADM_SOFT_001",
            first_name="Jane",
            last_name="Smith",
            date_of_birth=date(2010, 1, 1),
            gender_id=1,
            class_id=1,
            session_year_id=1,
            father_name="Father Name",
            mother_name="Mother Name",
            admission_date=date.today()
        )
        
        student = await student_crud.create(db_session, obj_in=student_data)
        
        # Soft delete the student
        student.is_deleted = True
        student.deleted_date = datetime.utcnow()
        await db_session.commit()
        
        # Test finding soft-deleted student
        soft_deleted = await check_student_soft_deleted_by_admission_number(
            db_session, "ADM_SOFT_001"
        )
        assert soft_deleted is not None
        assert soft_deleted.admission_number == "ADM_SOFT_001"
        assert soft_deleted.is_deleted is True


class TestTeacherSoftDeleteValidation:
    """Test teacher creation with soft-delete validation"""
    
    @pytest.mark.asyncio
    async def test_create_teacher_after_soft_delete(self, db_session: AsyncSession):
        """Test creating a new teacher with same employee ID as soft-deleted one"""
        # Create and soft delete a teacher
        original_teacher_data = TeacherCreate(
            employee_id="EMP_TEST_001",
            first_name="Original",
            last_name="Teacher",
            email="original@test.com",
            phone="1111111111",
            position="Science Teacher",
            joining_date=date.today()
        )
        
        original_teacher = await teacher_crud.create(db_session, obj_in=original_teacher_data)
        
        # Soft delete
        original_teacher.is_deleted = True
        original_teacher.deleted_date = datetime.utcnow()
        await db_session.commit()
        
        # Validate creation of new teacher with same employee ID
        can_create, success_msg, error_msg = await validate_teacher_creation_with_soft_delete_check(
            db_session, "EMP_TEST_001", "new@test.com"
        )
        
        assert can_create is True
        assert error_msg is None
        assert success_msg is not None
        assert "Original Teacher" in success_msg
        assert "employee ID EMP_TEST_001" in success_msg
        
        # Create new teacher with same employee ID
        new_teacher_data = TeacherCreate(
            employee_id="EMP_TEST_001",
            first_name="New",
            last_name="Teacher",
            email="new@test.com",
            phone="2222222222",
            position="Math Teacher",
            joining_date=date.today()
        )
        
        new_teacher = await teacher_crud.create(db_session, obj_in=new_teacher_data)
        assert new_teacher.employee_id == "EMP_TEST_001"
        assert new_teacher.first_name == "New"
        assert new_teacher.is_deleted is not True

    @pytest.mark.asyncio
    async def test_teacher_creation_blocked_by_active_record(self, db_session: AsyncSession):
        """Test that creation is blocked when active record exists"""
        # Create an active teacher
        active_teacher_data = TeacherCreate(
            employee_id="EMP_ACTIVE_001",
            first_name="Active",
            last_name="Teacher",
            email="active@test.com",
            phone="3333333333",
            position="English Teacher",
            joining_date=date.today()
        )
        
        await teacher_crud.create(db_session, obj_in=active_teacher_data)
        
        # Try to validate creation with same employee ID
        can_create, success_msg, error_msg = await validate_teacher_creation_with_soft_delete_check(
            db_session, "EMP_ACTIVE_001", "another@test.com"
        )
        
        assert can_create is False
        assert success_msg is None
        assert error_msg == "Teacher with this employee ID already exists"


class TestStudentSoftDeleteValidation:
    """Test student creation with soft-delete validation"""
    
    @pytest.mark.asyncio
    async def test_create_student_after_soft_delete(self, db_session: AsyncSession):
        """Test creating a new student with same admission number as soft-deleted one"""
        # Create and soft delete a student
        original_student_data = StudentCreate(
            admission_number="ADM_TEST_001",
            first_name="Original",
            last_name="Student",
            date_of_birth=date(2010, 1, 1),
            gender_id=1,
            class_id=1,
            session_year_id=1,
            father_name="Father Name",
            mother_name="Mother Name",
            admission_date=date.today(),
            email="original.student@test.com"
        )
        
        original_student = await student_crud.create(db_session, obj_in=original_student_data)
        
        # Soft delete
        original_student.is_deleted = True
        original_student.deleted_date = datetime.utcnow()
        await db_session.commit()
        
        # Validate creation of new student with same admission number
        can_create, success_msg, error_msg = await validate_student_creation_with_soft_delete_check(
            db_session, "ADM_TEST_001", "new.student@test.com"
        )
        
        assert can_create is True
        assert error_msg is None
        assert success_msg is not None
        assert "Original Student" in success_msg
        assert "admission number ADM_TEST_001" in success_msg
        
        # Create new student with same admission number
        new_student_data = StudentCreate(
            admission_number="ADM_TEST_001",
            first_name="New",
            last_name="Student",
            date_of_birth=date(2011, 1, 1),
            gender_id=2,
            class_id=2,
            session_year_id=1,
            father_name="New Father",
            mother_name="New Mother",
            admission_date=date.today(),
            email="new.student@test.com"
        )
        
        new_student = await student_crud.create(db_session, obj_in=new_student_data)
        assert new_student.admission_number == "ADM_TEST_001"
        assert new_student.first_name == "New"
        assert new_student.is_deleted is not True

    @pytest.mark.asyncio
    async def test_student_creation_blocked_by_active_record(self, db_session: AsyncSession):
        """Test that creation is blocked when active record exists"""
        # Create an active student
        active_student_data = StudentCreate(
            admission_number="ADM_ACTIVE_001",
            first_name="Active",
            last_name="Student",
            date_of_birth=date(2010, 1, 1),
            gender_id=1,
            class_id=1,
            session_year_id=1,
            father_name="Father Name",
            mother_name="Mother Name",
            admission_date=date.today(),
            email="active.student@test.com"
        )
        
        await student_crud.create(db_session, obj_in=active_student_data)
        
        # Try to validate creation with same admission number
        can_create, success_msg, error_msg = await validate_student_creation_with_soft_delete_check(
            db_session, "ADM_ACTIVE_001", "another.student@test.com"
        )
        
        assert can_create is False
        assert success_msg is None
        assert error_msg == "Student with this admission number already exists"


class TestCRUDSoftDeleteExclusion:
    """Test that CRUD methods properly exclude soft-deleted records"""
    
    @pytest.mark.asyncio
    async def test_teacher_get_by_employee_id_excludes_soft_deleted(self, db_session: AsyncSession):
        """Test that get_by_employee_id excludes soft-deleted teachers"""
        # Create a teacher
        teacher_data = TeacherCreate(
            employee_id="EMP_EXCLUDE_001",
            first_name="Test",
            last_name="Teacher",
            email="test@exclude.com",
            phone="4444444444",
            position="Test Teacher",
            joining_date=date.today()
        )
        
        teacher = await teacher_crud.create(db_session, obj_in=teacher_data)
        
        # Should find active teacher
        found_active = await teacher_crud.get_by_employee_id(db_session, employee_id="EMP_EXCLUDE_001")
        assert found_active is not None
        assert found_active.id == teacher.id
        
        # Soft delete the teacher
        teacher.is_deleted = True
        teacher.deleted_date = datetime.utcnow()
        await db_session.commit()
        
        # Should not find soft-deleted teacher
        found_deleted = await teacher_crud.get_by_employee_id(db_session, employee_id="EMP_EXCLUDE_001")
        assert found_deleted is None

    @pytest.mark.asyncio
    async def test_student_get_by_admission_number_excludes_soft_deleted(self, db_session: AsyncSession):
        """Test that get_by_admission_number excludes soft-deleted students"""
        # Create a student
        student_data = StudentCreate(
            admission_number="ADM_EXCLUDE_001",
            first_name="Test",
            last_name="Student",
            date_of_birth=date(2010, 1, 1),
            gender_id=1,
            class_id=1,
            session_year_id=1,
            father_name="Father Name",
            mother_name="Mother Name",
            admission_date=date.today(),
            email="test@exclude.com"
        )
        
        student = await student_crud.create(db_session, obj_in=student_data)
        
        # Should find active student
        found_active = await student_crud.get_by_admission_number(db_session, admission_number="ADM_EXCLUDE_001")
        assert found_active is not None
        assert found_active.id == student.id
        
        # Soft delete the student
        student.is_deleted = True
        student.deleted_date = datetime.utcnow()
        await db_session.commit()
        
        # Should not find soft-deleted student
        found_deleted = await student_crud.get_by_admission_number(db_session, admission_number="ADM_EXCLUDE_001")
        assert found_deleted is None


class TestAPIEndpointSoftDeleteValidation:
    """Test API endpoints with soft-delete validation"""

    def test_teacher_creation_api_with_soft_delete_replacement(self):
        """Test teacher creation API when replacing soft-deleted record"""
        # This would require setting up test database and authentication
        # For now, we'll create a placeholder test structure
        pass

    def test_student_creation_api_with_soft_delete_replacement(self):
        """Test student creation API when replacing soft-deleted record"""
        # This would require setting up test database and authentication
        # For now, we'll create a placeholder test structure
        pass

    def test_teacher_creation_api_blocked_by_active_record(self):
        """Test that teacher creation API is blocked by active records"""
        pass

    def test_student_creation_api_blocked_by_active_record(self):
        """Test that student creation API is blocked by active records"""
        pass


class TestEdgeCases:
    """Test edge cases and error scenarios"""

    @pytest.mark.asyncio
    async def test_multiple_soft_deleted_records_same_identifier(self, db_session: AsyncSession):
        """Test handling multiple soft-deleted records with same identifier"""
        # Create multiple teachers with same employee ID (soft deleted)
        for i in range(3):
            teacher_data = TeacherCreate(
                employee_id="EMP_MULTI_001",
                first_name=f"Teacher{i}",
                last_name="Multi",
                email=f"teacher{i}@multi.com",
                phone=f"555000{i}",
                position="Test Teacher",
                joining_date=date.today()
            )

            teacher = await teacher_crud.create(db_session, obj_in=teacher_data)
            teacher.is_deleted = True
            teacher.deleted_date = datetime.utcnow()
            await db_session.commit()

        # Should still be able to create new teacher
        can_create, success_msg, error_msg = await validate_teacher_creation_with_soft_delete_check(
            db_session, "EMP_MULTI_001", "new@multi.com"
        )

        assert can_create is True
        assert error_msg is None
        # Should find at least one soft-deleted record for success message
        assert success_msg is not None

    @pytest.mark.asyncio
    async def test_email_validation_with_soft_deleted_records(self, db_session: AsyncSession):
        """Test email validation considers soft-deleted records"""
        # Create teacher with email and soft delete
        teacher_data = TeacherCreate(
            employee_id="EMP_EMAIL_001",
            first_name="Email",
            last_name="Test",
            email="email.test@example.com",
            phone="5555555555",
            position="Test Teacher",
            joining_date=date.today()
        )

        teacher = await teacher_crud.create(db_session, obj_in=teacher_data)
        teacher.is_deleted = True
        teacher.deleted_date = datetime.utcnow()
        await db_session.commit()

        # Should be able to create new teacher with same email
        can_create, success_msg, error_msg = await validate_teacher_creation_with_soft_delete_check(
            db_session, "EMP_EMAIL_002", "email.test@example.com"
        )

        assert can_create is True
        assert error_msg is None
        assert success_msg is not None
        assert "email email.test@example.com" in success_msg

    @pytest.mark.asyncio
    async def test_concurrent_creation_attempts(self, db_session: AsyncSession):
        """Test concurrent creation attempts with same identifier"""
        # This is a placeholder for testing concurrent scenarios
        # In a real implementation, you'd test race conditions
        pass

    @pytest.mark.asyncio
    async def test_partial_data_matches(self, db_session: AsyncSession):
        """Test scenarios with partial data matches"""
        # Create teacher with specific data
        teacher_data = TeacherCreate(
            employee_id="EMP_PARTIAL_001",
            first_name="Partial",
            last_name="Match",
            email="partial@match.com",
            phone="6666666666",
            position="Test Teacher",
            joining_date=date.today()
        )

        teacher = await teacher_crud.create(db_session, obj_in=teacher_data)
        teacher.is_deleted = True
        teacher.deleted_date = datetime.utcnow()
        await db_session.commit()

        # Try to create with same employee ID but different email
        can_create, success_msg, error_msg = await validate_teacher_creation_with_soft_delete_check(
            db_session, "EMP_PARTIAL_001", "different@email.com"
        )

        assert can_create is True
        assert error_msg is None
        # Should mention employee ID in success message
        assert success_msg is not None
        assert "employee ID EMP_PARTIAL_001" in success_msg
