"""
SQLAlchemy models of the unified fee module. Tables: Database/Tables/T900-T950.

Every model is tenant-scoped (TenantMixin): queries are filtered by the request's
school and new rows are stamped with it by app.core.tenant.
"""
from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, Column, Date, DateTime, DECIMAL, ForeignKey,
    Integer, SmallInteger, String, Text, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.tenant import TenantMixin

Money = DECIMAL(10, 2)

# Read server defaults (created_at, ...) back on INSERT/UPDATE, so no lazy load is
# needed afterwards (lazy IO is not allowed on async sessions).
EAGER = {"eager_defaults": True}


class FeeHead(TenantMixin, Base):
    __tablename__ = "fee_heads"
    __mapper_args__ = EAGER
    __table_args__ = (
        UniqueConstraint("school_id", "code", name="fee_heads_school_code_unique"),
        UniqueConstraint("school_id", "name", name="fee_heads_school_name_unique"),
    )

    id = Column(Integer, primary_key=True)
    code = Column(String(30), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(20), nullable=False, default="ACADEMIC")
    default_frequency = Column(String(20), nullable=False, default="MONTHLY")
    is_system = Column(Boolean, nullable=False, default=False)
    sort_order = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FeeStructure(TenantMixin, Base):
    __tablename__ = "fee_structures"
    __mapper_args__ = EAGER

    id = Column(Integer, primary_key=True)
    session_year_id = Column(Integer, ForeignKey("session_years.id"), nullable=False)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    status = Column(String(20), nullable=False, default="DRAFT")
    copied_from_id = Column(Integer, ForeignKey("fee_structures.id"))
    published_at = Column(DateTime(timezone=True))
    published_by = Column(Integer, ForeignKey("users.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    items = relationship(
        "FeeStructureItem", back_populates="structure", cascade="all, delete-orphan",
        order_by="FeeStructureItem.id", lazy="selectin",
    )


class FeeStructureItem(TenantMixin, Base):
    __tablename__ = "fee_structure_items"
    __mapper_args__ = EAGER

    id = Column(Integer, primary_key=True)
    fee_structure_id = Column(Integer, ForeignKey("fee_structures.id", ondelete="CASCADE"), nullable=False)
    fee_head_id = Column(Integer, ForeignKey("fee_heads.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"))
    amount = Column(Money, nullable=False)
    frequency = Column(String(20), nullable=False, default="MONTHLY")
    billing_months = Column(ARRAY(SmallInteger))
    due_day = Column(SmallInteger, nullable=False, default=10)
    applies_to = Column(String(20), nullable=False, default="ALL")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    structure = relationship("FeeStructure", back_populates="items")


class ConcessionRule(TenantMixin, Base):
    __tablename__ = "concession_rules"
    __mapper_args__ = EAGER
    __table_args__ = (UniqueConstraint("school_id", "name", name="concession_rules_school_name_unique"),)

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    concession_type = Column(String(20), nullable=False)
    value_type = Column(String(10), nullable=False, default="PERCENT")
    value = Column(Money, nullable=False, default=0)
    fee_head_ids = Column(ARRAY(Integer))
    tiers = Column(JSONB)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class StudentFeePlan(TenantMixin, Base):
    __tablename__ = "student_fee_plans"
    __mapper_args__ = EAGER

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    session_year_id = Column(Integer, ForeignKey("session_years.id"), nullable=False)
    fee_head_id = Column(Integer, ForeignKey("fee_heads.id"), nullable=False)
    amount = Column(Money, nullable=False)
    frequency = Column(String(20), nullable=False, default="MONTHLY")
    billing_months = Column(ARRAY(SmallInteger))
    due_day = Column(SmallInteger, nullable=False, default=10)
    start_period = Column(Date, nullable=False)
    end_period = Column(Date)
    source = Column(String(20), nullable=False)
    source_ref_id = Column(Integer)
    is_active = Column(Boolean, nullable=False, default=True)
    remarks = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class StudentConcession(TenantMixin, Base):
    __tablename__ = "student_concessions"
    __mapper_args__ = EAGER

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    session_year_id = Column(Integer, ForeignKey("session_years.id"), nullable=False)
    concession_rule_id = Column(Integer, ForeignKey("concession_rules.id"))
    concession_type = Column(String(20), nullable=False)
    value_type = Column(String(10), nullable=False)
    value = Column(Money, nullable=False)
    fee_head_ids = Column(ARRAY(Integer))
    start_period = Column(Date)
    end_period = Column(Date)
    reason = Column(Text, nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, nullable=False, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class StudentDue(TenantMixin, Base):
    __tablename__ = "student_dues"
    __mapper_args__ = EAGER
    __table_args__ = (CheckConstraint("net_amount = gross_amount - concession_amount", name="student_dues_net"),)

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    session_year_id = Column(Integer, ForeignKey("session_years.id"), nullable=False)
    fee_head_id = Column(Integer, ForeignKey("fee_heads.id"), nullable=False)
    student_fee_plan_id = Column(Integer, ForeignKey("student_fee_plans.id"))
    line_type = Column(String(20), nullable=False, default="REGULAR")
    related_due_id = Column(Integer, ForeignKey("student_dues.id"))
    period = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    description = Column(String(255))
    gross_amount = Column(Money, nullable=False)
    concession_amount = Column(Money, nullable=False, default=0)
    net_amount = Column(Money, nullable=False)
    paid_amount = Column(Money, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="PENDING")
    cancelled_at = Column(DateTime(timezone=True))
    cancelled_by = Column(Integer, ForeignKey("users.id"))
    cancel_reason = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def balance(self):
        return self.net_amount - self.paid_amount


class ReceiptSequence(TenantMixin, Base):
    __tablename__ = "receipt_sequences"
    __mapper_args__ = EAGER
    __table_args__ = (
        UniqueConstraint("school_id", "session_year_id", name="receipt_sequences_school_session_unique"),
    )

    id = Column(Integer, primary_key=True)
    session_year_id = Column(Integer, ForeignKey("session_years.id"), nullable=False)
    prefix = Column(String(20), nullable=False)
    next_number = Column(Integer, nullable=False, default=1)
    padding = Column(SmallInteger, nullable=False, default=6)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Payment(TenantMixin, Base):
    __tablename__ = "payments"
    __mapper_args__ = EAGER
    __table_args__ = (UniqueConstraint("school_id", "receipt_number", name="payments_receipt_unique"),)

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    session_year_id = Column(Integer, ForeignKey("session_years.id"), nullable=False)
    kind = Column(String(10), nullable=False, default="PAYMENT")
    receipt_number = Column(String(40))
    amount = Column(Money, nullable=False)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"))
    payment_date = Column(Date, nullable=False, server_default=func.current_date())
    transaction_id = Column(String(100))
    remarks = Column(Text)
    reverses_payment_id = Column(Integer, ForeignKey("payments.id"))
    reversal_reason_id = Column(Integer, ForeignKey("reversal_reasons.id"))
    receipt_url = Column(Text)
    receipt_cloudinary_id = Column(Text)
    gateway_name = Column(String(30))
    gateway_order_id = Column(String(100))
    gateway_payment_id = Column(String(100))
    gateway_status = Column(String(30))
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Allocations of this payment's money (reversal rows included, as negatives)
    allocations = relationship(
        "PaymentAllocation", foreign_keys="PaymentAllocation.payment_id",
        back_populates="payment", lazy="selectin", order_by="PaymentAllocation.id",
    )
    # For a REVERSAL: the negative allocation rows it added to the original payment
    reversal_allocations = relationship(
        "PaymentAllocation", foreign_keys="PaymentAllocation.reversal_payment_id",
        lazy="selectin", order_by="PaymentAllocation.id", viewonly=True,
    )


class PaymentAllocation(TenantMixin, Base):
    __tablename__ = "payment_allocations"
    __mapper_args__ = EAGER

    id = Column(Integer, primary_key=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    student_due_id = Column(Integer, ForeignKey("student_dues.id"), nullable=False)
    amount = Column(Money, nullable=False)
    is_reversal = Column(Boolean, nullable=False, default=False)
    reversal_payment_id = Column(Integer, ForeignKey("payments.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    payment = relationship("Payment", foreign_keys=[payment_id], back_populates="allocations")


class FeeAuditLog(TenantMixin, Base):
    __tablename__ = "fee_audit_log"
    __mapper_args__ = EAGER

    id = Column(BigInteger, primary_key=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    remarks = Column(Text)
    performed_by = Column(Integer, ForeignKey("users.id"))
    performed_at = Column(DateTime(timezone=True), server_default=func.now())
