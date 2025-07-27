from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, date
from enum import Enum


class ExpenseCategoryEnum(str, Enum):
    OFFICE_SUPPLIES = "Office Supplies"
    MAINTENANCE = "Maintenance"
    UTILITIES = "Utilities"
    TRANSPORT = "Transport"
    FOOD_CATERING = "Food & Catering"
    EQUIPMENT = "Equipment"
    MARKETING = "Marketing"
    STAFF_WELFARE = "Staff Welfare"
    ACADEMIC_MATERIALS = "Academic Materials"
    INFRASTRUCTURE = "Infrastructure"
    OTHER = "Other"


class PaymentModeEnum(str, Enum):
    CASH = "Cash"
    CHEQUE = "Cheque"
    ONLINE_TRANSFER = "Online Transfer"
    UPI = "UPI"
    CARD = "Card"


class ExpenseStatusEnum(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    PAID = "Paid"


class ExpenseBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: ExpenseCategoryEnum
    amount: float
    tax_amount: float = 0.0
    total_amount: float
    vendor_name: Optional[str] = None
    vendor_contact: Optional[str] = None
    vendor_address: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    bill_attachment_url: Optional[str] = None
    remarks: Optional[str] = None
    is_recurring: bool = False
    recurring_frequency: Optional[str] = None
    expense_date: date


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ExpenseCategoryEnum] = None
    amount: Optional[float] = None
    tax_amount: Optional[float] = None
    total_amount: Optional[float] = None
    vendor_name: Optional[str] = None
    vendor_contact: Optional[str] = None
    vendor_address: Optional[str] = None
    payment_mode: Optional[PaymentModeEnum] = None
    payment_date: Optional[date] = None
    transaction_id: Optional[str] = None
    cheque_number: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    bill_attachment_url: Optional[str] = None
    status: Optional[ExpenseStatusEnum] = None
    rejection_reason: Optional[str] = None
    remarks: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurring_frequency: Optional[str] = None
    expense_date: Optional[date] = None


class ExpenseInDBBase(ExpenseBase):
    id: int
    payment_mode: Optional[PaymentModeEnum] = None
    payment_date: Optional[date] = None
    transaction_id: Optional[str] = None
    cheque_number: Optional[str] = None
    status: ExpenseStatusEnum
    requested_by: int
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Expense(ExpenseInDBBase):
    pass


class ExpenseWithUsers(Expense):
    requester_name: str
    approver_name: Optional[str] = None


class ExpenseApproval(BaseModel):
    status: ExpenseStatusEnum
    rejection_reason: Optional[str] = None


class ExpenseFilters(BaseModel):
    category: Optional[ExpenseCategoryEnum] = None
    status: Optional[ExpenseStatusEnum] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    vendor_name: Optional[str] = None
    requested_by: Optional[int] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None


class ExpenseListResponse(BaseModel):
    expenses: List[ExpenseWithUsers]
    total: int
    page: int
    per_page: int
    total_pages: int
    summary: dict


class ExpenseReport(BaseModel):
    period: str
    total_expenses: float
    total_approved: float
    total_pending: float
    category_breakdown: List[dict]
    monthly_trend: List[dict]
    vendor_breakdown: List[dict]


class ExpenseDashboard(BaseModel):
    total_expenses: float
    pending_approvals: int
    monthly_expenses: float
    category_wise_expenses: List[dict]
    recent_expenses: List[ExpenseWithUsers]
