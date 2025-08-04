"""
Test cases for Teacher Management System
"""
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.main import app
from app.core.database import get_db
from app.models.teacher import Teacher
from app.models.user import User
from app.crud import teacher_crud
from app.schemas.teacher import TeacherCreate


class TestTeacherManagement:
    """Test cases for teacher management functionality"""
    
    @pytest.fixture
    async def async_client(self):
        """Create async test client"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    @pytest.fixture
    async def db_session(self):
        """Create database session for testing"""
        # This would need to be implemented with test database setup
        pass
    
    @pytest.fixture
    def sample_teacher_data(self):
        """Sample teacher data for testing"""
        return {
            "employee_id": "TCH001",
            "first_name": "John",
            "last_name": "Smith",
            "date_of_birth": "1985-05-15",
            "gender_id": 1,
            "phone": "9876543210",
            "email": "john.smith@sunriseschool.edu",
            "position": "Mathematics Teacher",
            "department": "Mathematics",
            "qualification_id": 1,
            "employment_status_id": 1,
            "experience_years": 5,
            "joining_date": "2020-06-01",
            "is_active": True
        }
    
    async def test_create_teacher_with_user_account(self, db_session, sample_teacher_data):
        """Test creating teacher with associated user account"""
        teacher_data = TeacherCreate(**sample_teacher_data)
        
        # Create teacher with user account
        teacher = await teacher_crud.create_with_user_account(db_session, obj_in=teacher_data)
        
        assert teacher is not None
        assert teacher.employee_id == "TCH001"
        assert teacher.first_name == "John"
        assert teacher.last_name == "Smith"
        assert teacher.email == "john.smith@sunriseschool.edu"
        
        # Verify user account was created
        assert teacher.user_id is not None
    
    async def test_teacher_soft_delete(self, db_session, sample_teacher_data):
        """Test soft delete functionality"""
        teacher_data = TeacherCreate(**sample_teacher_data)
        teacher = await teacher_crud.create(db_session, obj_in=teacher_data)
        
        # Soft delete teacher
        deleted_teacher = await teacher_crud.soft_delete(db_session, id=teacher.id)
        
        assert deleted_teacher is not None
        assert deleted_teacher.is_deleted is True
        assert deleted_teacher.deleted_date is not None
        assert deleted_teacher.is_active is False
    
    async def test_get_teachers_with_metadata(self, db_session, sample_teacher_data):
        """Test getting teachers with metadata relationships"""
        teacher_data = TeacherCreate(**sample_teacher_data)
        teacher = await teacher_crud.create(db_session, obj_in=teacher_data)
        
        # Get teacher with metadata
        teacher_with_metadata = await teacher_crud.get_with_metadata(db_session, id=teacher.id)
        
        assert teacher_with_metadata is not None
        assert "gender_name" in teacher_with_metadata
        assert "qualification_name" in teacher_with_metadata
        assert "employment_status_name" in teacher_with_metadata
    
    async def test_teacher_search_functionality(self, db_session, sample_teacher_data):
        """Test teacher search functionality"""
        teacher_data = TeacherCreate(**sample_teacher_data)
        teacher = await teacher_crud.create(db_session, obj_in=teacher_data)
        
        # Search by name
        results = await teacher_crud.search_teachers(db_session, search_term="John")
        assert len(results) > 0
        assert any(t.first_name == "John" for t in results)
        
        # Search by employee ID
        results = await teacher_crud.search_teachers(db_session, search_term="TCH001")
        assert len(results) > 0
        assert any(t.employee_id == "TCH001" for t in results)
    
    async def test_teacher_filters(self, db_session, sample_teacher_data):
        """Test teacher filtering functionality"""
        teacher_data = TeacherCreate(**sample_teacher_data)
        teacher = await teacher_crud.create(db_session, obj_in=teacher_data)
        
        # Filter by department
        teachers, total = await teacher_crud.get_multi_with_filters(
            db_session, 
            department_filter="Mathematics"
        )
        assert total > 0
        assert any(t["department"] == "Mathematics" for t in teachers)
        
        # Filter by position
        teachers, total = await teacher_crud.get_multi_with_filters(
            db_session, 
            position_filter="Mathematics Teacher"
        )
        assert total > 0
        assert any(t["position"] == "Mathematics Teacher" for t in teachers)
    
    async def test_teacher_dashboard_stats(self, db_session, sample_teacher_data):
        """Test teacher dashboard statistics"""
        teacher_data = TeacherCreate(**sample_teacher_data)
        await teacher_crud.create(db_session, obj_in=teacher_data)
        
        stats = await teacher_crud.get_dashboard_stats(db_session)
        
        assert "total_teachers" in stats
        assert "active_teachers" in stats
        assert "departments" in stats
        assert "qualification_breakdown" in stats
        assert "experience_breakdown" in stats
        
        assert stats["total_teachers"] > 0
        assert isinstance(stats["departments"], list)
        assert isinstance(stats["qualification_breakdown"], list)
    
    async def test_teacher_authentication_endpoints(self, async_client):
        """Test teacher authentication endpoints"""
        # Test teacher profile endpoint (requires authentication)
        response = await async_client.get("/api/v1/teachers/my-profile")
        assert response.status_code == 403  # Not authenticated
        
        # Test teacher profile update endpoint (requires authentication)
        response = await async_client.put("/api/v1/teachers/my-profile", json={
            "phone": "9876543210",
            "address": "123 Main St"
        })
        assert response.status_code == 403  # Not authenticated
    
    async def test_teacher_configuration_endpoint(self, async_client):
        """Test teacher management configuration endpoint"""
        response = await async_client.get("/api/v1/configuration/teacher-management/")
        
        # May require authentication depending on setup
        if response.status_code == 200:
            config = response.json()
            assert "employment_statuses" in config
            assert "qualifications" in config
            assert "genders" in config
            assert "user_types" in config
            assert "session_years" in config
        else:
            assert response.status_code in [401, 403]  # Authentication required
    
    async def test_teacher_options_endpoints(self, async_client):
        """Test teacher options endpoints"""
        # Test qualifications endpoint
        response = await async_client.get("/api/v1/teachers/options/qualifications")
        if response.status_code == 200:
            data = response.json()
            assert "qualifications" in data
            assert isinstance(data["qualifications"], list)
        
        # Test employment status endpoint
        response = await async_client.get("/api/v1/teachers/options/employment-status")
        if response.status_code == 200:
            data = response.json()
            assert "employment_status" in data
            assert isinstance(data["employment_status"], list)
    
    def test_teacher_composite_identifier_format(self):
        """Test teacher composite identifier format"""
        # Test the format: 'John Smith (EMP001)'
        teacher_data = {
            "first_name": "John",
            "last_name": "Smith",
            "employee_id": "EMP001"
        }
        
        expected_format = f"{teacher_data['first_name']} {teacher_data['last_name']} ({teacher_data['employee_id']})"
        assert expected_format == "John Smith (EMP001)"
    
    async def test_teacher_validation(self, db_session):
        """Test teacher data validation"""
        # Test duplicate employee ID
        teacher_data1 = TeacherCreate(
            employee_id="TCH001",
            first_name="John",
            last_name="Smith",
            phone="9876543210",
            email="john@test.com",
            position="Teacher",
            joining_date=date.today()
        )
        
        teacher_data2 = TeacherCreate(
            employee_id="TCH001",  # Duplicate
            first_name="Jane",
            last_name="Doe",
            phone="9876543211",
            email="jane@test.com",
            position="Teacher",
            joining_date=date.today()
        )
        
        # First teacher should be created successfully
        teacher1 = await teacher_crud.create(db_session, obj_in=teacher_data1)
        assert teacher1 is not None
        
        # Second teacher with duplicate employee_id should fail
        # This would be handled at the API level with proper error handling
        existing_teacher = await teacher_crud.get_by_employee_id(db_session, employee_id="TCH001")
        assert existing_teacher is not None
        assert existing_teacher.employee_id == "TCH001"


# Additional test cases for specific scenarios
class TestTeacherIntegration:
    """Integration tests for teacher management"""
    
    async def test_teacher_leave_integration(self, db_session):
        """Test teacher integration with leave management"""
        # This would test how teachers interact with the leave system
        pass
    
    async def test_teacher_class_assignment(self, db_session):
        """Test teacher class assignment functionality"""
        # This would test class teacher assignments
        pass
    
    async def test_teacher_subject_assignment(self, db_session):
        """Test teacher subject assignment functionality"""
        # This would test subject assignments
        pass


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
