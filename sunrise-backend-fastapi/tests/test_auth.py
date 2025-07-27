import pytest
from httpx import AsyncClient
from app.models.user import User


@pytest.mark.asyncio
async def test_login_json_success(client: AsyncClient, test_user: User):
    """Test successful login with JSON payload"""
    response = await client.post(
        "/api/v1/auth/login-json",
        json={"email": "test@example.com", "password": "testpassword"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_oauth2_success(client: AsyncClient, test_user: User):
    """Test successful login with OAuth2 form"""
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "testpassword"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_email(client: AsyncClient):
    """Test login with invalid email"""
    response = await client.post(
        "/api/v1/auth/login-json",
        json={"email": "nonexistent@example.com", "password": "testpassword"}
    )

    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, test_user: User):
    """Test login with invalid password"""
    response = await client.post(
        "/api/v1/auth/login-json",
        json={"email": "test@example.com", "password": "wrongpassword"}
    )

    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, auth_headers: dict):
    """Test getting current user"""
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["first_name"] == "Test"


@pytest.mark.asyncio
async def test_protected_route(client: AsyncClient, auth_headers: dict):
    """Test protected route access"""
    response = await client.get("/api/v1/auth/protected", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "message" in data
    assert data["message"] == "This is a protected route"


@pytest.mark.asyncio
async def test_protected_route_unauthorized(client: AsyncClient):
    """Test protected route without authentication"""
    response = await client.get("/api/v1/auth/protected")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration"""
    user_data = {
        "first_name": "New",
        "last_name": "User",
        "mobile": "9876543210",
        "email": "newuser@example.com",
        "password": "newpassword123",
        "user_type": "user"
    }

    response = await client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["first_name"] == "New"
    assert data["last_name"] == "User"
    assert "password" not in data  # Password should not be returned


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user: User):
    """Test registration with duplicate email"""
    user_data = {
        "first_name": "Duplicate",
        "last_name": "User",
        "mobile": "9876543210",
        "email": "test@example.com",  # Same as test_user
        "password": "password123",
        "user_type": "user"
    }

    response = await client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    """Test logout endpoint"""
    response = await client.post("/api/v1/auth/logout")

    assert response.status_code == 200
    data = response.json()
    assert "Successfully logged out" in data["message"]
