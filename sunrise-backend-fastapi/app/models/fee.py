from sqlalchemy import Column, Integer, String, Float, Date, Enum, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class PaymentTypeEnum(str, enum.Enum):
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    HALF_YEARLY = "Half Yearly"
    YEARLY = "Yearly"


class PaymentStatusEnum(str, enum.Enum):
    PENDING = "Pending"
    PARTIAL = "Partial"
    PAID = "Paid"
    OVERDUE = "Overdue"


class PaymentMethodEnum(str, enum.Enum):
    CASH = "Cash"
    CHEQUE = "Cheque"
    ONLINE = "Online"
    UPI = "UPI"
    CARD = "Card"


class SessionYearEnum(str, enum.Enum):
    YEAR_2022_23 = "2022-23"
    YEAR_2023_24 = "2023-24"
    YEAR_2024_25 = "2024-25"
    YEAR_2025_26 = "2025-26"
    YEAR_2026_27 = "2026-27"


class FeeStructure(Base):
    __tablename__ = "fee_structures"

    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String(20), nullable=False)
    session_year = Column(String(10), nullable=False)
    
    # Fee Components
    tuition_fee = Column(Float, default=0.0)
    admission_fee = Column(Float, default=0.0)
    development_fee = Column(Float, default=0.0)
    activity_fee = Column(Float, default=0.0)
    transport_fee = Column(Float, default=0.0)
    library_fee = Column(Float, default=0.0)
    lab_fee = Column(Float, default=0.0)
    exam_fee = Column(Float, default=0.0)
    other_fee = Column(Float, default=0.0)
    
    # Total
    total_annual_fee = Column(Float, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def session_year_enum(self) -> SessionYearEnum:
        """Convert string session_year to SessionYearEnum for application logic"""
        try:
            for member in SessionYearEnum:
                if member.value == self.session_year:
                    return member
            return SessionYearEnum.YEAR_2024_25  # Default fallback
        except (AttributeError, TypeError):
            return SessionYearEnum.YEAR_2024_25


class FeeRecord(Base):
    __tablename__ = "fee_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    session_year = Column(String(10), nullable=False)
    payment_type = Column(String(20), nullable=False)

    # Fee Details
    total_amount = Column(Float, nullable=False)
    paid_amount = Column(Float, default=0.0)
    balance_amount = Column(Float, nullable=False)

    # Payment Status
    status = Column(String(20), default="Pending")

    # Due Date
    due_date = Column(Date, nullable=False)

    # Payment Details
    payment_method = Column(String(20), nullable=True)
    transaction_id = Column(String(100), nullable=True)
    payment_date = Column(Date, nullable=True)
    
    # Additional Info
    remarks = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="fee_records")
    payments = relationship("FeePayment", back_populates="fee_record")


class FeePayment(Base):
    __tablename__ = "fee_payments"

    id = Column(Integer, primary_key=True, index=True)
    fee_record_id = Column(Integer, ForeignKey("fee_records.id"), nullable=False)
    
    # Payment Details
    amount = Column(Float, nullable=False)
    payment_method = Column(String(20), nullable=False)
    payment_date = Column(Date, nullable=False)
    transaction_id = Column(String(100), nullable=True)
    
    # Additional Info
    remarks = Column(Text, nullable=True)
    receipt_number = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    fee_record = relationship("FeeRecord", back_populates="payments")
