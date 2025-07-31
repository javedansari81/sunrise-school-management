from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, DateTime, DECIMAL
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

    # Foreign keys to metadata tables
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    session_year_id = Column(Integer, ForeignKey("session_years.id"), nullable=False)
    
    # Fee Components
    tuition_fee = Column(DECIMAL(10, 2), default=0.0)
    admission_fee = Column(DECIMAL(10, 2), default=0.0)
    development_fee = Column(DECIMAL(10, 2), default=0.0)
    activity_fee = Column(DECIMAL(10, 2), default=0.0)
    transport_fee = Column(DECIMAL(10, 2), default=0.0)
    library_fee = Column(DECIMAL(10, 2), default=0.0)
    lab_fee = Column(DECIMAL(10, 2), default=0.0)
    exam_fee = Column(DECIMAL(10, 2), default=0.0)
    other_fee = Column(DECIMAL(10, 2), default=0.0)

    # Total
    total_annual_fee = Column(DECIMAL(10, 2), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    class_ref = relationship("Class", back_populates="fee_structures")
    session_year = relationship("SessionYear", back_populates="fee_structures")

    @property
    def class_name(self) -> str:
        """Get class display name from relationship"""
        return self.class_ref.display_name if self.class_ref else ""

    @property
    def session_year_name(self) -> str:
        """Get session year name from relationship"""
        return self.session_year.name if self.session_year else ""


class FeeRecord(Base):
    __tablename__ = "fee_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    # Foreign keys to metadata tables
    session_year_id = Column(Integer, ForeignKey("session_years.id"), nullable=False)
    payment_type_id = Column(Integer, ForeignKey("payment_types.id"), nullable=False)
    payment_status_id = Column(Integer, ForeignKey("payment_statuses.id"), default=1)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=True)

    # Fee Details
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    paid_amount = Column(DECIMAL(10, 2), default=0.0)
    balance_amount = Column(DECIMAL(10, 2), nullable=False)

    # Due Date
    due_date = Column(Date, nullable=False)

    # Payment Details (for single payment records)
    transaction_id = Column(String(100), nullable=True)
    payment_date = Column(Date, nullable=True)

    # Additional Info
    remarks = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    student = relationship("Student", back_populates="fee_records")
    session_year = relationship("SessionYear", back_populates="fee_records")
    payment_type = relationship("PaymentType", back_populates="fee_records")
    payment_status = relationship("PaymentStatus", back_populates="fee_records")
    payment_method = relationship("PaymentMethod", back_populates="fee_records")
    payments = relationship("FeePayment", back_populates="fee_record")

    @property
    def session_year_name(self) -> str:
        """Get session year name from relationship"""
        return self.session_year.name if self.session_year else ""

    @property
    def payment_type_name(self) -> str:
        """Get payment type name from relationship"""
        return self.payment_type.name if self.payment_type else ""

    @property
    def payment_status_name(self) -> str:
        """Get payment status name from relationship"""
        return self.payment_status.name if self.payment_status else ""

    @property
    def payment_method_name(self) -> str:
        """Get payment method name from relationship"""
        return self.payment_method.name if self.payment_method else ""


class FeePayment(Base):
    __tablename__ = "fee_payments"

    id = Column(Integer, primary_key=True, index=True)
    fee_record_id = Column(Integer, ForeignKey("fee_records.id"), nullable=False)

    # Payment Details
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=False)
    payment_date = Column(Date, nullable=False)
    transaction_id = Column(String(100), nullable=True)

    # Additional Info
    remarks = Column(Text, nullable=True)
    receipt_number = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    fee_record = relationship("FeeRecord", back_populates="payments")
    payment_method = relationship("PaymentMethod", back_populates="fee_payments")

    @property
    def payment_method_name(self) -> str:
        """Get payment method name from relationship"""
        return self.payment_method.name if self.payment_method else ""
