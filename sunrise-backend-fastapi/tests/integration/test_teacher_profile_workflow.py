"""
Integration tests for teacher profile workflow.

This module tests the complete workflow from login to profile management,
simulating real frontend interactions.
"""
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
@pytest.mark.integration
class TestTeacherProfileWorkflow:
    """Integration tests for teacher profile workflow."""

    async def test_complete_profile_workflow(self, async_client: AsyncClient):
        """Test the complete profile workflow as used by the frontend."""
        # Step 1: Login as teacher
        print("🔐 Step 1: Logging in as teacher...")
        login_data = {
            "email": "amit.kumar@gmail.com",
            "password": "Sunrise@001"
        }
        
        login_response = await async_client.post(
            "/api/v1/auth/login-json",
            json=login_data
        )
        
        assert login_response.status_code == status.HTTP_200_OK
        login_result = login_response.json()
        token = login_result["access_token"]
        print("✅ Login successful")
        
        # Step 2: Get teacher profile
        print("👤 Step 2: Getting teacher profile...")
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = await async_client.get(
            "/api/v1/teachers/my-profile",
            headers=headers
        )
        
        assert profile_response.status_code == status.HTTP_200_OK
        profile_data = profile_response.json()
        print("✅ Profile data retrieved successfully!")
        print(f"   Teacher: {profile_data.get('first_name')} {profile_data.get('last_name')}")
        print(f"   Employee ID: {profile_data.get('employee_id')}")
        print(f"   Position: {profile_data.get('position')}")
        
        # Verify required profile fields
        required_fields = [
            "id", "employee_id", "first_name", "last_name", 
            "email", "position", "department"
        ]
        for field in required_fields:
            assert field in profile_data, f"Missing required field: {field}"
        
        # Step 3: Test profile update
        print("📝 Step 3: Testing profile update...")
        update_data = {
            "phone": "9876543210",
            "address": "Updated Address, Test City",
            "emergency_contact_name": "Emergency Contact",
            "emergency_contact_phone": "9876543211"
        }
        
        update_response = await async_client.put(
            "/api/v1/teachers/my-profile",
            json=update_data,
            headers=headers
        )
        
        assert update_response.status_code == status.HTTP_200_OK
        updated_data = update_response.json()
        print("✅ Profile update successful!")
        print(f"   Updated phone: {updated_data.get('phone')}")
        print(f"   Updated address: {updated_data.get('address')}")
        
        # Verify updates were applied
        assert updated_data["phone"] == update_data["phone"]
        assert updated_data["address"] == update_data["address"]
        assert updated_data["emergency_contact_name"] == update_data["emergency_contact_name"]
        assert updated_data["emergency_contact_phone"] == update_data["emergency_contact_phone"]
        
        # Step 4: Verify persistence by fetching profile again
        print("🔍 Step 4: Verifying data persistence...")
        verify_response = await async_client.get(
            "/api/v1/teachers/my-profile",
            headers=headers
        )
        
        assert verify_response.status_code == status.HTTP_200_OK
        verified_data = verify_response.json()
        
        # Verify the updates persisted
        assert verified_data["phone"] == update_data["phone"]
        assert verified_data["address"] == update_data["address"]
        print("✅ Data persistence verified!")
        
        print("🎉 Complete workflow test passed!")

    async def test_profile_error_handling_workflow(self, async_client: AsyncClient):
        """Test error handling in the profile workflow."""
        # Test 1: Access profile without authentication
        print("🔒 Testing unauthorized access...")
        response = await async_client.get("/api/v1/teachers/my-profile")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        print("✅ Unauthorized access properly blocked")
        
        # Test 2: Login and test invalid profile update
        login_data = {
            "email": "amit.kumar@gmail.com",
            "password": "Sunrise@001"
        }
        
        login_response = await async_client.post(
            "/api/v1/auth/login-json",
            json=login_data
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test invalid data update
        print("❌ Testing invalid data handling...")
        invalid_update = {
            "phone": "invalid_phone_format",
            "email": "invalid_email_format"
        }
        
        update_response = await async_client.put(
            "/api/v1/teachers/my-profile",
            json=invalid_update,
            headers=headers
        )
        
        # Should handle validation errors gracefully
        assert update_response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST
        ]
        print("✅ Invalid data properly rejected")

    async def test_concurrent_profile_access(self, async_client: AsyncClient):
        """Test concurrent access to profile endpoints."""
        # Login first
        login_data = {
            "email": "amit.kumar@gmail.com",
            "password": "Sunrise@001"
        }
        
        login_response = await async_client.post(
            "/api/v1/auth/login-json",
            json=login_data
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Simulate concurrent profile requests
        import asyncio
        
        async def get_profile():
            return await async_client.get(
                "/api/v1/teachers/my-profile",
                headers=headers
            )
        
        # Make multiple concurrent requests
        tasks = [get_profile() for _ in range(5)]
        responses = await asyncio.gather(*tasks)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "employee_id" in data
            assert "first_name" in data
        
        print("✅ Concurrent access handled successfully")

    async def test_profile_data_consistency(self, async_client: AsyncClient):
        """Test data consistency across multiple operations."""
        # Login
        login_data = {
            "email": "amit.kumar@gmail.com",
            "password": "Sunrise@001"
        }
        
        login_response = await async_client.post(
            "/api/v1/auth/login-json",
            json=login_data
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get initial profile
        initial_response = await async_client.get(
            "/api/v1/teachers/my-profile",
            headers=headers
        )
        initial_data = initial_response.json()
        
        # Update profile multiple times
        updates = [
            {"phone": "1111111111"},
            {"phone": "2222222222"},
            {"phone": "3333333333"}
        ]
        
        for update in updates:
            update_response = await async_client.put(
                "/api/v1/teachers/my-profile",
                json=update,
                headers=headers
            )
            assert update_response.status_code == status.HTTP_200_OK
            
            # Verify immediate consistency
            verify_response = await async_client.get(
                "/api/v1/teachers/my-profile",
                headers=headers
            )
            verify_data = verify_response.json()
            assert verify_data["phone"] == update["phone"]
        
        # Verify core data remained consistent
        final_response = await async_client.get(
            "/api/v1/teachers/my-profile",
            headers=headers
        )
        final_data = final_response.json()
        
        # Core fields should remain unchanged
        assert final_data["id"] == initial_data["id"]
        assert final_data["employee_id"] == initial_data["employee_id"]
        assert final_data["first_name"] == initial_data["first_name"]
        assert final_data["last_name"] == initial_data["last_name"]
        
        print("✅ Data consistency maintained across operations")

    @pytest.mark.slow
    async def test_profile_workflow_performance(self, async_client: AsyncClient):
        """Test the performance of the complete profile workflow."""
        import time
        
        start_time = time.time()
        
        # Complete workflow
        login_data = {
            "email": "amit.kumar@gmail.com",
            "password": "Sunrise@001"
        }
        
        # Login
        login_response = await async_client.post(
            "/api/v1/auth/login-json",
            json=login_data
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get profile
        await async_client.get(
            "/api/v1/teachers/my-profile",
            headers=headers
        )
        
        # Update profile
        update_data = {"phone": "9999999999"}
        await async_client.put(
            "/api/v1/teachers/my-profile",
            json=update_data,
            headers=headers
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Complete workflow should finish within 3 seconds
        assert total_time < 3.0
        print(f"✅ Complete workflow completed in {total_time:.2f} seconds")
