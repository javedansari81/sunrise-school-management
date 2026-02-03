from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, date
from decimal import Decimal


# ============================================================================
# STUDENT UDISE REPORT SCHEMAS
# ============================================================================

class StudentUDISEData(BaseModel):
    """Individual student data for UDISE report"""
    # Basic Information
    id: int
    admission_number: str
    first_name: str
    last_name: str
    full_name: str = ""
    date_of_birth: date
    age: Optional[int] = None
    
    # Academic Information
    class_id: int
    class_name: str
    section: Optional[str] = None
    roll_number: Optional[str] = None
    session_year_id: int
    session_year_name: str
    admission_date: date
    
    # Personal Information
    gender_id: int
    gender_name: str
    blood_group: Optional[str] = None
    aadhar_no: Optional[str] = None
    
    # Contact Information
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = "India"
    
    # Parent Information
    father_name: str
    father_phone: Optional[str] = None
    father_email: Optional[str] = None
    father_occupation: Optional[str] = None
    
    mother_name: str
    mother_phone: Optional[str] = None
    mother_email: Optional[str] = None
    mother_occupation: Optional[str] = None
    
    # Guardian Information
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    guardian_email: Optional[str] = None
    guardian_relation: Optional[str] = None

    # Status
    is_active: bool
    
    class Config:
        from_attributes = True


class UDISEReportResponse(BaseModel):
    """Response schema for UDISE report"""
    students: List[StudentUDISEData]
    total: int
    page: int
    per_page: int
    total_pages: int
    
    # Summary statistics
    summary: dict = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


# ============================================================================
# FEE TRACKING REPORT SCHEMAS
# ============================================================================

class FeeTrackingData(BaseModel):
    """Individual student fee tracking data"""
    # Student Information
    student_id: int
    admission_number: str
    first_name: str
    last_name: str
    full_name: str = ""
    class_id: int
    class_name: str
    section: Optional[str] = None
    session_year_id: int
    session_year_name: str
    
    # Fee Information
    total_fee_amount: Decimal = Field(default=Decimal("0.00"), description="Total fee amount for the session")
    paid_fee_amount: Decimal = Field(default=Decimal("0.00"), description="Total paid fee amount")
    pending_fee_amount: Decimal = Field(default=Decimal("0.00"), description="Pending fee amount")
    fee_collection_rate: float = Field(default=0.0, description="Fee collection rate percentage")
    fee_payment_status: str = Field(default="Pending", description="Paid/Partial/Pending")

    # Transport Information
    transport_opted: bool = Field(default=False, description="Whether student has opted for transport")
    transport_type: Optional[str] = Field(None, description="Type of transport (Bus/Van/etc)")
    monthly_transport_fee: Optional[Decimal] = Field(None, description="Monthly transport fee amount")
    total_transport_amount: Optional[Decimal] = Field(None, description="Total transport amount for session")
    paid_transport_amount: Optional[Decimal] = Field(None, description="Paid transport amount")
    pending_transport_amount: Optional[Decimal] = Field(None, description="Pending transport amount")
    transport_collection_rate: Optional[float] = Field(None, description="Transport fee collection rate percentage")
    transport_payment_status: Optional[str] = Field(None, description="Paid/Partial/Pending/N/A")
    
    # Combined Totals
    total_amount: Decimal = Field(default=Decimal("0.00"), description="Total fee + transport amount")
    total_paid: Decimal = Field(default=Decimal("0.00"), description="Total paid (fee + transport)")
    total_pending: Decimal = Field(default=Decimal("0.00"), description="Total pending (fee + transport)")
    overall_collection_rate: float = Field(default=0.0, description="Overall collection rate percentage")
    
    class Config:
        from_attributes = True


class FeeTrackingReportResponse(BaseModel):
    """Response schema for fee tracking report"""
    records: List[FeeTrackingData]
    total: int
    page: int
    per_page: int
    total_pages: int
    
    # Summary statistics
    summary: dict = Field(
        default_factory=lambda: {
            "total_students": 0,
            "total_fee_amount": "0.00",
            "total_paid_amount": "0.00",
            "total_pending_amount": "0.00",
            "overall_collection_rate": 0.0,
            "students_with_transport": 0,
            "transport_total_amount": "0.00",
            "transport_paid_amount": "0.00",
            "transport_pending_amount": "0.00",
        }
    )
    
    class Config:
        from_attributes = True


# ============================================================================
# REPORT FILTER SCHEMAS
# ============================================================================

class UDISEReportFilters(BaseModel):
    """Filters for UDISE report"""
    session_year_id: Optional[int] = None
    class_id: Optional[int] = None
    section: Optional[str] = None
    gender_id: Optional[int] = None
    is_active: Optional[bool] = None
    search: Optional[str] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=25, ge=1, le=100)


class FeeTrackingReportFilters(BaseModel):
    """Filters for fee tracking report"""
    session_year_id: int = Field(..., description="Session year is required for fee tracking")
    class_id: Optional[int] = None
    section: Optional[str] = None
    payment_status: Optional[str] = Field(None, description="paid/partial/pending")
    transport_opted: Optional[bool] = None
    pending_only: bool = Field(default=False, description="Show only students with pending fees")
    search: Optional[str] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=25, ge=1, le=100)


# ============================================================================
# DAILY COLLECTION REPORT SCHEMAS
# ============================================================================

class DailyCollectionData(BaseModel):
    """Individual payment record for daily collection report"""
    # Payment Information
    payment_id: int
    receipt_number: Optional[str] = None
    payment_date: date
    amount: Decimal = Field(default=Decimal("0.00"), description="Payment amount")
    payment_method: str = Field(default="Cash", description="Payment method name")
    transaction_id: Optional[str] = None

    # Student Information
    student_id: int
    admission_number: str
    student_name: str
    class_name: str
    section: Optional[str] = None

    # Fee Record Information
    fee_record_id: int
    session_year_name: str

    # Payment Type (Fee/Transport)
    payment_type: str = Field(default="Fee", description="Fee or Transport")

    # Additional Info
    remarks: Optional[str] = None
    created_by_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DailyCollectionReportResponse(BaseModel):
    """Response schema for daily collection report"""
    records: List[DailyCollectionData]
    total: int
    page: int
    per_page: int
    total_pages: int

    # Summary statistics
    summary: dict = Field(
        default_factory=lambda: {
            "total_collections": 0,
            "total_amount": "0.00",
            "cash_amount": "0.00",
            "online_amount": "0.00",
            "upi_amount": "0.00",
            "cheque_amount": "0.00",
            "card_amount": "0.00",
            "fee_collections": "0.00",
            "transport_collections": "0.00",
        }
    )

    class Config:
        from_attributes = True


class DailyCollectionReportFilters(BaseModel):
    """Filters for daily collection report"""
    from_date: date = Field(..., description="Start date for collection report")
    to_date: date = Field(..., description="End date for collection report")
    class_id: Optional[int] = None
    section: Optional[str] = None
    payment_method_id: Optional[int] = None
    search: Optional[str] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=25, ge=1, le=100)
