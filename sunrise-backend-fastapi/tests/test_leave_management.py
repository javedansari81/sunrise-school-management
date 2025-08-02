"""
Comprehensive test suite for Leave Management System
Tests CRUD operations, API endpoints, and business logic
"""

import pytest
from datetime import date, datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.core.database import get_db
from app.models.leave import LeaveRequest, LeaveBalance, LeavePolicy
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.user import User
from app.schemas.leave import (
    LeaveRequestCreate, LeaveRequestUpdate, LeaveApproval,
    ApplicantTypeEnum
)
from app.crud.crud_leave import leave_request_crud, leave_balance_crud, leave_policy_crud


class TestLeaveRequestCRUD:
    """Test CRUD operations for leave requests"""

    @pytest.mark.asyncio
    async def test_create_student_leave_request(self, db: AsyncSession):
        """Test creating a student leave request"""
        leave_data = LeaveRequestCreate(
            applicant_id=1,
            applicant_type=ApplicantTypeEnum.STUDENT,
            leave_type_id=1,  # Sick Leave
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=3),
            total_days=3,
            reason="Student has fever and needs rest",
            parent_consent=True,
            emergency_contact_name="Parent Name",
            emergency_contact_phone="9876543210"
        )
        
        leave_request = await leave_request_crud.create(db, obj_in=leave_data)
        
        assert leave_request.applicant_id == 1
        assert leave_request.applicant_type == "student"
        assert leave_request.leave_type_id == 1
        assert leave_request.total_days == 3
        assert leave_request.leave_status_id == 1  # Pending
        assert leave_request.parent_consent is True

    @pytest.mark.asyncio
    async def test_create_teacher_leave_request(self, db: AsyncSession):
        """Test creating a teacher leave request"""
        leave_data = LeaveRequestCreate(
            applicant_id=1,
            applicant_type=ApplicantTypeEnum.TEACHER,
            leave_type_id=2,  # Casual Leave
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=7),
            total_days=3,
            reason="Personal work requiring time off",
            substitute_teacher_id=2,
            substitute_arranged=True
        )
        
        leave_request = await leave_request_crud.create(db, obj_in=leave_data)
        
        assert leave_request.applicant_id == 1
        assert leave_request.applicant_type == "teacher"
        assert leave_request.leave_type_id == 2
        assert leave_request.substitute_teacher_id == 2
        assert leave_request.substitute_arranged is True

    @pytest.mark.asyncio
    async def test_get_leave_request_with_details(self, db: AsyncSession):
        """Test retrieving leave request with all details"""
        # First create a leave request
        leave_data = LeaveRequestCreate(
            applicant_id=1,
            applicant_type=ApplicantTypeEnum.STUDENT,
            leave_type_id=1,
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=2),
            total_days=2,
            reason="Test leave request"
        )
        
        created_leave = await leave_request_crud.create(db, obj_in=leave_data)
        
        # Retrieve with details
        leave_with_details = await leave_request_crud.get_with_details(db, id=created_leave.id)
        
        assert leave_with_details is not None
        assert leave_with_details.id == created_leave.id
        assert leave_with_details.applicant_name is not None
        assert leave_with_details.leave_type_name is not None
        assert leave_with_details.leave_status_name is not None

    @pytest.mark.asyncio
    async def test_approve_leave_request(self, db: AsyncSession):
        """Test approving a leave request"""
        # Create a pending leave request
        leave_data = LeaveRequestCreate(
            applicant_id=1,
            applicant_type=ApplicantTypeEnum.STUDENT,
            leave_type_id=1,
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=2),
            total_days=2,
            reason="Test leave for approval"
        )
        
        leave_request = await leave_request_crud.create(db, obj_in=leave_data)
        
        # Approve the request
        approved_leave = await leave_request_crud.approve_request(
            db,
            leave_request=leave_request,
            reviewer_id=1,
            leave_status_id=2,  # Approved
            review_comments="Approved for valid reason"
        )
        
        assert approved_leave.leave_status_id == 2
        assert approved_leave.reviewed_by == 1
        assert approved_leave.review_comments == "Approved for valid reason"
        assert approved_leave.reviewed_at is not None

    @pytest.mark.asyncio
    async def test_get_pending_requests(self, db: AsyncSession):
        """Test retrieving pending leave requests"""
        # Create multiple leave requests with different statuses
        for i in range(3):
            leave_data = LeaveRequestCreate(
                applicant_id=1,
                applicant_type=ApplicantTypeEnum.STUDENT,
                leave_type_id=1,
                start_date=date.today() + timedelta(days=i+1),
                end_date=date.today() + timedelta(days=i+2),
                total_days=2,
                reason=f"Test leave request {i+1}"
            )
            await leave_request_crud.create(db, obj_in=leave_data)
        
        pending_requests = await leave_request_crud.get_pending_requests(db)
        
        assert len(pending_requests) >= 3
        for request in pending_requests:
            assert request.leave_status_name == "Pending"

    @pytest.mark.asyncio
    async def test_get_leave_statistics(self, db: AsyncSession):
        """Test getting leave statistics"""
        stats = await leave_request_crud.get_leave_statistics(db, year=2024)
        
        assert "total_requests" in stats
        assert "approved_requests" in stats
        assert "rejected_requests" in stats
        assert "pending_requests" in stats
        assert "approval_rate" in stats
        assert "leave_type_breakdown" in stats
        assert "applicant_type_breakdown" in stats


class TestLeaveRequestAPI:
    """Test Leave Request API endpoints"""

    def test_get_leave_requests(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/leaves/ endpoint"""
        response = client.get("/api/v1/leaves/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "leaves" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "total_pages" in data

    def test_create_student_leave_request(self, client: TestClient, auth_headers: dict):
        """Test POST /api/v1/leaves/ endpoint for student"""
        leave_data = {
            "applicant_id": 1,
            "applicant_type": "student",
            "leave_type_id": 1,
            "start_date": str(date.today() + timedelta(days=1)),
            "end_date": str(date.today() + timedelta(days=3)),
            "total_days": 3,
            "reason": "Student has fever and needs medical rest",
            "parent_consent": True,
            "emergency_contact_name": "Parent Name",
            "emergency_contact_phone": "9876543210"
        }
        
        response = client.post("/api/v1/leaves/", json=leave_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["applicant_id"] == 1
        assert data["applicant_type"] == "student"
        assert data["leave_type_id"] == 1
        assert data["total_days"] == 3

    def test_create_teacher_leave_request(self, client: TestClient, auth_headers: dict):
        """Test POST /api/v1/leaves/ endpoint for teacher"""
        leave_data = {
            "applicant_id": 1,
            "applicant_type": "teacher",
            "leave_type_id": 2,
            "start_date": str(date.today() + timedelta(days=5)),
            "end_date": str(date.today() + timedelta(days=7)),
            "total_days": 3,
            "reason": "Professional development workshop attendance",
            "substitute_teacher_id": 2,
            "substitute_arranged": True
        }
        
        response = client.post("/api/v1/leaves/", json=leave_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["applicant_id"] == 1
        assert data["applicant_type"] == "teacher"
        assert data["substitute_teacher_id"] == 2

    def test_get_leave_request_by_id(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/leaves/{leave_id} endpoint"""
        # First create a leave request
        leave_data = {
            "applicant_id": 1,
            "applicant_type": "student",
            "leave_type_id": 1,
            "start_date": str(date.today() + timedelta(days=1)),
            "end_date": str(date.today() + timedelta(days=2)),
            "total_days": 2,
            "reason": "Test leave request for retrieval"
        }
        
        create_response = client.post("/api/v1/leaves/", json=leave_data, headers=auth_headers)
        assert create_response.status_code == 200
        leave_id = create_response.json()["id"]
        
        # Retrieve the leave request
        response = client.get(f"/api/v1/leaves/{leave_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == leave_id
        assert "applicant_name" in data
        assert "leave_type_name" in data
        assert "leave_status_name" in data

    def test_update_leave_request(self, client: TestClient, auth_headers: dict):
        """Test PUT /api/v1/leaves/{leave_id} endpoint"""
        # First create a leave request
        leave_data = {
            "applicant_id": 1,
            "applicant_type": "student",
            "leave_type_id": 1,
            "start_date": str(date.today() + timedelta(days=1)),
            "end_date": str(date.today() + timedelta(days=2)),
            "total_days": 2,
            "reason": "Original reason"
        }
        
        create_response = client.post("/api/v1/leaves/", json=leave_data, headers=auth_headers)
        leave_id = create_response.json()["id"]
        
        # Update the leave request
        update_data = {
            "reason": "Updated reason for leave",
            "total_days": 3,
            "end_date": str(date.today() + timedelta(days=3))
        }
        
        response = client.put(f"/api/v1/leaves/{leave_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["reason"] == "Updated reason for leave"

    def test_approve_leave_request(self, client: TestClient, auth_headers: dict):
        """Test PATCH /api/v1/leaves/{leave_id}/approve endpoint"""
        # First create a leave request
        leave_data = {
            "applicant_id": 1,
            "applicant_type": "student",
            "leave_type_id": 1,
            "start_date": str(date.today() + timedelta(days=1)),
            "end_date": str(date.today() + timedelta(days=2)),
            "total_days": 2,
            "reason": "Leave request for approval test"
        }
        
        create_response = client.post("/api/v1/leaves/", json=leave_data, headers=auth_headers)
        leave_id = create_response.json()["id"]
        
        # Approve the leave request
        approval_data = {
            "leave_status_id": 2,  # Approved
            "review_comments": "Approved for valid medical reason"
        }
        
        response = client.patch(f"/api/v1/leaves/{leave_id}/approve", json=approval_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["leave_status_id"] == 2
        assert data["review_comments"] == "Approved for valid medical reason"

    def test_get_pending_requests(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/leaves/pending endpoint"""
        response = client.get("/api/v1/leaves/pending", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_leave_statistics(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/leaves/statistics endpoint"""
        response = client.get("/api/v1/leaves/statistics?year=2024", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total_requests" in data
        assert "approved_requests" in data
        assert "approval_rate" in data
        assert "leave_type_breakdown" in data

    def test_delete_leave_request(self, client: TestClient, auth_headers: dict):
        """Test DELETE /api/v1/leaves/{leave_id} endpoint"""
        # First create a leave request
        leave_data = {
            "applicant_id": 1,
            "applicant_type": "student",
            "leave_type_id": 1,
            "start_date": str(date.today() + timedelta(days=1)),
            "end_date": str(date.today() + timedelta(days=2)),
            "total_days": 2,
            "reason": "Leave request for deletion test"
        }
        
        create_response = client.post("/api/v1/leaves/", json=leave_data, headers=auth_headers)
        leave_id = create_response.json()["id"]
        
        # Delete the leave request
        response = client.delete(f"/api/v1/leaves/{leave_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "deleted successfully" in data["message"]


class TestLeaveValidation:
    """Test leave request validation logic"""

    def test_invalid_date_range(self, client: TestClient, auth_headers: dict):
        """Test validation for invalid date range"""
        leave_data = {
            "applicant_id": 1,
            "applicant_type": "student",
            "leave_type_id": 1,
            "start_date": str(date.today() + timedelta(days=5)),
            "end_date": str(date.today() + timedelta(days=2)),  # End before start
            "total_days": 2,
            "reason": "Test invalid date range"
        }
        
        response = client.post("/api/v1/leaves/", json=leave_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "Start date cannot be after end date" in response.json()["detail"]

    def test_nonexistent_applicant(self, client: TestClient, auth_headers: dict):
        """Test validation for nonexistent applicant"""
        leave_data = {
            "applicant_id": 99999,  # Nonexistent ID
            "applicant_type": "student",
            "leave_type_id": 1,
            "start_date": str(date.today() + timedelta(days=1)),
            "end_date": str(date.today() + timedelta(days=2)),
            "total_days": 2,
            "reason": "Test nonexistent applicant"
        }
        
        response = client.post("/api/v1/leaves/", json=leave_data, headers=auth_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
