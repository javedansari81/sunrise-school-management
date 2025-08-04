"""
Tests for teacher profile API endpoints.

This module contains tests for:
- GET /api/v1/teachers/my-profile
- PUT /api/v1/teachers/my-profile
"""
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.profile
class TestTeacherProfile:
    """Test class for teacher profile endpoints."""

    async def test_get_my_profile_success(
        self, 
        async_client: AsyncClient, 
        auth_headers: dict
    ):
        """Test successful retrieval of teacher profile."""
        response = await async_client.get(
            "/api/v1/teachers/my-profile",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify required fields are present
        assert "id" in data
        assert "employee_id" in data
        assert "first_name" in data
        assert "last_name" in data
        assert "email" in data
        assert "position" in data
        assert "department" in data

    async def test_get_my_profile_unauthorized(self, async_client: AsyncClient):
        """Test profile retrieval without authentication."""
        response = await async_client.get("/api/v1/teachers/my-profile")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_update_my_profile_success(
        self, 
        async_client: AsyncClient, 
        auth_headers: dict
    ):
        """Test successful update of teacher profile."""
        update_data = {
            "phone": "9876543210",
            "address": "Updated Address, Test City",
            "emergency_contact_name": "Emergency Contact",
            "emergency_contact_phone": "9876543211"
        }
        
        response = await async_client.put(
            "/api/v1/teachers/my-profile",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify updated fields
        assert data["phone"] == update_data["phone"]
        assert data["address"] == update_data["address"]
        assert data["emergency_contact_name"] == update_data["emergency_contact_name"]
        assert data["emergency_contact_phone"] == update_data["emergency_contact_phone"]

    async def test_update_my_profile_unauthorized(self, async_client: AsyncClient):
        """Test profile update without authentication."""
        update_data = {"phone": "9876543210"}
        
        response = await async_client.put(
            "/api/v1/teachers/my-profile",
            json=update_data
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_update_my_profile_invalid_data(
        self, 
        async_client: AsyncClient, 
        auth_headers: dict
    ):
        """Test profile update with invalid data."""
        update_data = {
            "phone": "invalid_phone",  # Invalid phone format
            "email": "invalid_email"   # Invalid email format
        }
        
        response = await async_client.put(
            "/api/v1/teachers/my-profile",
            json=update_data,
            headers=auth_headers
        )
        
        # Should return validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_profile_data_consistency(
        self, 
        async_client: AsyncClient, 
        auth_headers: dict
    ):
        """Test that profile data remains consistent after update."""
        # Get initial profile
        initial_response = await async_client.get(
            "/api/v1/teachers/my-profile",
            headers=auth_headers
        )
        initial_data = initial_response.json()
        
        # Update profile
        update_data = {"phone": "9999999999"}
        update_response = await async_client.put(
            "/api/v1/teachers/my-profile",
            json=update_data,
            headers=auth_headers
        )
        updated_data = update_response.json()
        
        # Verify consistency
        assert updated_data["id"] == initial_data["id"]
        assert updated_data["employee_id"] == initial_data["employee_id"]
        assert updated_data["first_name"] == initial_data["first_name"]
        assert updated_data["last_name"] == initial_data["last_name"]
        assert updated_data["phone"] == update_data["phone"]  # Should be updated

    @pytest.mark.slow
    async def test_profile_performance(
        self, 
        async_client: AsyncClient, 
        auth_headers: dict
    ):
        """Test profile endpoint performance."""
        import time
        
        start_time = time.time()
        response = await async_client.get(
            "/api/v1/teachers/my-profile",
            headers=auth_headers
        )
        end_time = time.time()
        
        assert response.status_code == status.HTTP_200_OK
        # Profile should load within 1 second
        assert (end_time - start_time) < 1.0
