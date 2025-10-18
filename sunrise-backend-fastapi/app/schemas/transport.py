"""
Transport Management Schemas
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, date
from decimal import Decimal


# =====================================================
# Transport Type Schemas
# =====================================================

class TransportTypeBase(BaseModel):
    name: str = Field(..., max_length=50)
    description: Optional[str] = None
    base_monthly_fee: Decimal = Field(..., ge=0)
    capacity: Optional[int] = None


class TransportTypeCreate(TransportTypeBase):
    id: int = Field(..., description="Manually assigned ID")


class TransportTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    base_monthly_fee: Optional[Decimal] = Field(None, ge=0)
    capacity: Optional[int] = None
    is_active: Optional[bool] = None


class TransportTypeResponse(TransportTypeBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# =====================================================
# Transport Distance Slab Schemas
# =====================================================

class TransportDistanceSlabBase(BaseModel):
    transport_type_id: int
    distance_from_km: Decimal = Field(..., ge=0)
    distance_to_km: Decimal = Field(..., gt=0)
    monthly_fee: Decimal = Field(..., ge=0)
    description: Optional[str] = None


class TransportDistanceSlabCreate(TransportDistanceSlabBase):
    pass


class TransportDistanceSlabUpdate(BaseModel):
    distance_from_km: Optional[Decimal] = Field(None, ge=0)
    distance_to_km: Optional[Decimal] = Field(None, gt=0)
    monthly_fee: Optional[Decimal] = Field(None, ge=0)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class TransportDistanceSlabResponse(TransportDistanceSlabBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# =====================================================
# Student Transport Enrollment Schemas
# =====================================================

class StudentTransportEnrollmentBase(BaseModel):
    student_id: int
    session_year_id: int
    transport_type_id: int
    enrollment_date: date
    distance_km: Optional[Decimal] = Field(None, ge=0)
    monthly_fee: Decimal = Field(..., ge=0)
    pickup_location: Optional[str] = None
    drop_location: Optional[str] = None
    remarks: Optional[str] = None


class StudentTransportEnrollmentCreate(StudentTransportEnrollmentBase):
    pass


class StudentTransportEnrollmentUpdate(BaseModel):
    transport_type_id: Optional[int] = None
    distance_km: Optional[Decimal] = Field(None, ge=0)
    monthly_fee: Optional[Decimal] = Field(None, ge=0)
    pickup_location: Optional[str] = None
    drop_location: Optional[str] = None
    remarks: Optional[str] = None
    discontinue_date: Optional[date] = None
    is_active: Optional[bool] = None


class StudentTransportEnrollmentResponse(StudentTransportEnrollmentBase):
    id: int
    discontinue_date: Optional[date] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# =====================================================
# Transport Monthly Tracking Schemas
# =====================================================

class TransportMonthlyTrackingBase(BaseModel):
    academic_month: int = Field(..., ge=1, le=12)
    academic_year: int
    month_name: str
    is_service_enabled: bool = True
    monthly_amount: Decimal = Field(..., ge=0)
    paid_amount: Decimal = Field(0, ge=0)
    due_date: date
    late_fee: Decimal = Field(0, ge=0)
    discount_amount: Decimal = Field(0, ge=0)


class TransportMonthlyTrackingCreate(TransportMonthlyTrackingBase):
    enrollment_id: int
    student_id: int
    session_year_id: int
    payment_status_id: int = 1


class TransportMonthlyTrackingUpdate(BaseModel):
    is_service_enabled: Optional[bool] = None
    paid_amount: Optional[Decimal] = Field(None, ge=0)
    payment_status_id: Optional[int] = None
    late_fee: Optional[Decimal] = Field(None, ge=0)
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    remarks: Optional[str] = None


class TransportMonthlyTrackingResponse(TransportMonthlyTrackingBase):
    id: int
    enrollment_id: int
    student_id: int
    session_year_id: int
    payment_status_id: int
    balance_amount: Decimal
    status_name: str = Field(..., description="Payment status name")
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# =====================================================
# Transport Payment Schemas
# =====================================================

class TransportPaymentBase(BaseModel):
    amount: Decimal = Field(..., gt=0)
    payment_method_id: int
    payment_date: date
    transaction_id: Optional[str] = None
    remarks: Optional[str] = None


class TransportPaymentCreate(TransportPaymentBase):
    enrollment_id: int
    student_id: int
    receipt_number: Optional[str] = None


class TransportPaymentResponse(TransportPaymentBase):
    id: int
    enrollment_id: int
    student_id: int
    receipt_number: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# Enhanced Schemas for UI
# =====================================================

class EnhancedStudentTransportSummary(BaseModel):
    """Enhanced summary for transport management UI"""
    student_id: int
    admission_number: str
    student_name: str
    class_name: str
    session_year: str
    
    # Enrollment Info
    enrollment_id: Optional[int] = None
    transport_type_id: Optional[int] = None
    transport_type_name: Optional[str] = None
    enrollment_date: Optional[date] = None
    discontinue_date: Optional[date] = None
    is_enrolled: bool = False
    distance_km: Optional[Decimal] = None
    monthly_fee: Optional[Decimal] = None
    pickup_location: Optional[str] = None
    drop_location: Optional[str] = None
    
    # Monthly Tracking Statistics
    total_months_tracked: int = 0
    enabled_months: int = 0
    paid_months: int = 0
    pending_months: int = 0
    overdue_months: int = 0
    
    # Financial Summary
    total_amount: Decimal = Decimal('0.0')
    total_paid: Decimal = Decimal('0.0')
    total_balance: Decimal = Decimal('0.0')
    collection_percentage: Decimal = Decimal('0.0')
    
    # Tracking Status
    has_monthly_tracking: bool = False

    class Config:
        from_attributes = True


class StudentTransportMonthlyHistory(BaseModel):
    """Monthly history for a student's transport fees"""
    student_id: int
    student_name: str
    class_name: str
    session_year: str
    transport_type_name: str
    monthly_fee_amount: Decimal
    
    # Monthly records
    monthly_history: List[TransportMonthlyTrackingResponse]
    
    # Summary
    total_months: int
    enabled_months: int
    paid_months: int
    pending_months: int
    overdue_months: int
    total_paid: Decimal
    total_balance: Decimal
    collection_percentage: Decimal

    class Config:
        from_attributes = True


class EnableTransportMonthlyTrackingRequest(BaseModel):
    """Request to enable monthly tracking for transport enrollments"""
    enrollment_ids: List[int] = Field(..., description="List of enrollment IDs")
    start_month: int = Field(4, ge=1, le=12, description="Starting academic month (default: April)")
    start_year: int = Field(..., description="Starting academic year")


class TransportPaymentRequest(BaseModel):
    """Request for making transport payment"""
    amount: Decimal = Field(..., gt=0)
    payment_method_id: int
    selected_months: List[int] = Field(..., description="List of month numbers to pay")
    transaction_id: Optional[str] = None
    remarks: Optional[str] = None

