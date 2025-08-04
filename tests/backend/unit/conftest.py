import asyncio
import os
import sys
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add the parent directory (sunrise-backend-fastapi) to the path so we can import from app
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # api-tests
grandparent_dir = os.path.dirname(parent_dir)  # sunrise-backend-fastapi
sys.path.insert(0, grandparent_dir)

from app.core.database import Base, get_db
from app.core.config import settings
from app.main import app
from app.models.user import User
from app.models.student import Student
from app.models.fee import FeeRecord, FeeStructure
from app.core.security import get_password_hash
from decimal import Decimal
from datetime import date

# Test database URL (use in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session factory
TestSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest_asyncio.fixture
async def db_session():
    """Create a test database session"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    """Create a test client"""
    def override_get_db():
        return db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user"""
    user = User(
        first_name="Test",
        last_name="User",
        mobile="1234567890",
        email="test@example.com",
        password=get_password_hash("testpassword"),
        user_type="user",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession):
    """Create a test admin user"""
    user = User(
        first_name="Admin",
        last_name="User",
        mobile="0987654321",
        email="admin@example.com",
        password=get_password_hash("adminpassword"),
        user_type="admin",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, test_user: User):
    """Get authentication headers for test user"""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(client: AsyncClient, admin_user: User):
    """Get authentication headers for admin user"""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "adminpassword"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_student(db_session: AsyncSession):
    """Create a test student"""
    student = Student(
        admission_number="TEST001",
        first_name="Test",
        last_name="Student",
        date_of_birth=date(2010, 1, 1),
        gender_id=1,  # Assuming gender ID 1 exists
        class_id=1,   # Assuming class ID 1 exists
        session_year_id=4,  # 2025-26
        section="A",
        roll_number="001",
        phone="1234567890",
        email="student@test.com"
    )
    db_session.add(student)
    await db_session.commit()
    await db_session.refresh(student)
    return student


@pytest_asyncio.fixture
async def test_fee_structure(db_session: AsyncSession):
    """Create a test fee structure"""
    fee_structure = FeeStructure(
        class_id=1,
        session_year_id=4,  # 2025-26
        tuition_fee=Decimal('5000.00'),
        admission_fee=Decimal('1000.00'),
        development_fee=Decimal('500.00'),
        total_annual_fee=Decimal('6500.00')
    )
    db_session.add(fee_structure)
    await db_session.commit()
    await db_session.refresh(fee_structure)
    return fee_structure


@pytest_asyncio.fixture
async def test_fee_record(db_session: AsyncSession, test_student: Student):
    """Create a test fee record"""
    fee_record = FeeRecord(
        student_id=test_student.id,
        session_year_id=4,  # 2025-26
        payment_type_id=1,  # Monthly
        total_amount=Decimal('1000.00'),
        paid_amount=Decimal('0.00'),
        balance_amount=Decimal('1000.00'),
        payment_status_id=1,  # Pending
        due_date=date.today()
    )
    db_session.add(fee_record)
    await db_session.commit()
    await db_session.refresh(fee_record)
    return fee_record


@pytest_asyncio.fixture
async def admin_token(client, admin_user: User):
    """Get admin authentication token"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "adminpassword"}
    )
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def student_token(client, test_user: User):
    """Get student authentication token"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword"}
    )
    return response.json()["access_token"]
