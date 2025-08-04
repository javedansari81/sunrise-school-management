import pytest
from httpx import AsyncClient
from app.models.user import User


@pytest.mark.asyncio
async def test_get_users(client: AsyncClient, auth_headers: dict, test_user: User):
    """Test getting all users"""
    response = await client.get("/api/v1/users/", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient, auth_headers: dict):
    """Test creating a new user"""
    user_data = {
        "first_name": "New",
        "last_name": "User",
        "mobile": "5555555555",
        "email": "newuser@example.com",
        "password": "newpassword",
        "user_type": "user"
    }
    
    response = await client.post("/api/v1/users/", json=user_data, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["first_name"] == "New"
    assert "password" not in data  # Password should not be returned


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client: AsyncClient, auth_headers: dict, test_user: User):
    """Test creating a user with duplicate email"""
    user_data = {
        "first_name": "Duplicate",
        "last_name": "User",
        "mobile": "5555555555",
        "email": "test@example.com",  # Same as test_user
        "password": "newpassword",
        "user_type": "user"
    }
    
    response = await client.post("/api/v1/users/", json=user_data, headers=auth_headers)
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_user_by_id(client: AsyncClient, auth_headers: dict, test_user: User):
    """Test getting a user by ID"""
    response = await client.get(f"/api/v1/users/{test_user.id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email


@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient, auth_headers: dict):
    """Test getting a non-existent user"""
    response = await client.get("/api/v1/users/999", headers=auth_headers)
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_user(client: AsyncClient, auth_headers: dict, test_user: User):
    """Test updating a user"""
    update_data = {
        "first_name": "Updated",
        "last_name": "Name"
    }
    
    response = await client.put(
        f"/api/v1/users/{test_user.id}", 
        json=update_data, 
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "Name"


@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient, auth_headers: dict, test_user: User):
    """Test deleting a user (soft delete)"""
    response = await client.delete(f"/api/v1/users/{test_user.id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] == False


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test accessing users endpoint without authentication"""
    response = await client.get("/api/v1/users/")
    
    assert response.status_code == 401
