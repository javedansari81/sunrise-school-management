"""
Pydantic schemas for metadata models
These schemas are used for API responses and validation
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, date


# Base metadata schema
class MetadataBase(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# User Type schemas
class UserTypeResponse(MetadataBase):
    pass


# Session Year schemas
class SessionYearResponse(MetadataBase):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False


# Gender schemas
class GenderResponse(MetadataBase):
    pass


# Class schemas
class ClassResponse(MetadataBase):
    display_name: Optional[str] = None
    sort_order: Optional[int] = None


# Payment Type schemas
class PaymentTypeResponse(MetadataBase):
    pass


# Payment Status schemas
class PaymentStatusResponse(MetadataBase):
    color_code: Optional[str] = None


# Payment Method schemas
class PaymentMethodResponse(MetadataBase):
    requires_reference: bool = False


# Leave Type schemas
class LeaveTypeResponse(MetadataBase):
    max_days_per_year: Optional[int] = None
    requires_medical_certificate: bool = False


# Leave Status schemas
class LeaveStatusResponse(MetadataBase):
    color_code: Optional[str] = None
    is_final: bool = False


# Expense Category schemas
class ExpenseCategoryResponse(MetadataBase):
    budget_limit: Optional[float] = None
    requires_approval: bool = True


# Expense Status schemas
class ExpenseStatusResponse(MetadataBase):
    color_code: Optional[str] = None
    is_final: bool = False


# Employment Status schemas
class EmploymentStatusResponse(MetadataBase):
    pass


# Qualification schemas
class QualificationResponse(MetadataBase):
    level_order: Optional[int] = None


# Configuration response schema
class ConfigurationResponse(BaseModel):
    user_types: List[UserTypeResponse]
    session_years: List[SessionYearResponse]
    genders: List[GenderResponse]
    classes: List[ClassResponse]
    payment_types: List[PaymentTypeResponse]
    payment_statuses: List[PaymentStatusResponse]
    payment_methods: List[PaymentMethodResponse]
    leave_types: List[LeaveTypeResponse]
    leave_statuses: List[LeaveStatusResponse]
    expense_categories: List[ExpenseCategoryResponse]
    expense_statuses: List[ExpenseStatusResponse]
    employment_statuses: List[EmploymentStatusResponse]
    qualifications: List[QualificationResponse]
    metadata: dict = Field(default_factory=dict, description="Additional metadata information")


# Helper schemas for dropdowns
class DropdownOption(BaseModel):
    id: int
    name: str
    display_name: Optional[str] = None
    is_active: bool = True


class DropdownResponse(BaseModel):
    options: List[DropdownOption]
    total: int


# Metadata creation/update schemas (for admin use)
class MetadataCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    is_active: bool = True


class MetadataUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


# Specific metadata creation schemas
class UserTypeCreate(MetadataCreate):
    pass


class SessionYearCreate(MetadataCreate):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False


class ClassCreate(MetadataCreate):
    display_name: Optional[str] = Field(None, max_length=50)
    sort_order: Optional[int] = None


class PaymentStatusCreate(MetadataCreate):
    color_code: Optional[str] = Field(None, max_length=10)


class PaymentMethodCreate(MetadataCreate):
    requires_reference: bool = False


class LeaveTypeCreate(MetadataCreate):
    max_days_per_year: Optional[int] = Field(None, ge=0, le=365)
    requires_medical_certificate: bool = False


class LeaveStatusCreate(MetadataCreate):
    color_code: Optional[str] = Field(None, max_length=10)
    is_final: bool = False


class ExpenseCategoryCreate(MetadataCreate):
    budget_limit: Optional[float] = Field(None, ge=0)
    requires_approval: bool = True


class ExpenseStatusCreate(MetadataCreate):
    color_code: Optional[str] = Field(None, max_length=10)
    is_final: bool = False


class QualificationCreate(MetadataCreate):
    level_order: Optional[int] = Field(None, ge=1, le=10)


# Bulk operations
class BulkMetadataUpdate(BaseModel):
    items: List[dict] = Field(..., description="List of metadata items to update")
    table_name: str = Field(..., description="Name of the metadata table")


class BulkOperationResponse(BaseModel):
    success: bool
    updated_count: int
    errors: List[str] = Field(default_factory=list)
    message: str
