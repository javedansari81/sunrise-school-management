"""
Comprehensive tests for the expense management system
Tests CRUD operations, approval workflows, and metadata integration
"""

import pytest
from decimal import Decimal
from datetime import date, datetime
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.expense import Expense, Vendor
from app.models.user import User
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseApproval
from app.crud.crud_expense import expense_crud, vendor_crud


client = TestClient(app)


class TestExpenseManagement:
    """Test suite for expense management functionality"""

    @pytest.fixture
    def sample_expense_data(self):
        """Sample expense data for testing"""
        return {
            "expense_date": "2024-01-15",
            "expense_category_id": 1,  # Infrastructure
            "subcategory": "Office Equipment",
            "description": "Purchase of office chairs and desks for new employees",
            "amount": 25000.00,
            "tax_amount": 4500.00,
            "total_amount": 29500.00,
            "currency": "INR",
            "vendor_name": "Office Furniture Ltd",
            "vendor_contact": "9876543210",
            "vendor_email": "sales@officefurniture.com",
            "vendor_gst_number": "27ABCDE1234F1Z5",
            "payment_method_id": 3,  # Bank Transfer
            "payment_reference": "TXN20240115001",
            "budget_category": "Office Setup",
            "session_year_id": 4,
            "is_budgeted": True,
            "invoice_url": "https://example.com/invoices/INV001.pdf",
            "receipt_url": "https://example.com/receipts/REC001.pdf",
            "priority": "Medium",
            "is_emergency": False,
            "is_recurring": False
        }

    @pytest.fixture
    def sample_vendor_data(self):
        """Sample vendor data for testing"""
        return {
            "vendor_name": "Test Vendor Ltd",
            "vendor_code": "TV001",
            "contact_person": "John Doe",
            "phone": "9876543210",
            "email": "contact@testvendor.com",
            "address_line1": "123 Business Street",
            "city": "Mumbai",
            "state": "Maharashtra",
            "postal_code": "400001",
            "country": "India",
            "gst_number": "27TESTV1234G1H2",
            "pan_number": "TESTV1234P",
            "business_type": "Private Limited",
            "is_active": True,
            "credit_limit": 100000.00,
            "credit_days": 30
        }

    def test_create_expense_success(self, db_session: AsyncSession, sample_expense_data, auth_headers):
        """Test successful expense creation"""
        response = client.post(
            "/api/v1/expenses/",
            json=sample_expense_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == sample_expense_data["description"]
        assert float(data["total_amount"]) == sample_expense_data["total_amount"]
        assert data["expense_status_id"] == 1  # Pending status
        assert data["requested_by"] is not None

    def test_create_expense_invalid_total(self, sample_expense_data, auth_headers):
        """Test expense creation with invalid total amount"""
        sample_expense_data["total_amount"] = 20000.00  # Incorrect total
        
        response = client.post(
            "/api/v1/expenses/",
            json=sample_expense_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "Total amount must equal amount plus tax amount" in response.json()["detail"]

    def test_get_expenses_with_filters(self, auth_headers):
        """Test getting expenses with various filters"""
        # Test with category filter
        response = client.get(
            "/api/v1/expenses/?expense_category_id=1&page=1&per_page=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "expenses" in data
        assert "total" in data
        assert "page" in data
        assert "total_pages" in data

    def test_get_expense_by_id(self, auth_headers):
        """Test getting a specific expense by ID"""
        # First create an expense
        sample_data = {
            "expense_date": "2024-01-20",
            "expense_category_id": 2,
            "description": "Test expense for retrieval",
            "amount": 5000.00,
            "tax_amount": 900.00,
            "total_amount": 5900.00,
            "payment_method_id": 1
        }
        
        create_response = client.post(
            "/api/v1/expenses/",
            json=sample_data,
            headers=auth_headers
        )
        expense_id = create_response.json()["id"]
        
        # Get the expense
        response = client.get(
            f"/api/v1/expenses/{expense_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == expense_id
        assert data["description"] == sample_data["description"]

    def test_update_expense_success(self, auth_headers):
        """Test successful expense update"""
        # Create an expense first
        create_data = {
            "expense_date": "2024-01-25",
            "expense_category_id": 1,
            "description": "Original description",
            "amount": 10000.00,
            "tax_amount": 1800.00,
            "total_amount": 11800.00,
            "payment_method_id": 2
        }
        
        create_response = client.post(
            "/api/v1/expenses/",
            json=create_data,
            headers=auth_headers
        )
        expense_id = create_response.json()["id"]
        
        # Update the expense
        update_data = {
            "description": "Updated description",
            "amount": 12000.00,
            "tax_amount": 2160.00,
            "total_amount": 14160.00
        }
        
        response = client.put(
            f"/api/v1/expenses/{expense_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == update_data["description"]
        assert float(data["total_amount"]) == update_data["total_amount"]

    def test_update_non_pending_expense_fails(self, auth_headers):
        """Test that updating non-pending expense fails"""
        # This would require setting up an approved expense
        # For now, we'll test the endpoint exists
        response = client.put(
            "/api/v1/expenses/999",
            json={"description": "Should fail"},
            headers=auth_headers
        )
        
        assert response.status_code == 404  # Expense not found

    def test_delete_expense_success(self, auth_headers):
        """Test successful expense deletion"""
        # Create an expense first
        create_data = {
            "expense_date": "2024-01-30",
            "expense_category_id": 3,
            "description": "Expense to be deleted",
            "amount": 3000.00,
            "tax_amount": 540.00,
            "total_amount": 3540.00,
            "payment_method_id": 1
        }
        
        create_response = client.post(
            "/api/v1/expenses/",
            json=create_data,
            headers=auth_headers
        )
        expense_id = create_response.json()["id"]
        
        # Delete the expense
        response = client.delete(
            f"/api/v1/expenses/{expense_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

    def test_approve_expense_success(self, auth_headers):
        """Test successful expense approval"""
        # Create an expense first
        create_data = {
            "expense_date": "2024-02-01",
            "expense_category_id": 1,
            "description": "Expense for approval test",
            "amount": 8000.00,
            "tax_amount": 1440.00,
            "total_amount": 9440.00,
            "payment_method_id": 3
        }
        
        create_response = client.post(
            "/api/v1/expenses/",
            json=create_data,
            headers=auth_headers
        )
        expense_id = create_response.json()["id"]
        
        # Approve the expense
        approval_data = {
            "expense_status_id": 2,  # Approved
            "approval_comments": "Approved for necessary office equipment"
        }
        
        response = client.patch(
            f"/api/v1/expenses/{expense_id}/approve",
            json=approval_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["expense_status_id"] == 2
        assert data["approved_by"] is not None
        assert data["approved_at"] is not None

    def test_reject_expense_success(self, auth_headers):
        """Test successful expense rejection"""
        # Create an expense first
        create_data = {
            "expense_date": "2024-02-05",
            "expense_category_id": 2,
            "description": "Expense for rejection test",
            "amount": 15000.00,
            "tax_amount": 2700.00,
            "total_amount": 17700.00,
            "payment_method_id": 2
        }
        
        create_response = client.post(
            "/api/v1/expenses/",
            json=create_data,
            headers=auth_headers
        )
        expense_id = create_response.json()["id"]
        
        # Reject the expense
        rejection_data = {
            "expense_status_id": 3,  # Rejected
            "approval_comments": "Budget exceeded for this category"
        }
        
        response = client.patch(
            f"/api/v1/expenses/{expense_id}/approve",
            json=rejection_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["expense_status_id"] == 3

    def test_get_expense_statistics(self, auth_headers):
        """Test getting expense statistics"""
        response = client.get(
            "/api/v1/expenses/statistics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_expenses" in data
        assert "approved_expenses" in data
        assert "pending_expenses" in data
        assert "rejected_expenses" in data
        assert "category_breakdown" in data

    def test_get_pending_expenses(self, auth_headers):
        """Test getting pending expenses"""
        response = client.get(
            "/api/v1/expenses/pending",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "pending_expenses" in data

    def test_get_my_expenses(self, auth_headers):
        """Test getting current user's expenses"""
        response = client.get(
            "/api/v1/expenses/my-expenses?limit=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "my_expenses" in data
        assert "total" in data

    def test_expense_dashboard(self, auth_headers):
        """Test expense dashboard endpoint"""
        response = client.get(
            "/api/v1/expenses/dashboard",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_expenses" in data
        assert "pending_approvals" in data

    def test_create_vendor_success(self, sample_vendor_data, auth_headers):
        """Test successful vendor creation"""
        response = client.post(
            "/api/v1/expenses/vendors/",
            json=sample_vendor_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["vendor_name"] == sample_vendor_data["vendor_name"]
        assert data["is_active"] == True

    def test_get_active_vendors(self, auth_headers):
        """Test getting active vendors"""
        response = client.get(
            "/api/v1/expenses/vendors/active",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_unauthorized_access(self):
        """Test that endpoints require authentication"""
        response = client.get("/api/v1/expenses/")
        assert response.status_code == 401

    def test_expense_validation_errors(self, auth_headers):
        """Test various validation errors"""
        # Missing required fields
        invalid_data = {
            "description": "Missing required fields"
        }
        
        response = client.post(
            "/api/v1/expenses/",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error

    def test_expense_filtering_edge_cases(self, auth_headers):
        """Test edge cases in expense filtering"""
        # Test with invalid date range
        response = client.get(
            "/api/v1/expenses/?from_date=2024-12-31&to_date=2024-01-01",
            headers=auth_headers
        )
        
        assert response.status_code == 200  # Should handle gracefully
        
        # Test with very large page number
        response = client.get(
            "/api/v1/expenses/?page=9999",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["expenses"]) == 0  # No results for large page


@pytest.fixture
def auth_headers():
    """Mock authentication headers for testing"""
    # This would normally involve creating a test user and getting a token
    # For now, we'll mock it
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def db_session():
    """Mock database session for testing"""
    # This would normally create a test database session
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
