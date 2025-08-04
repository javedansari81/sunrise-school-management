"""
Tests for teacher management API endpoints.

This module contains tests for:
- Teacher CRUD operations
- Teacher configuration endpoints
- Teacher search and filtering
"""
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
@pytest.mark.api
class TestTeacherEndpoints:
    """Test class for teacher management endpoints."""

    async def test_teacher_configuration_endpoint(self, async_client: AsyncClient):
        """Test teacher-management configuration endpoint."""
        response = await async_client.get("/api/v1/configuration/teacher-management/")
        
        assert response.status_code == status.HTTP_200_OK
        config = response.json()
        
        # Verify expected configuration keys
        expected_keys = ["genders", "qualifications", "employment_statuses"]
        for key in expected_keys:
            assert key in config, f"Missing configuration key: {key}"
            assert isinstance(config[key], list), f"{key} should be a list"

    async def test_get_teachers_list(
        self, 
        async_client: AsyncClient, 
        auth_headers: dict
    ):
        """Test getting list of teachers."""
        response = await async_client.get(
            "/api/v1/teachers/",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should return a list
        assert isinstance(data, list)

    async def test_get_teacher_by_id(
        self, 
        async_client: AsyncClient, 
        auth_headers: dict
    ):
        """Test getting a specific teacher by ID."""
        # First get the list to find a valid teacher ID
        list_response = await async_client.get(
            "/api/v1/teachers/",
            headers=auth_headers
        )
        teachers = list_response.json()
        
        if teachers:
            teacher_id = teachers[0]["id"]
            response = await async_client.get(
                f"/api/v1/teachers/{teacher_id}",
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_200_OK
            teacher_data = response.json()
            assert teacher_data["id"] == teacher_id

    async def test_get_nonexistent_teacher(
        self, 
        async_client: AsyncClient, 
        auth_headers: dict
    ):
        """Test getting a teacher that doesn't exist."""
        response = await async_client.get(
            "/api/v1/teachers/99999",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_create_teacher(
        self, 
        async_client: AsyncClient, 
        auth_headers: dict,
        sample_teacher_data: dict
    ):
        """Test creating a new teacher."""
        response = await async_client.post(
            "/api/v1/teachers/",
            json=sample_teacher_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        teacher_data = response.json()
        
        # Verify created teacher data
        assert teacher_data["employee_id"] == sample_teacher_data["employee_id"]
        assert teacher_data["first_name"] == sample_teacher_data["first_name"]
        assert teacher_data["last_name"] == sample_teacher_data["last_name"]
        assert teacher_data["email"] == sample_teacher_data["email"]

    async def test_create_teacher_duplicate_employee_id(
        self, 
        async_client: AsyncClient, 
        auth_headers: dict,
        sample_teacher_data: dict
    ):
        """Test creating a teacher with duplicate employee ID."""
        # Create first teacher
        await async_client.post(
            "/api/v1/teachers/",
            json=sample_teacher_data,
            headers=auth_headers
        )
        
        # Try to create another with same employee_id
        duplicate_data = sample_teacher_data.copy()
        duplicate_data["email"] = "different@test.com"
        
        response = await async_client.post(
            "/api/v1/teachers/",
            json=duplicate_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_update_teacher(
        self, 
        async_client: AsyncClient, 
        auth_headers: dict,
        sample_teacher_data: dict
    ):
        """Test updating a teacher."""
        # Create a teacher first
        create_response = await async_client.post(
            "/api/v1/teachers/",
            json=sample_teacher_data,
            headers=auth_headers
        )
        teacher_data = create_response.json()
        teacher_id = teacher_data["id"]
        
        # Update the teacher
        update_data = {
            "phone": "9999999999",
            "position": "Senior Teacher"
        }
        
        response = await async_client.put(
            f"/api/v1/teachers/{teacher_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        updated_data = response.json()
        
        assert updated_data["phone"] == update_data["phone"]
        assert updated_data["position"] == update_data["position"]

    async def test_delete_teacher(
        self, 
        async_client: AsyncClient, 
        auth_headers: dict,
        sample_teacher_data: dict
    ):
        """Test deleting a teacher (soft delete)."""
        # Create a teacher first
        create_response = await async_client.post(
            "/api/v1/teachers/",
            json=sample_teacher_data,
            headers=auth_headers
        )
        teacher_data = create_response.json()
        teacher_id = teacher_data["id"]
        
        # Delete the teacher
        response = await async_client.delete(
            f"/api/v1/teachers/{teacher_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify teacher is soft deleted (should return 404 when fetched)
        get_response = await async_client.get(
            f"/api/v1/teachers/{teacher_id}",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    async def test_teacher_search_by_department(
        self, 
        async_client: AsyncClient, 
        auth_headers: dict
    ):
        """Test searching teachers by department."""
        response = await async_client.get(
            "/api/v1/teachers/department/Mathematics",
            headers=auth_headers
        )
        
        # Should return successfully even if no teachers found
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    async def test_unauthorized_access(self, async_client: AsyncClient):
        """Test that endpoints require authentication."""
        endpoints = [
            "/api/v1/teachers/",
            "/api/v1/teachers/1",
        ]
        
        for endpoint in endpoints:
            response = await async_client.get(endpoint)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
