from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, date
from enum import Enum


class ExpenseCategoryEnum(str, Enum):
    """
    Expense Category Enum with metadata-driven values
    These values correspond to the IDs in the expense_categories metadata table
    """
    INFRASTRUCTURE = "Infrastructure"
    MAINTENANCE = "Maintenance"
    UTILITIES = "Utilities"
    SUPPLIES = "Supplies"
    EQUIPMENT = "Equipment"
    TRANSPORTATION = "Transportation"
    EVENTS = "Events"
    MARKETING = "Marketing"
    STAFF_WELFARE = "Staff Welfare"
    ACADEMIC = "Academic"
    SPORTS = "Sports"
    LIBRARY = "Library"
    LABORATORY = "Laboratory"
    SECURITY = "Security"
    CLEANING = "Cleaning"
    OTHER = "Other"

    # Metadata table ID mappings
    class VALUE:
        INFRASTRUCTURE = 1
        MAINTENANCE = 2
        UTILITIES = 3
        SUPPLIES = 4
        EQUIPMENT = 5
        TRANSPORTATION = 6
        EVENTS = 7
        MARKETING = 8
        STAFF_WELFARE = 9
        ACADEMIC = 10
        SPORTS = 11
        LIBRARY = 12
        LABORATORY = 13
        SECURITY = 14
        CLEANING = 15
        OTHER = 16

    @classmethod
    def get_id_by_name(cls, name: str) -> int:
        """Get metadata table ID by enum name"""
        name_upper = name.upper()
        if hasattr(cls.VALUE, name_upper):
            return getattr(cls.VALUE, name_upper)
        return None


class PaymentModeEnum(str, Enum):
    """
    Payment Mode Enum with metadata-driven values
    These values correspond to the IDs in the payment_methods metadata table
    """
    CASH = "Cash"
    CHEQUE = "Cheque"
    ONLINE = "Online"
    UPI = "UPI"
    CARD = "Card"

    # Metadata table ID mappings
    class VALUE:
        CASH = 1
        CHEQUE = 2
        ONLINE = 3
        UPI = 4
        CARD = 5

    @classmethod
    def get_id_by_name(cls, name: str) -> int:
        """Get metadata table ID by enum name"""
        name_upper = name.upper()
        if hasattr(cls.VALUE, name_upper):
            return getattr(cls.VALUE, name_upper)
        return None


class ExpenseStatusEnum(str, Enum):
    """
    Expense Status Enum with metadata-driven values
    These values correspond to the IDs in the expense_statuses metadata table
    """
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    PAID = "Paid"

    # Metadata table ID mappings
    class VALUE:
        PENDING = 1
        APPROVED = 2
        REJECTED = 3
        PAID = 4

    @classmethod
    def get_id_by_name(cls, name: str) -> int:
        """Get metadata table ID by enum name"""
        name_upper = name.upper()
        if hasattr(cls.VALUE, name_upper):
            return getattr(cls.VALUE, name_upper)
        return None


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
