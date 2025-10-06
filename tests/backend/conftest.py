"""
Shared test configuration and fixtures for all tests.

This module contains pytest fixtures and configuration that are shared
across all test modules in the test suite.
"""
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.database import get_db
from app.models.base import Base
from main import app


# Test database URL (use a separate test database)
TEST_DATABASE_URL = settings.DATABASE_URL.replace("sunrise_school", "sunrise_school_test")


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """Override the get_db dependency for testing."""
    async def _override_get_db():
        yield db_session
    
    return _override_get_db


@pytest.fixture
def client(override_get_db) -> TestClient:
    """Create a test client with database dependency override."""
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client with database dependency override."""
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_teacher_data():
    """Sample teacher data for testing."""
    return {
        "employee_id": "EMP001",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@test.com",
        "phone": "1234567890",
        "date_of_birth": "1985-01-15",
        "joining_date": "2020-08-01",
        "position": "Teacher",
        "department": "Mathematics",
        "gender_id": 1,
        "qualification_id": 1,
        "employment_status_id": 1
    }


@pytest.fixture
def sample_student_data():
    """Sample student data for testing."""
    return {
        "admission_number": "ADM001",
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@test.com",
        "phone": "0987654321",
        "date_of_birth": "2005-03-20",
        "admission_date": "2020-04-01",
        "class_id": 1,
        "session_year_id": 1,
        "gender_id": 2,
        "roll_number": "001"
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "1234567890",
        "user_type_id": 2,  # Teacher
        "is_active": True
        # Note: is_verified field removed as it doesn't exist in User model
    }


@pytest.fixture
async def authenticated_teacher_token(async_client: AsyncClient, sample_user_data):
    """Create an authenticated teacher and return the access token."""
    # First create a user account
    user_response = await async_client.post("/api/v1/auth/register", json=sample_user_data)
    assert user_response.status_code == 201
    
    # Login to get token
    login_data = {
        "username": sample_user_data["email"],
        "password": sample_user_data["password"]
    }
    
    login_response = await async_client.post(
        "/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert login_response.status_code == 200
    
    token_data = login_response.json()
    return token_data["access_token"]


@pytest.fixture
def auth_headers(authenticated_teacher_token):
    """Create authorization headers with the authenticated token."""
    return {"Authorization": f"Bearer {authenticated_teacher_token}"}
