from sqlalchemy import Column, Integer, String, DECIMAL, Date, ForeignKey, Text, DateTime, Boolean, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Expense(Base):
    """
    Expense model aligned with metadata-driven architecture
    Uses expense_categories, expense_statuses, and payment_methods metadata tables
    """
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)

    # Basic Information
    expense_date = Column(Date, nullable=False)
    expense_category_id = Column(Integer, ForeignKey("expense_categories.id"), nullable=False)
    subcategory = Column(String(100), nullable=True)
    description = Column(Text, nullable=False)

    # Financial Details
    amount = Column(DECIMAL(12, 2), nullable=False)
    tax_amount = Column(DECIMAL(10, 2), default=0.0)
    total_amount = Column(DECIMAL(12, 2), nullable=False)
    currency = Column(String(3), default='INR')

    # Vendor Information
    vendor_name = Column(String(200), nullable=True)
    vendor_contact = Column(String(20), nullable=True)
    vendor_email = Column(String(255), nullable=True)
    vendor_address = Column(Text, nullable=True)
    vendor_gst_number = Column(String(20), nullable=True)

    # Payment Details
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=False)
    payment_status_id = Column(Integer, ForeignKey("payment_statuses.id"), default=1)
    payment_date = Column(Date, nullable=True)
    payment_reference = Column(String(100), nullable=True)

    # Bank/Cheque Details
    bank_name = Column(String(100), nullable=True)
    cheque_number = Column(String(50), nullable=True)
    cheque_date = Column(Date, nullable=True)

    # Approval Workflow
    expense_status_id = Column(Integer, ForeignKey("expense_statuses.id"), default=1)
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approval_comments = Column(Text, nullable=True)

    # Budget Information
    budget_category = Column(String(100), nullable=True)
    session_year_id = Column(Integer, ForeignKey("session_years.id"), nullable=True)
    is_budgeted = Column(Boolean, default=False)

    # Documents
    invoice_url = Column(String(500), nullable=True)
    receipt_url = Column(String(500), nullable=True)
    supporting_documents = Column(JSON, nullable=True)  # Array of document URLs

    # Additional Information
    is_recurring = Column(Boolean, default=False)
    recurring_frequency = Column(String(20), nullable=True)  # Monthly, Quarterly, Half Yearly, Yearly
    next_due_date = Column(Date, nullable=True)

    # Priority and Urgency
    priority = Column(String(10), default='Medium')  # Low, Medium, High, Urgent
    is_emergency = Column(Boolean, default=False)

    # Soft Delete Functionality
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_date = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    expense_category = relationship("ExpenseCategory", foreign_keys=[expense_category_id])
    expense_status = relationship("ExpenseStatus", foreign_keys=[expense_status_id])
    payment_method = relationship("PaymentMethod", foreign_keys=[payment_method_id])
    payment_status = relationship("PaymentStatus", foreign_keys=[payment_status_id])
    session_year = relationship("SessionYear", foreign_keys=[session_year_id])
    requester = relationship("User", foreign_keys=[requested_by])
    approver = relationship("User", foreign_keys=[approved_by])


class Vendor(Base):
    """
    Vendor/Supplier management for expenses
    """
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)

    # Basic Information
    vendor_name = Column(String(200), nullable=False)
    contact_person = Column(String(100), nullable=True)

    # Contact Information
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    country = Column(String(100), default='India')

    # Business Information
    gst_number = Column(String(20), nullable=True)
    pan_number = Column(String(15), nullable=True)
    vendor_categories = Column(JSONB, nullable=True)

    # Banking Information
    bank_name = Column(String(100), nullable=True)
    account_number = Column(String(50), nullable=True)
    ifsc_code = Column(String(15), nullable=True)
    account_holder_name = Column(String(200), nullable=True)

    # Contract Information
    contract_start_date = Column(Date, nullable=True)
    contract_end_date = Column(Date, nullable=True)
    payment_terms = Column(String(100), nullable=True)
    credit_limit = Column(DECIMAL(12, 2), default=0.0)

    # Performance Metrics
    rating = Column(DECIMAL(3, 2), nullable=True)
    total_orders = Column(Integer, default=0)
    total_amount = Column(DECIMAL(15, 2), default=0.0)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Soft Delete
    is_deleted = Column(Boolean, default=False)
    deleted_date = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class Budget(Base):
    """
    Budget planning and tracking
    """
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)

    # Budget Information
    budget_name = Column(String(200), nullable=False)
    session_year_id = Column(Integer, ForeignKey("session_years.id"), nullable=False)
    expense_category_id = Column(Integer, ForeignKey("expense_categories.id"), nullable=False)

    # Budget Amounts
    allocated_amount = Column(DECIMAL(12, 2), nullable=False)
    spent_amount = Column(DECIMAL(12, 2), default=0.0)
    committed_amount = Column(DECIMAL(12, 2), default=0.0)  # For pending approvals
    available_amount = Column(DECIMAL(12, 2), nullable=False)

    # Budget Period
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    # Status and Approval
    is_active = Column(Boolean, default=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    # Additional Information
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    session_year = relationship("SessionYear", foreign_keys=[session_year_id])
    expense_category = relationship("ExpenseCategory", foreign_keys=[expense_category_id])
    approver = relationship("User", foreign_keys=[approved_by])


class ExpenseReport(Base):
    """
    Generated expense reports
    """
    __tablename__ = "expense_reports"

    id = Column(Integer, primary_key=True, index=True)

    # Report Information
    report_name = Column(String(200), nullable=False)
    report_type = Column(String(50), nullable=False)  # Monthly, Quarterly, Yearly, Custom

    # Report Period
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    session_year_id = Column(Integer, ForeignKey("session_years.id"), nullable=True)

    # Report Data
    total_expenses = Column(DECIMAL(12, 2), default=0.0)
    total_approved = Column(DECIMAL(12, 2), default=0.0)
    total_pending = Column(DECIMAL(12, 2), default=0.0)
    total_rejected = Column(DECIMAL(12, 2), default=0.0)

    # Report Content
    report_data = Column(JSON, nullable=True)  # Detailed report data
    report_url = Column(String(500), nullable=True)  # Generated report file URL

    # Generation Information
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Status
    is_published = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    session_year = relationship("SessionYear", foreign_keys=[session_year_id])
    generator = relationship("User", foreign_keys=[generated_by])
