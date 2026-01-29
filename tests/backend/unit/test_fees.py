"""
Test cases for fee management functionality
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.core.database import get_db
from app.models.fee import FeeStructure, FeeRecord, FeePayment
from app.models.student import Student
from app.models.user import User
from app.schemas.fee import (
    FeeStructureCreate, FeeRecordCreate, FeePaymentCreate,
    SessionYearEnum, PaymentStatusEnum, PaymentTypeEnum, PaymentMethodEnum
)
from app.crud import fee_structure_crud, fee_record_crud, fee_payment_crud, student_crud


class TestFeeStructure:
    """Test fee structure operations"""

    @pytest.mark.asyncio
    async def test_create_fee_structure(self, db_session: AsyncSession, admin_user: User):
        """Test creating a fee structure"""
        fee_structure_data = FeeStructureCreate(
            class_id=1,  # Assuming class ID 1 exists
            session_year_id=4,  # 2025-26
            tuition_fee=Decimal('5000.00'),
            admission_fee=Decimal('1000.00'),
            development_fee=Decimal('500.00'),
            total_annual_fee=Decimal('6500.00')
        )
        
        fee_structure = await fee_structure_crud.create(db_session, obj_in=fee_structure_data)
        
        assert fee_structure.id is not None
        assert fee_structure.class_id == 1
        assert fee_structure.session_year_id == 4
        assert fee_structure.total_annual_fee == Decimal('6500.00')

    @pytest.mark.asyncio
    async def test_get_fee_structure_by_class_and_session(self, db_session: AsyncSession):
        """Test getting fee structure by class and session"""
        # First create a fee structure
        fee_structure_data = FeeStructureCreate(
            class_id=1,
            session_year_id=4,
            tuition_fee=Decimal('5000.00'),
            total_annual_fee=Decimal('5000.00')
        )
        created_structure = await fee_structure_crud.create(db_session, obj_in=fee_structure_data)
        
        # Now retrieve it
        retrieved_structure = await fee_structure_crud.get_by_class_and_session(
            db_session, class_name="Class 1", session_year="2025-26"
        )
        
        assert retrieved_structure is not None
        assert retrieved_structure.id == created_structure.id


class TestFeeRecord:
    """Test fee record operations"""

    @pytest.mark.asyncio
    async def test_create_fee_record(self, db_session: AsyncSession, test_student: Student):
        """Test creating a fee record"""
        fee_record_data = FeeRecordCreate(
            student_id=test_student.id,
            session_year_id=4,  # 2025-26
            payment_type_id=1,  # Monthly
            total_amount=Decimal('1000.00'),
            balance_amount=Decimal('1000.00'),
            due_date=date.today(),
            payment_status_id=1  # Pending
        )
        
        fee_record = await fee_record_crud.create(db_session, obj_in=fee_record_data)
        
        assert fee_record.id is not None
        assert fee_record.student_id == test_student.id
        assert fee_record.total_amount == Decimal('1000.00')
        assert fee_record.balance_amount == Decimal('1000.00')

    @pytest.mark.asyncio
    async def test_get_fee_record_by_student_session_type(self, db_session: AsyncSession, test_student: Student):
        """Test getting fee record by student, session, and payment type"""
        # Create a fee record
        fee_record_data = FeeRecordCreate(
            student_id=test_student.id,
            session_year_id=4,
            payment_type_id=1,
            total_amount=Decimal('1000.00'),
            balance_amount=Decimal('1000.00'),
            due_date=date.today(),
            payment_status_id=1
        )
        created_record = await fee_record_crud.create(db_session, obj_in=fee_record_data)
        
        # Retrieve it
        retrieved_record = await fee_record_crud.get_by_student_session_type(
            db_session,
            student_id=test_student.id,
            session_year_id=4,
            payment_type_id=1
        )
        
        assert retrieved_record is not None
        assert retrieved_record.id == created_record.id

    @pytest.mark.asyncio
    async def test_get_fee_records_by_student(self, db_session: AsyncSession, test_student: Student):
        """Test getting all fee records for a student"""
        # Create multiple fee records
        for payment_type_id in [1, 2, 3]:  # Monthly, Quarterly, Half Yearly
            fee_record_data = FeeRecordCreate(
                student_id=test_student.id,
                session_year_id=4,
                payment_type_id=payment_type_id,
                total_amount=Decimal('1000.00'),
                balance_amount=Decimal('1000.00'),
                due_date=date.today(),
                payment_status_id=1
            )
            await fee_record_crud.create(db_session, obj_in=fee_record_data)
        
        # Retrieve all records
        records = await fee_record_crud.get_by_student(
            db_session, student_id=test_student.id, session_year="2025-26"
        )
        
        assert len(records) == 3


class TestFeePayment:
    """Test fee payment operations"""

    @pytest.mark.asyncio
    async def test_create_fee_payment(self, db_session: AsyncSession, test_fee_record: FeeRecord):
        """Test creating a fee payment"""
        payment_data = FeePaymentCreate(
            fee_record_id=test_fee_record.id,
            amount=Decimal('500.00'),
            payment_method_id=1,  # Cash
            payment_date=date.today(),
            transaction_id="TXN123456",
            remarks="Test payment"
        )
        
        payment = await fee_payment_crud.create_payment(
            db_session, obj_in=payment_data, fee_record=test_fee_record
        )
        
        assert payment.id is not None
        assert payment.amount == Decimal('500.00')
        assert payment.transaction_id == "TXN123456"
        
        # Check that fee record was updated
        await db_session.refresh(test_fee_record)
        assert test_fee_record.paid_amount == Decimal('500.00')
        assert test_fee_record.balance_amount == Decimal('500.00')  # Assuming original total was 1000
        assert test_fee_record.payment_status_id == 2  # Partial

    @pytest.mark.asyncio
    async def test_full_payment(self, db_session: AsyncSession, test_fee_record: FeeRecord):
        """Test making a full payment"""
        payment_data = FeePaymentCreate(
            fee_record_id=test_fee_record.id,
            amount=test_fee_record.balance_amount,
            payment_method_id=1,
            payment_date=date.today(),
            transaction_id="TXN789012"
        )
        
        payment = await fee_payment_crud.create_payment(
            db_session, obj_in=payment_data, fee_record=test_fee_record
        )
        
        # Check that fee record status is updated to paid
        await db_session.refresh(test_fee_record)
        assert test_fee_record.balance_amount == Decimal('0.00')
        assert test_fee_record.payment_status_id == 3  # Paid

    @pytest.mark.asyncio
    async def test_get_payments_by_fee_record(self, db_session: AsyncSession, test_fee_record: FeeRecord):
        """Test getting all payments for a fee record"""
        # Create multiple payments
        for i in range(3):
            payment_data = FeePaymentCreate(
                fee_record_id=test_fee_record.id,
                amount=Decimal('100.00'),
                payment_method_id=1,
                payment_date=date.today(),
                transaction_id=f"TXN{i:06d}"
            )
            await fee_payment_crud.create_payment(
                db_session, obj_in=payment_data, fee_record=test_fee_record
            )
        
        # Retrieve all payments
        payments = await fee_payment_crud.get_by_fee_record(
            db_session, fee_record_id=test_fee_record.id
        )
        
        assert len(payments) == 3


class TestFeeAPI:
    """Test fee management API endpoints"""

    def test_get_fees_endpoint(self, client: TestClient, admin_token: str):
        """Test the main fees listing endpoint"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v1/fees/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "fees" in data
        assert "total" in data
        assert "summary" in data

    def test_create_fee_record_endpoint(self, client: TestClient, admin_token: str, test_student: Student):
        """Test creating a fee record via API"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        fee_data = {
            "student_id": test_student.id,
            "session_year_id": 4,
            "payment_type_id": 1,
            "total_amount": 1000.00,
            "balance_amount": 1000.00,
            "due_date": str(date.today()),
            "payment_status_id": 1
        }
        
        response = client.post("/api/v1/fees/", json=fee_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == test_student.id
        assert data["total_amount"] == 1000.00

    def test_get_student_fee_options(self, client: TestClient, student_token: str, test_student: Student):
        """Test getting fee options for a student"""
        headers = {"Authorization": f"Bearer {student_token}"}
        
        response = client.get(
            f"/api/v1/fees/student-options/{test_student.id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "payment_options" in data
        assert len(data["payment_options"]) == 4  # Monthly, Quarterly, Half Yearly, Yearly

    def test_get_payment_history(self, client: TestClient, student_token: str, test_student: Student):
        """Test getting payment history for a student"""
        headers = {"Authorization": f"Bearer {student_token}"}
        
        response = client.get(
            f"/api/v1/fees/payments/history/{test_student.id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "payment_history" in data
        assert "summary" in data

    def test_fee_analytics_endpoint(self, client: TestClient, admin_token: str):
        """Test fee analytics endpoint"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = client.get("/api/v1/fees/analytics", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "overall_summary" in data
        assert "session_year" in data
        assert data["session_year"] == "2025-26"
