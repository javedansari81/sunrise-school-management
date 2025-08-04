"""
Tests for authentication API endpoints.

This module contains tests for:
- User login/logout
- Token generation and validation
- User profile retrieval
- Authentication workflows
"""
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.auth
class TestAuthentication:
    """Test class for authentication endpoints."""

    async def test_teacher_login_success(self, async_client: AsyncClient):
        """Test successful teacher login."""
        login_data = {
            "username": "amit.kumar@gmail.com",
            "password": "Sunrise@001"
        }
        
        response = await async_client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify token response structure
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user_info" in data

    async def test_teacher_login_json_format(self, async_client: AsyncClient):
        """Test teacher login with JSON format."""
        login_data = {
            "email": "amit.kumar@gmail.com",
            "password": "Sunrise@001"
        }
        
        response = await async_client.post(
            "/api/v1/auth/login-json",
            json=login_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify response structure
        assert "access_token" in data
        assert "token_type" in data
        assert "user_info" in data
        
        # Verify user info structure
        user_info = data["user_info"]
        assert "id" in user_info
        assert "email" in user_info
        assert "user_type" in user_info
        assert "permissions" in user_info

    async def test_login_invalid_credentials(self, async_client: AsyncClient):
        """Test login with invalid credentials."""
        login_data = {
            "username": "invalid@email.com",
            "password": "wrongpassword"
        }
        
        response = await async_client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_login_missing_credentials(self, async_client: AsyncClient):
        """Test login with missing credentials."""
        # Missing password
        login_data = {"username": "test@email.com"}
        
        response = await async_client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_get_current_user_info_with_token(self, async_client: AsyncClient):
        """Test getting current user info with valid token."""
        # First login to get token
        login_data = {
            "email": "amit.kumar@gmail.com",
            "password": "Sunrise@001"
        }
        
        login_response = await async_client.post(
            "/api/v1/auth/login-json",
            json=login_data
        )
        
        assert login_response.status_code == status.HTTP_200_OK
        token_data = login_response.json()
        token = token_data["access_token"]
        
        # Get user info with token
        headers = {"Authorization": f"Bearer {token}"}
        response = await async_client.get(
            "/api/v1/auth/me",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        user_data = response.json()
        
        # Verify user data structure
        assert "id" in user_data
        assert "email" in user_data
        assert "user_type" in user_data
        assert "permissions" in user_data
        assert user_data["email"] == "amit.kumar@gmail.com"

    async def test_get_current_user_info_without_token(self, async_client: AsyncClient):
        """Test getting current user info without token."""
        response = await async_client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_current_user_info_invalid_token(self, async_client: AsyncClient):
        """Test getting current user info with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await async_client.get(
            "/api/v1/auth/me",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_token_expiration_handling(self, async_client: AsyncClient):
        """Test handling of expired tokens."""
        # This would require mocking time or using a very short token expiry
        # For now, we'll test with a malformed token that should fail
        headers = {"Authorization": "Bearer expired.token.here"}
        response = await async_client.get(
            "/api/v1/auth/me",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_complete_authentication_workflow(self, async_client: AsyncClient):
        """Test complete authentication workflow from login to profile access."""
        # Step 1: Login
        login_data = {
            "email": "amit.kumar@gmail.com",
            "password": "Sunrise@001"
        }
        
        login_response = await async_client.post(
            "/api/v1/auth/login-json",
            json=login_data
        )
        
        assert login_response.status_code == status.HTTP_200_OK
        token_data = login_response.json()
        token = token_data["access_token"]
        
        # Step 2: Get user info
        headers = {"Authorization": f"Bearer {token}"}
        user_response = await async_client.get(
            "/api/v1/auth/me",
            headers=headers
        )
        
        assert user_response.status_code == status.HTTP_200_OK
        user_data = user_response.json()
        
        # Step 3: Access protected resource (teacher profile)
        profile_response = await async_client.get(
            "/api/v1/teachers/my-profile",
            headers=headers
        )
        
        assert profile_response.status_code == status.HTTP_200_OK
        profile_data = profile_response.json()
        
        # Verify data consistency
        assert "first_name" in profile_data
        assert "last_name" in profile_data
        assert "employee_id" in profile_data

    async def test_different_user_types_login(self, async_client: AsyncClient):
        """Test login for different user types if available."""
        # This test assumes we have different user types in the system
        # We'll test with the known teacher account
        login_data = {
            "email": "amit.kumar@gmail.com",
            "password": "Sunrise@001"
        }
        
        response = await async_client.post(
            "/api/v1/auth/login-json",
            json=login_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify user type is correctly identified
        user_info = data["user_info"]
        assert "user_type" in user_info
        # Should be teacher type based on the test account
        assert user_info["user_type"] in ["TEACHER", "teacher", 2]

    @pytest.mark.slow
    async def test_login_performance(self, async_client: AsyncClient):
        """Test login endpoint performance."""
        import time
        
        login_data = {
            "email": "amit.kumar@gmail.com",
            "password": "Sunrise@001"
        }
        
        start_time = time.time()
        response = await async_client.post(
            "/api/v1/auth/login-json",
            json=login_data
        )
        end_time = time.time()
        
        assert response.status_code == status.HTTP_200_OK
        # Login should complete within 2 seconds
        assert (end_time - start_time) < 2.0
