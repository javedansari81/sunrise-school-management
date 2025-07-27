from sqlalchemy import Column, Integer, String, Float, Date, Enum, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class ExpenseCategoryEnum(str, enum.Enum):
    INFRASTRUCTURE = "Infrastructure"
    MAINTENANCE = "Maintenance"
    UTILITIES = "Utilities"
    SUPPLIES = "Supplies"
    EQUIPMENT = "Equipment"
    TRANSPORTATION = "Transportation"
    EVENTS = "Events"
    MARKETING = "Marketing"
    STAFF_WELFARE = "Staff Welfare"
    ACADEMIC = "Academic"
    SPORTS = "Sports"
    LIBRARY = "Library"
    LABORATORY = "Laboratory"
    SECURITY = "Security"
    CLEANING = "Cleaning"
    OTHER = "Other"


class PaymentModeEnum(str, enum.Enum):
    CASH = "Cash"
    CHEQUE = "Cheque"
    ONLINE = "Online Transfer"
    UPI = "UPI"
    CARD = "Card"


class ExpenseStatusEnum(str, enum.Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    PAID = "Paid"
    REJECTED = "Rejected"


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Enum(ExpenseCategoryEnum), nullable=False)
    
    # Amount Details
    amount = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    
    # Vendor/Supplier Information
    vendor_name = Column(String(200), nullable=True)
    vendor_contact = Column(String(15), nullable=True)
    vendor_address = Column(Text, nullable=True)
    
    # Payment Information
    payment_mode = Column(Enum(PaymentModeEnum), nullable=True)
    payment_date = Column(Date, nullable=True)
    transaction_id = Column(String(100), nullable=True)
    cheque_number = Column(String(50), nullable=True)
    
    # Invoice/Bill Information
    invoice_number = Column(String(100), nullable=True)
    invoice_date = Column(Date, nullable=True)
    bill_attachment_url = Column(String(500), nullable=True)
    
    # Approval Workflow
    status = Column(Enum(ExpenseStatusEnum), default=ExpenseStatusEnum.PENDING)
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Additional Information
    remarks = Column(Text, nullable=True)
    is_recurring = Column(Boolean, default=False)
    recurring_frequency = Column(String(50), nullable=True)  # Monthly, Quarterly, Yearly
    
    # Timestamps
    expense_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    requester = relationship("User", foreign_keys=[requested_by])
    approver = relationship("User", foreign_keys=[approved_by])
