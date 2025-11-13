from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, date
from enum import Enum
from decimal import Decimal


class PaymentTypeEnum(str, Enum):
    """
    Payment Type Enum with metadata-driven values
    These values correspond to the IDs in the payment_types metadata table
    """
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    HALF_YEARLY = "Half Yearly"
    YEARLY = "Yearly"

    # Metadata table ID mappings
    class VALUE:
        MONTHLY = 1
        QUARTERLY = 2
        HALF_YEARLY = 3
        YEARLY = 4

    @classmethod
    def get_id_by_name(cls, name: str) -> int:
        """Get metadata table ID by enum name"""
        name_upper = name.upper()
        if hasattr(cls.VALUE, name_upper):
            return getattr(cls.VALUE, name_upper)
        return None


class PaymentStatusEnum(str, Enum):
    """
    Payment Status Enum with metadata-driven values
    These values correspond to the IDs in the payment_statuses metadata table
    """
    PENDING = "Pending"
    PARTIAL = "Partial"
    PAID = "Paid"
    OVERDUE = "Overdue"

    # Metadata table ID mappings
    class VALUE:
        PENDING = 1
        PAID = 2
        PARTIAL = 3
        OVERDUE = 4

    @classmethod
    def get_id_by_name(cls, name: str) -> int:
        """Get metadata table ID by enum name"""
        name_upper = name.upper()
        if hasattr(cls.VALUE, name_upper):
            return getattr(cls.VALUE, name_upper)
        return None


class PaymentMethodEnum(str, Enum):
    """
    Payment Method Enum with metadata-driven values
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


class SessionYearEnum(str, Enum):
    """
    Session Year Enum with metadata-driven values
    These values correspond to the IDs in the session_years metadata table
    """
    YEAR_2022_23 = "2022-23"
    YEAR_2023_24 = "2023-24"
    YEAR_2024_25 = "2024-25"
    YEAR_2025_26 = "2025-26"
    YEAR_2026_27 = "2026-27"

    # Metadata table ID mappings
    class VALUE:
        YEAR_2022_23 = 1
        YEAR_2023_24 = 2
        YEAR_2024_25 = 3
        YEAR_2025_26 = 4
        YEAR_2026_27 = 5

    @classmethod
    def get_id_by_name(cls, name: str) -> int:
        """Get metadata table ID by enum name"""
        name_upper = name.upper()
        if hasattr(cls.VALUE, name_upper):
            return getattr(cls.VALUE, name_upper)
        return None


# Fee Structure Schemas
class FeeStructureBase(BaseModel):
    class_id: int = Field(..., description="Foreign key to classes table")
    session_year_id: int = Field(..., description="Foreign key to session_years table")
    tuition_fee: Decimal = Field(default=Decimal('0.0'), ge=0)
    admission_fee: Decimal = Field(default=Decimal('0.0'), ge=0)
    development_fee: Decimal = Field(default=Decimal('0.0'), ge=0)
    activity_fee: Decimal = Field(default=Decimal('0.0'), ge=0)
    transport_fee: Decimal = Field(default=Decimal('0.0'), ge=0)
    library_fee: Decimal = Field(default=Decimal('0.0'), ge=0)
    lab_fee: Decimal = Field(default=Decimal('0.0'), ge=0)
    exam_fee: Decimal = Field(default=Decimal('0.0'), ge=0)
    other_fee: Decimal = Field(default=Decimal('0.0'), ge=0)
    total_annual_fee: Decimal = Field(..., ge=0)


class FeeStructureCreate(FeeStructureBase):
    pass


class FeeStructureUpdate(BaseModel):
    class_id: Optional[int] = None
    session_year_id: Optional[int] = None
    tuition_fee: Optional[Decimal] = Field(None, ge=0)
    admission_fee: Optional[Decimal] = Field(None, ge=0)
    development_fee: Optional[Decimal] = Field(None, ge=0)
    activity_fee: Optional[Decimal] = Field(None, ge=0)
    transport_fee: Optional[Decimal] = Field(None, ge=0)
    library_fee: Optional[Decimal] = Field(None, ge=0)
    lab_fee: Optional[Decimal] = Field(None, ge=0)
    exam_fee: Optional[Decimal] = Field(None, ge=0)
    other_fee: Optional[Decimal] = Field(None, ge=0)
    total_annual_fee: Optional[Decimal] = Field(None, ge=0)


class FeeStructureInDBBase(FeeStructureBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class FeeStructure(FeeStructureInDBBase):
    # Computed fields for API responses
    class_name: Optional[str] = Field(None, description="Resolved class name")
    session_year_name: Optional[str] = Field(None, description="Resolved session year name")

    @classmethod
    def from_orm_with_metadata(cls, db_fee_structure):
        """Create FeeStructure schema with resolved metadata values"""
        fee_data = {
            "id": db_fee_structure.id,
            "class_id": db_fee_structure.class_id,
            "session_year_id": db_fee_structure.session_year_id,
            "tuition_fee": db_fee_structure.tuition_fee,
            "admission_fee": db_fee_structure.admission_fee,
            "development_fee": db_fee_structure.development_fee,
            "activity_fee": db_fee_structure.activity_fee,
            "transport_fee": db_fee_structure.transport_fee,
            "library_fee": db_fee_structure.library_fee,
            "lab_fee": db_fee_structure.lab_fee,
            "exam_fee": db_fee_structure.exam_fee,
            "other_fee": db_fee_structure.other_fee,
            "total_annual_fee": db_fee_structure.total_annual_fee,
            "created_at": db_fee_structure.created_at,
            "updated_at": db_fee_structure.updated_at,
            "class_name": db_fee_structure.class_ref.description if db_fee_structure.class_ref else None,
            "session_year_name": db_fee_structure.session_year.name if db_fee_structure.session_year else None
        }
        return cls(**fee_data)


# Fee Record Schemas
class FeeRecordBase(BaseModel):
    student_id: int = Field(..., description="Foreign key to students table")
    session_year_id: int = Field(..., description="Foreign key to session_years table")
    payment_type_id: int = Field(..., description="Foreign key to payment_types table")
    total_amount: Decimal = Field(..., ge=0)
    balance_amount: Decimal = Field(..., ge=0)
    due_date: date
    remarks: Optional[str] = None


class FeeRecordCreate(FeeRecordBase):
    # Additional fields for creation
    payment_status_id: int = Field(..., description="Foreign key to payment_statuses table")
    payment_method_id: Optional[int] = None
    fee_structure_id: Optional[int] = None
    is_monthly_tracked: bool = Field(..., description="Whether this record uses monthly tracking")
    academic_month: Optional[int] = None
    academic_year: Optional[int] = None
    paid_amount: Decimal = Field(default=Decimal('0.0'), ge=0, description="Amount already paid")
    transaction_id: Optional[str] = None
    payment_date: Optional[date] = None


class FeeRecordUpdate(BaseModel):
    student_id: Optional[int] = None
    session_year_id: Optional[int] = None
    payment_type_id: Optional[int] = None
    payment_status_id: Optional[int] = None
    payment_method_id: Optional[int] = None
    total_amount: Optional[Decimal] = Field(None, ge=0)
    paid_amount: Optional[Decimal] = Field(None, ge=0)
    balance_amount: Optional[Decimal] = Field(None, ge=0)
    due_date: Optional[date] = None
    transaction_id: Optional[str] = None
    payment_date: Optional[date] = None
    remarks: Optional[str] = None


class FeeRecordInDBBase(FeeRecordBase):
    id: int
    paid_amount: Decimal = Decimal('0.0')
    payment_status_id: int = 1
    payment_method_id: Optional[int] = None
    transaction_id: Optional[str] = None
    payment_date: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class FeeRecord(FeeRecordInDBBase):
    # Computed fields for API responses
    student_name: Optional[str] = Field(None, description="Student full name")
    session_year_name: Optional[str] = Field(None, description="Resolved session year name")
    payment_type_name: Optional[str] = Field(None, description="Resolved payment type name")
    payment_status_name: Optional[str] = Field(None, description="Resolved payment status name")
    payment_method_name: Optional[str] = Field(None, description="Resolved payment method name")

    @classmethod
    def from_orm_with_metadata(cls, db_fee_record):
        """Create FeeRecord schema with resolved metadata values"""
        fee_data = {
            "id": db_fee_record.id,
            "student_id": db_fee_record.student_id,
            "session_year_id": db_fee_record.session_year_id,
            "payment_type_id": db_fee_record.payment_type_id,
            "payment_status_id": db_fee_record.payment_status_id,
            "payment_method_id": db_fee_record.payment_method_id,
            "total_amount": db_fee_record.total_amount,
            "paid_amount": db_fee_record.paid_amount,
            "balance_amount": db_fee_record.balance_amount,
            "due_date": db_fee_record.due_date,
            "transaction_id": db_fee_record.transaction_id,
            "payment_date": db_fee_record.payment_date,
            "remarks": db_fee_record.remarks,
            "created_at": db_fee_record.created_at,
            "updated_at": db_fee_record.updated_at,
            "student_name": f"{db_fee_record.student.first_name} {db_fee_record.student.last_name}" if db_fee_record.student else None,
            "session_year_name": db_fee_record.session_year.name if db_fee_record.session_year else None,
            "payment_type_name": db_fee_record.payment_type.name if db_fee_record.payment_type else None,
            "payment_status_name": db_fee_record.payment_status.name if db_fee_record.payment_status else None,
            "payment_method_name": db_fee_record.payment_method.name if db_fee_record.payment_method else None
        }
        return cls(**fee_data)


class FeeRecordWithStudent(FeeRecord):
    student_name: str
    student_admission_number: str
    student_class: str


# Fee Payment Schemas
class FeePaymentBase(BaseModel):
    fee_record_id: int
    amount: float
    payment_method_id: int  # Changed from PaymentMethodEnum to int to match database model
    transaction_id: Optional[str] = None
    payment_date: date
    remarks: Optional[str] = None


class FeePaymentCreate(FeePaymentBase):
    pass


class FeePaymentUpdate(BaseModel):
    amount: Optional[float] = None
    payment_method_id: Optional[int] = None  # Changed from PaymentMethodEnum to int
    transaction_id: Optional[str] = None
    payment_date: Optional[date] = None
    remarks: Optional[str] = None


class FeePaymentInDBBase(FeePaymentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class FeePayment(FeePaymentInDBBase):
    # Reversal fields
    is_reversal: bool = False
    reverses_payment_id: Optional[int] = None
    reversed_by_payment_id: Optional[int] = None
    reversal_reason: Optional[str] = None
    reversal_type: Optional[str] = None
    created_by: Optional[int] = None

    # Computed properties
    is_reversed: bool = False
    can_be_reversed: bool = True


# Reversal Reason Enum (DEPRECATED - Use reversal_reason_id from configuration endpoint instead)
class ReversalReasonEnum(str, Enum):
    INCORRECT_AMOUNT = "Incorrect Amount Entered"
    DUPLICATE_PAYMENT = "Duplicate Payment"
    WRONG_STUDENT = "Wrong Student Account"
    WRONG_PAYMENT_METHOD = "Wrong Payment Method"
    PROCESSING_ERROR = "Payment Processing Error"
    STUDENT_REQUEST = "Student Request/Refund"
    ADMINISTRATIVE_CORRECTION = "Administrative Correction"
    OTHER = "Other"


# Payment Reversal Schemas
class FeePaymentReversalRequest(BaseModel):
    """Request schema for full payment reversal"""
    reason_id: int = Field(..., description="Reversal reason ID from reversal_reasons table")
    details: Optional[str] = Field(None, description="Additional details about the reversal")


class FeePaymentPartialReversalRequest(BaseModel):
    """Request schema for partial (month-specific) payment reversal"""
    allocation_ids: List[int] = Field(..., min_items=1, description="List of monthly_payment_allocation IDs to reverse")
    reason_id: int = Field(..., description="Reversal reason ID from reversal_reasons table")
    details: Optional[str] = Field(None, description="Additional details about the reversal")


class FeePaymentReversalResponse(BaseModel):
    """Response schema for payment reversal operations"""
    success: bool
    message: str
    original_payment_id: int
    reversal_payment_id: int
    reversal_amount: float
    reversal_type: str  # 'FULL' or 'PARTIAL'
    affected_months: List[dict]
    fee_record_updated: dict


# Filter and Response Schemas
class FeeFilters(BaseModel):
    session_year: Optional[SessionYearEnum] = None
    class_id: Optional[int] = None
    month: Optional[int] = None
    status: Optional[PaymentStatusEnum] = None
    payment_type: Optional[PaymentTypeEnum] = None
    student_id: Optional[int] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None


class FeeListResponse(BaseModel):
    fees: List[FeeRecordWithStudent]
    total: int
    page: int
    per_page: int
    total_pages: int
    summary: dict


class FeeCollectionReport(BaseModel):
    period: str
    total_collected: float
    total_pending: float
    total_students: int
    collection_percentage: float


class FeeDashboard(BaseModel):
    total_students: int
    total_fees_collected: float
    total_fees_pending: float
    overdue_fees: float
    collection_rate: float
    monthly_collection: List[dict]
    class_wise_collection: List[dict]
    payment_method_breakdown: List[dict]


# Monthly Fee Tracking Schemas
class MonthlyFeeTrackingBase(BaseModel):
    academic_month: int = Field(..., ge=1, le=12, description="Academic month (1-12)")
    academic_year: int = Field(..., description="Academic year")
    month_name: str = Field(..., description="Month name (January, February, etc.)")
    monthly_amount: float = Field(..., ge=0, description="Monthly fee amount")
    paid_amount: float = Field(0, ge=0, description="Amount paid for this month")
    due_date: date = Field(..., description="Due date for this month")
    late_fee: float = Field(0, ge=0, description="Late fee amount")
    discount_amount: float = Field(0, ge=0, description="Discount amount")


class MonthlyFeeTrackingCreate(MonthlyFeeTrackingBase):
    fee_record_id: int = Field(..., description="Foreign key to fee_records")
    student_id: int = Field(..., description="Foreign key to students")
    session_year_id: int = Field(..., description="Foreign key to session_years")
    payment_status_id: int = Field(1, description="Payment status ID")


class MonthlyFeeTrackingUpdate(BaseModel):
    paid_amount: Optional[float] = Field(None, ge=0, description="Amount paid for this month")
    payment_status_id: Optional[int] = Field(None, description="Payment status ID")
    late_fee: Optional[float] = Field(None, ge=0, description="Late fee amount")
    discount_amount: Optional[float] = Field(None, ge=0, description="Discount amount")


class MonthlyFeeTracking(MonthlyFeeTrackingBase):
    id: int
    fee_record_id: int
    student_id: int
    session_year_id: int
    payment_status_id: int
    balance_amount: float = Field(..., description="Calculated balance amount")
    status_name: str = Field(..., description="Payment status name")
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Enhanced Student Fee Summary
class EnhancedStudentFeeSummary(BaseModel):
    student_id: int
    admission_number: str
    student_name: str
    class_name: str
    session_year: str

    # Legacy fee record data
    fee_record_id: Optional[int] = None
    annual_fee: Optional[float] = None
    total_paid: Optional[float] = None
    total_balance: Optional[float] = None

    # Monthly tracking data
    total_months_tracked: int = Field(0, description="Number of months with tracking")
    paid_months: int = Field(0, description="Number of fully paid months")
    pending_months: int = Field(0, description="Number of pending months")
    overdue_months: int = Field(0, description="Number of overdue months")
    monthly_total: Optional[float] = Field(None, description="Total monthly amounts")
    monthly_paid: Optional[float] = Field(None, description="Total monthly payments")
    monthly_balance: Optional[float] = Field(None, description="Total monthly balance")

    # Calculated fields
    collection_percentage: float = Field(0, description="Percentage of fees collected")
    has_monthly_tracking: bool = Field(False, description="Whether student has monthly tracking enabled")

    # Transport enrollment status (for quick access button)
    has_transport_enrollment: bool = Field(False, description="Whether student has active transport enrollment")
    transport_enrollment_id: Optional[int] = Field(None, description="Transport enrollment ID if enrolled")

    class Config:
        from_attributes = True


# Monthly Fee Status Response
class MonthlyFeeStatus(BaseModel):
    month: int
    year: int
    month_name: str
    monthly_amount: float
    paid_amount: float
    balance_amount: float
    due_date: date
    status: str
    status_color: str = Field(..., description="Color code for UI display")
    is_overdue: bool
    days_overdue: Optional[int] = None
    late_fee: float = 0
    discount_amount: float = 0


class StudentMonthlyFeeHistory(BaseModel):
    student_id: int
    student_name: str
    admission_number: str
    roll_number: Optional[str] = None
    class_name: str
    session_year: str
    monthly_fee_amount: float
    total_annual_fee: float
    monthly_history: List[MonthlyFeeStatus]

    # Summary statistics
    total_months: int
    paid_months: int
    pending_months: int
    overdue_months: int
    total_paid: float
    total_balance: float
    collection_percentage: float

    class Config:
        from_attributes = True


# Enhanced Payment Request
class EnhancedPaymentRequest(BaseModel):
    student_id: int
    from_month: int = Field(..., ge=1, le=12, description="Starting month")
    to_month: int = Field(..., ge=1, le=12, description="Ending month")
    payment_method_id: int = Field(..., description="Payment method ID")
    amount: float = Field(..., gt=0, description="Payment amount")
    transaction_id: Optional[str] = Field(None, description="Transaction reference ID")
    remarks: Optional[str] = Field(None, description="Payment remarks")
    session_year_id: int = Field(..., description="Session year ID")
    enable_monthly_tracking: bool = Field(True, description="Enable monthly tracking for this payment")


# Monthly Tracking Enable Request
class EnableMonthlyTrackingRequest(BaseModel):
    fee_record_ids: List[int] = Field(..., description="List of fee record IDs to enable tracking for")
    start_month: int = Field(4, ge=1, le=12, description="Starting academic month (default: April)")
    start_year: Optional[int] = Field(None, description="Starting academic year (default: current year)")
