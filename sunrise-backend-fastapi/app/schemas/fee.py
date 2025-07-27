from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, date
from enum import Enum


class PaymentTypeEnum(str, Enum):
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    HALF_YEARLY = "Half Yearly"
    YEARLY = "Yearly"


class PaymentStatusEnum(str, Enum):
    PENDING = "Pending"
    PARTIAL = "Partial"
    PAID = "Paid"
    OVERDUE = "Overdue"


class PaymentMethodEnum(str, Enum):
    CASH = "Cash"
    CHEQUE = "Cheque"
    ONLINE = "Online"
    UPI = "UPI"
    CARD = "Card"


class SessionYearEnum(str, Enum):
    YEAR_2023_24 = "2023-24"
    YEAR_2024_25 = "2024-25"
    YEAR_2025_26 = "2025-26"
    YEAR_2026_27 = "2026-27"


# Fee Structure Schemas
class FeeStructureBase(BaseModel):
    class_name: str
    session_year: SessionYearEnum
    tuition_fee: float = 0.0
    admission_fee: float = 0.0
    development_fee: float = 0.0
    activity_fee: float = 0.0
    transport_fee: float = 0.0
    library_fee: float = 0.0
    lab_fee: float = 0.0
    exam_fee: float = 0.0
    other_fee: float = 0.0
    total_annual_fee: float


class FeeStructureCreate(FeeStructureBase):
    pass


class FeeStructureUpdate(BaseModel):
    class_name: Optional[str] = None
    session_year: Optional[SessionYearEnum] = None
    tuition_fee: Optional[float] = None
    admission_fee: Optional[float] = None
    development_fee: Optional[float] = None
    activity_fee: Optional[float] = None
    transport_fee: Optional[float] = None
    library_fee: Optional[float] = None
    lab_fee: Optional[float] = None
    exam_fee: Optional[float] = None
    other_fee: Optional[float] = None
    total_annual_fee: Optional[float] = None


class FeeStructureInDBBase(FeeStructureBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class FeeStructure(FeeStructureInDBBase):
    pass


# Fee Record Schemas
class FeeRecordBase(BaseModel):
    student_id: int
    session_year: SessionYearEnum
    payment_type: PaymentTypeEnum
    total_amount: float
    balance_amount: float
    due_date: date
    remarks: Optional[str] = None


class FeeRecordCreate(FeeRecordBase):
    pass


class FeeRecordUpdate(BaseModel):
    student_id: Optional[int] = None
    session_year: Optional[SessionYearEnum] = None
    payment_type: Optional[PaymentTypeEnum] = None
    total_amount: Optional[float] = None
    balance_amount: Optional[float] = None
    due_date: Optional[date] = None
    status: Optional[PaymentStatusEnum] = None
    remarks: Optional[str] = None


class FeeRecordInDBBase(FeeRecordBase):
    id: int
    paid_amount: float = 0.0
    status: PaymentStatusEnum
    payment_method: Optional[PaymentMethodEnum] = None
    transaction_id: Optional[str] = None
    payment_date: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class FeeRecord(FeeRecordInDBBase):
    pass


class FeeRecordWithStudent(FeeRecord):
    student_name: str
    student_admission_number: str
    student_class: str


# Fee Payment Schemas
class FeePaymentBase(BaseModel):
    fee_record_id: int
    amount: float
    payment_method: PaymentMethodEnum
    transaction_id: Optional[str] = None
    payment_date: date
    remarks: Optional[str] = None


class FeePaymentCreate(FeePaymentBase):
    pass


class FeePaymentUpdate(BaseModel):
    amount: Optional[float] = None
    payment_method: Optional[PaymentMethodEnum] = None
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
    pass


# Filter and Response Schemas
class FeeFilters(BaseModel):
    session_year: Optional[SessionYearEnum] = None
    class_name: Optional[str] = None
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
