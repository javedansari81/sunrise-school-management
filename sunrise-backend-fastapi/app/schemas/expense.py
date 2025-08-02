from typing import Optional, List, Union
from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from decimal import Decimal


class ExpenseBase(BaseModel):
    """Base schema for expense records using metadata-driven architecture"""
    expense_date: date = Field(..., description="Date of the expense")
    expense_category_id: int = Field(..., description="Expense category ID from metadata")
    subcategory: Optional[str] = Field(None, max_length=100, description="Subcategory within the main category")
    description: str = Field(..., min_length=5, max_length=1000, description="Detailed description of the expense")

    # Financial Details
    amount: Decimal = Field(..., gt=0, description="Base amount before tax")
    tax_amount: Decimal = Field(0.0, ge=0, description="Tax amount")
    total_amount: Decimal = Field(..., gt=0, description="Total amount including tax")
    currency: str = Field("INR", max_length=3, description="Currency code")

    # Vendor Information
    vendor_name: Optional[str] = Field(None, max_length=200, description="Vendor/supplier name")
    vendor_contact: Optional[str] = Field(None, max_length=20, description="Vendor contact number")
    vendor_email: Optional[str] = Field(None, max_length=255, description="Vendor email address")
    vendor_address: Optional[str] = Field(None, description="Vendor address")
    vendor_gst_number: Optional[str] = Field(None, max_length=20, description="Vendor GST number")

    # Payment Details
    payment_method_id: int = Field(..., description="Payment method ID from metadata")
    payment_reference: Optional[str] = Field(None, max_length=100, description="Payment reference/transaction ID")

    # Bank/Cheque Details
    bank_name: Optional[str] = Field(None, max_length=100, description="Bank name for cheque/transfer")
    cheque_number: Optional[str] = Field(None, max_length=50, description="Cheque number")
    cheque_date: Optional[date] = Field(None, description="Cheque date")

    # Budget Information
    budget_category: Optional[str] = Field(None, max_length=100, description="Budget category")
    session_year_id: Optional[int] = Field(None, description="Session year ID from metadata")
    is_budgeted: bool = Field(False, description="Whether this expense is budgeted")

    # Documents
    invoice_url: Optional[str] = Field(None, max_length=500, description="Invoice document URL")
    receipt_url: Optional[str] = Field(None, max_length=500, description="Receipt document URL")
    supporting_documents: Optional[List[str]] = Field(None, description="List of supporting document URLs")

    # Additional Information
    is_recurring: bool = Field(False, description="Whether this is a recurring expense")
    recurring_frequency: Optional[str] = Field(None, description="Frequency for recurring expenses")
    next_due_date: Optional[date] = Field(None, description="Next due date for recurring expenses")

    # Priority and Urgency
    priority: str = Field("Medium", description="Priority level")
    is_emergency: bool = Field(False, description="Whether this is an emergency expense")

    @validator('total_amount')
    def validate_total_amount(cls, v, values):
        if 'amount' in values and 'tax_amount' in values:
            expected_total = values['amount'] + values['tax_amount']
            if abs(v - expected_total) > 0.01:  # Allow for small rounding differences
                raise ValueError('Total amount must equal amount plus tax amount')
        return v

    @validator('priority')
    def validate_priority(cls, v):
        if v not in ['Low', 'Medium', 'High', 'Urgent']:
            raise ValueError('Priority must be one of: Low, Medium, High, Urgent')
        return v

    @validator('recurring_frequency')
    def validate_recurring_frequency(cls, v, values):
        if values.get('is_recurring') and not v:
            raise ValueError('Recurring frequency is required for recurring expenses')
        if v and v not in ['Monthly', 'Quarterly', 'Half Yearly', 'Yearly']:
            raise ValueError('Recurring frequency must be one of: Monthly, Quarterly, Half Yearly, Yearly')
        return v

    @validator('cheque_date')
    def validate_cheque_date(cls, v, values):
        if v and 'expense_date' in values and v < values['expense_date']:
            raise ValueError('Cheque date cannot be before expense date')
        return v


class ExpenseCreate(ExpenseBase):
    """Schema for creating new expense records"""
    pass


class ExpenseUpdate(BaseModel):
    """Schema for updating expense records"""
    expense_date: Optional[date] = None
    expense_category_id: Optional[int] = None
    subcategory: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    currency: Optional[str] = None
    vendor_name: Optional[str] = None
    vendor_contact: Optional[str] = None
    vendor_email: Optional[str] = None
    vendor_address: Optional[str] = None
    vendor_gst_number: Optional[str] = None
    payment_method_id: Optional[int] = None
    payment_reference: Optional[str] = None
    bank_name: Optional[str] = None
    cheque_number: Optional[str] = None
    cheque_date: Optional[date] = None
    budget_category: Optional[str] = None
    session_year_id: Optional[int] = None
    is_budgeted: Optional[bool] = None
    invoice_url: Optional[str] = None
    receipt_url: Optional[str] = None
    supporting_documents: Optional[List[str]] = None
    is_recurring: Optional[bool] = None
    recurring_frequency: Optional[str] = None
    next_due_date: Optional[date] = None
    priority: Optional[str] = None
    is_emergency: Optional[bool] = None


class ExpenseInDBBase(ExpenseBase):
    """Base schema for expense records in database"""
    id: int
    expense_status_id: int = Field(..., description="Expense status ID from metadata")
    payment_status_id: int = Field(..., description="Payment status ID from metadata")
    payment_date: Optional[date] = None
    requested_by: int = Field(..., description="User ID who requested the expense")
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    approval_comments: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Expense(ExpenseInDBBase):
    """Complete expense schema"""
    pass


class ExpenseWithDetails(Expense):
    """Expense with additional details from related tables"""
    expense_category_name: str
    expense_status_name: str
    expense_status_color: Optional[str] = None
    payment_method_name: str
    payment_status_name: str
    payment_status_color: Optional[str] = None
    session_year_name: Optional[str] = None
    requester_name: str
    approver_name: Optional[str] = None


class ExpenseApproval(BaseModel):
    """Schema for expense approval/rejection"""
    expense_status_id: int = Field(..., description="New status ID from metadata")
    approval_comments: Optional[str] = Field(None, description="Comments from approver")


class ExpenseFilters(BaseModel):
    """Filters for expense queries"""
    expense_category_id: Optional[int] = None
    expense_status_id: Optional[int] = None
    payment_status_id: Optional[int] = None
    payment_method_id: Optional[int] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    vendor_name: Optional[str] = None
    requested_by: Optional[int] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    session_year_id: Optional[int] = None
    priority: Optional[str] = None
    is_emergency: Optional[bool] = None
    is_recurring: Optional[bool] = None


class ExpenseListResponse(BaseModel):
    """Response schema for expense list"""
    expenses: List[ExpenseWithDetails]
    total: int
    page: int
    per_page: int
    total_pages: int
    summary: dict


class ExpenseReport(BaseModel):
    """Expense report schema"""
    period: str
    total_expenses: Decimal
    total_approved: Decimal
    total_pending: Decimal
    total_rejected: Decimal
    category_breakdown: List[dict]
    monthly_trend: List[dict]
    vendor_breakdown: List[dict]
    payment_method_breakdown: List[dict]


class ExpenseDashboard(BaseModel):
    """Expense dashboard schema"""
    total_expenses: Decimal
    pending_approvals: int
    monthly_budget_utilization: float
    top_categories: List[dict]
    recent_expenses: List[ExpenseWithDetails]
    monthly_trend: List[dict]
    urgent_expenses: List[ExpenseWithDetails]


# Vendor Schemas
class VendorBase(BaseModel):
    """Base schema for vendor records"""
    vendor_name: str = Field(..., min_length=2, max_length=200, description="Vendor/supplier name")
    vendor_code: Optional[str] = Field(None, max_length=50, description="Unique vendor code")
    contact_person: Optional[str] = Field(None, max_length=200, description="Primary contact person")

    # Contact Information
    phone: Optional[str] = Field(None, max_length=20, description="Contact phone number")
    email: Optional[str] = Field(None, max_length=255, description="Contact email address")
    website: Optional[str] = Field(None, max_length=255, description="Company website")

    # Address
    address: Optional[str] = Field(None, description="Complete address")
    city: Optional[str] = Field(None, max_length=100, description="City")
    state: Optional[str] = Field(None, max_length=100, description="State/Province")
    postal_code: Optional[str] = Field(None, max_length=20, description="Postal/ZIP code")
    country: str = Field(default="India", max_length=100, description="Country")

    # Business Information
    gst_number: Optional[str] = Field(None, max_length=20, description="GST registration number")
    pan_number: Optional[str] = Field(None, max_length=20, description="PAN number")
    business_type: Optional[str] = Field(None, max_length=50, description="Type of business")

    # Banking Details
    bank_name: Optional[str] = Field(None, max_length=100, description="Bank name")
    account_number: Optional[str] = Field(None, max_length=50, description="Bank account number")
    ifsc_code: Optional[str] = Field(None, max_length=20, description="IFSC code")
    account_holder_name: Optional[str] = Field(None, max_length=200, description="Account holder name")

    # Status and Categories
    is_active: bool = Field(default=True, description="Whether vendor is active")
    vendor_categories: Optional[List[int]] = Field(None, description="Array of category IDs")

    # Credit Terms
    credit_limit: Optional[Decimal] = Field(None, ge=0, description="Credit limit amount")
    credit_days: int = Field(default=30, ge=0, le=365, description="Credit payment days")


class VendorCreate(VendorBase):
    """Schema for creating vendor records"""
    pass


class VendorUpdate(BaseModel):
    """Schema for updating vendor records"""
    vendor_name: Optional[str] = Field(None, min_length=2, max_length=200)
    vendor_code: Optional[str] = Field(None, max_length=50)
    contact_person: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    gst_number: Optional[str] = Field(None, max_length=20)
    pan_number: Optional[str] = Field(None, max_length=20)
    business_type: Optional[str] = Field(None, max_length=50)
    bank_name: Optional[str] = Field(None, max_length=100)
    account_number: Optional[str] = Field(None, max_length=50)
    ifsc_code: Optional[str] = Field(None, max_length=20)
    account_holder_name: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None
    vendor_categories: Optional[List[int]] = None
    credit_limit: Optional[Decimal] = Field(None, ge=0)
    credit_days: Optional[int] = Field(None, ge=0, le=365)


class VendorInDBBase(VendorBase):
    """Base schema for vendor records in database"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Vendor(VendorInDBBase):
    """Complete vendor schema"""
    pass
