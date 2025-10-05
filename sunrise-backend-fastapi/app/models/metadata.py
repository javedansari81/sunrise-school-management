"""
Metadata models for the metadata-driven architecture
These models represent reference tables with non-auto-increment primary keys
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserType(Base):
    __tablename__ = "user_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    users = relationship("User", back_populates="user_type")


class SessionYear(Base):
    __tablename__ = "session_years"

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_current = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    students = relationship("Student", back_populates="session_year")
    fee_structures = relationship("FeeStructure", back_populates="session_year")
    fee_records = relationship("FeeRecord", back_populates="session_year")


class Gender(Base):
    __tablename__ = "genders"

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    students = relationship("Student", back_populates="gender")
    teachers = relationship("Teacher", back_populates="gender")


class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    sort_order = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    students = relationship("Student", back_populates="class_ref")
    teachers = relationship("Teacher", back_populates="class_teacher_of_ref")
    fee_structures = relationship("FeeStructure", back_populates="class_ref")


class PaymentType(Base):
    __tablename__ = "payment_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    fee_records = relationship("FeeRecord", back_populates="payment_type")


class PaymentStatus(Base):
    __tablename__ = "payment_statuses"

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    color_code = Column(String(10), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    fee_records = relationship("FeeRecord", back_populates="payment_status")


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    requires_reference = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    fee_records = relationship("FeeRecord", back_populates="payment_method")
    fee_payments = relationship("FeePayment", back_populates="payment_method")


class LeaveType(Base):
    __tablename__ = "leave_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    max_days_per_year = Column(Integer, nullable=True)
    requires_medical_certificate = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    # leave_requests = relationship("LeaveRequest", back_populates="leave_type")


class LeaveStatus(Base):
    __tablename__ = "leave_statuses"

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    color_code = Column(String(10), nullable=True)
    is_final = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    # leave_requests = relationship("LeaveRequest", back_populates="leave_status")


class ExpenseCategory(Base):
    __tablename__ = "expense_categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    budget_limit = Column(DECIMAL(12, 2), nullable=True)
    requires_approval = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    # expenses = relationship("Expense", back_populates="expense_category")


class ExpenseStatus(Base):
    __tablename__ = "expense_statuses"

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    color_code = Column(String(10), nullable=True)
    is_final = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    # expenses = relationship("Expense", back_populates="expense_status")


class EmploymentStatus(Base):
    __tablename__ = "employment_statuses"

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    teachers = relationship("Teacher", back_populates="employment_status")


class Qualification(Base):
    __tablename__ = "qualifications"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    level_order = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    teachers = relationship("Teacher", back_populates="qualification")
