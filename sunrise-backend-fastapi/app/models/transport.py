"""
Transport Management Models
"""

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, DateTime, DECIMAL, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class TransportType(Base):
    """Transport type metadata (E-Rickshaw, Van, Bus, etc.)"""
    __tablename__ = "transport_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    base_monthly_fee = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    capacity = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    enrollments = relationship("StudentTransportEnrollment", back_populates="transport_type")
    distance_slabs = relationship("TransportDistanceSlab", back_populates="transport_type")


class TransportDistanceSlab(Base):
    """Distance-based pricing slabs for transport types"""
    __tablename__ = "transport_distance_slabs"

    id = Column(Integer, primary_key=True, index=True)
    transport_type_id = Column(Integer, ForeignKey("transport_types.id"), nullable=False)
    distance_from_km = Column(DECIMAL(5, 2), nullable=False, default=0.00)
    distance_to_km = Column(DECIMAL(5, 2), nullable=False)
    monthly_fee = Column(DECIMAL(10, 2), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    transport_type = relationship("TransportType", back_populates="distance_slabs")


class StudentTransportEnrollment(Base):
    """Student enrollment in transport services"""
    __tablename__ = "student_transport_enrollment"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    session_year_id = Column(Integer, ForeignKey("session_years.id"), nullable=False)
    transport_type_id = Column(Integer, ForeignKey("transport_types.id"), nullable=False)

    # Enrollment Details
    enrollment_date = Column(Date, nullable=False)
    discontinue_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)

    # Distance and Pricing
    distance_km = Column(DECIMAL(5, 2), nullable=True)
    monthly_fee = Column(DECIMAL(10, 2), nullable=False)

    # Additional Information
    pickup_location = Column(Text, nullable=True)
    drop_location = Column(Text, nullable=True)
    remarks = Column(Text, nullable=True)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    student = relationship("Student", back_populates="transport_enrollments")
    session_year = relationship("SessionYear")
    transport_type = relationship("TransportType", back_populates="enrollments")
    monthly_tracking = relationship("TransportMonthlyTracking", back_populates="enrollment", cascade="all, delete-orphan")
    payments = relationship("TransportPayment", back_populates="enrollment", cascade="all, delete-orphan")


class TransportMonthlyTracking(Base):
    """Month-wise tracking of transport fees"""
    __tablename__ = "transport_monthly_tracking"

    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("student_transport_enrollment.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    session_year_id = Column(Integer, ForeignKey("session_years.id"), nullable=False)

    # Month Details
    academic_month = Column(Integer, nullable=False)
    academic_year = Column(Integer, nullable=False)
    month_name = Column(String(20), nullable=False)

    # Service Status
    is_service_enabled = Column(Boolean, default=True)

    # Amount Details
    monthly_amount = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    paid_amount = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    # balance_amount is computed column in database

    # Payment Status
    due_date = Column(Date, nullable=False)
    payment_status_id = Column(Integer, ForeignKey("payment_statuses.id"), default=1)

    # Additional
    late_fee = Column(DECIMAL(10, 2), default=0.00)
    discount_amount = Column(DECIMAL(10, 2), default=0.00)
    remarks = Column(Text, nullable=True)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    enrollment = relationship("StudentTransportEnrollment", back_populates="monthly_tracking")
    student = relationship("Student")
    session_year = relationship("SessionYear")
    payment_status = relationship("PaymentStatus")


class TransportPayment(Base):
    """Transport fee payment transactions"""
    __tablename__ = "transport_payments"

    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("student_transport_enrollment.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    # Payment Details
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=False)
    payment_date = Column(Date, nullable=False)
    transaction_id = Column(String(100), nullable=True)

    # Additional Info
    remarks = Column(Text, nullable=True)
    receipt_number = Column(String(50), nullable=True)

    # Receipt Details (Phase 1: Receipt Generation)
    receipt_url = Column(Text, nullable=True)
    receipt_cloudinary_public_id = Column(String(255), nullable=True)
    receipt_generated_at = Column(DateTime(timezone=True), nullable=True)

    # Reversal Fields
    is_reversal = Column(Boolean, default=False, nullable=False)
    reverses_payment_id = Column(Integer, ForeignKey("transport_payments.id"), nullable=True)
    reversed_by_payment_id = Column(Integer, ForeignKey("transport_payments.id"), nullable=True)
    reversal_reason_id = Column(Integer, ForeignKey("reversal_reasons.id"), nullable=True)
    reversal_type = Column(String(20), nullable=True)  # FULL or PARTIAL

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    enrollment = relationship("StudentTransportEnrollment", back_populates="payments")
    student = relationship("Student")
    payment_method = relationship("PaymentMethod")
    allocations = relationship("TransportPaymentAllocation", back_populates="transport_payment", foreign_keys="[TransportPaymentAllocation.transport_payment_id]", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])
    reversal_reason = relationship("ReversalReason", foreign_keys=[reversal_reason_id])

    # Self-referential relationships for reversals
    reverses_payment = relationship(
        "TransportPayment",
        foreign_keys=[reverses_payment_id],
        remote_side=[id],
        backref="reversed_by_payments",
        uselist=False
    )

    @property
    def can_be_reversed(self) -> bool:
        """Check if this payment can be reversed"""
        return not self.is_reversal and self.reversed_by_payment_id is None

    @property
    def is_reversed(self) -> bool:
        """Check if this payment has been reversed"""
        return self.reversed_by_payment_id is not None


class TransportPaymentAllocation(Base):
    """Month-wise allocation of transport payments"""
    __tablename__ = "transport_payment_allocations"

    id = Column(Integer, primary_key=True, index=True)
    transport_payment_id = Column(Integer, ForeignKey("transport_payments.id"), nullable=False)
    monthly_tracking_id = Column(Integer, ForeignKey("transport_monthly_tracking.id"), nullable=False)
    allocated_amount = Column(DECIMAL(10, 2), nullable=False)

    # Reversal Fields
    is_reversal = Column(Boolean, default=False, nullable=False)
    reverses_allocation_id = Column(Integer, ForeignKey("transport_payment_allocations.id"), nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    transport_payment = relationship("TransportPayment", back_populates="allocations", foreign_keys=[transport_payment_id])
    monthly_tracking = relationship("TransportMonthlyTracking")
    creator = relationship("User", foreign_keys=[created_by])

    # Self-referential relationship for reversals
    reverses_allocation = relationship(
        "TransportPaymentAllocation",
        foreign_keys=[reverses_allocation_id],
        remote_side=[id],
        backref="reversed_by_allocations",
        uselist=False
    )

    @property
    def allocation_percentage(self) -> float:
        """Calculate what percentage of payment this allocation represents"""
        if self.transport_payment and self.transport_payment.amount > 0:
            return float(self.allocated_amount) / float(self.transport_payment.amount) * 100
        return 0.0

