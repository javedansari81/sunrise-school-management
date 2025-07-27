from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class LeaveTypeEnum(str, enum.Enum):
    SICK = "Sick Leave"
    CASUAL = "Casual Leave"
    EMERGENCY = "Emergency Leave"
    FAMILY = "Family Function"
    MEDICAL = "Medical Leave"
    OTHER = "Other"


class LeaveStatusEnum(str, enum.Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    CANCELLED = "Cancelled"


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Leave Details
    leave_type = Column(Enum(LeaveTypeEnum), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_days = Column(Integer, nullable=False)
    
    # Reason and Description
    reason = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Status and Approval
    status = Column(Enum(LeaveStatusEnum), default=LeaveStatusEnum.PENDING)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Contact Information during leave
    emergency_contact = Column(String(15), nullable=True)
    
    # Attachments (if any)
    attachment_url = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="leave_requests")
    approver = relationship("User", foreign_keys=[approved_by])
