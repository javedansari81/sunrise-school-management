from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class LeaveRequest(Base):
    """
    Leave Request model for both students and teachers
    Aligned with metadata-driven architecture using leave_types and leave_statuses tables
    Matches database schema in T600_leave_requests.sql
    """
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True)

    # Basic Information
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # User ID for authentication
    leave_type_id = Column(Integer, ForeignKey("leave_types.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_days = Column(Integer, nullable=False)
    reason = Column(Text, nullable=False)

    # Applicant Information
    applicant_type = Column(String(10), nullable=False)  # 'student' or 'teacher'
    applicant_id = Column(Integer, nullable=False)  # Student ID or Teacher ID for business logic

    # Session Year
    session_year_id = Column(Integer, ForeignKey("session_years.id"), nullable=True)

    # Status and Approval
    leave_status_id = Column(Integer, ForeignKey("leave_statuses.id"), default=1)
    applied_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approval_comments = Column(Text, nullable=True)

    # Additional Information
    is_half_day = Column(Boolean, default=False)
    half_day_period = Column(String(10), nullable=True)  # 'Morning' or 'Afternoon'
    emergency_contact = Column(String(20), nullable=True)
    medical_certificate_url = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    leave_type = relationship("LeaveType", foreign_keys=[leave_type_id])
    leave_status = relationship("LeaveStatus", foreign_keys=[leave_status_id])
    applied_by_user = relationship("User", foreign_keys=[applied_by])
    approver = relationship("User", foreign_keys=[approved_by])
    session_year = relationship("SessionYear", foreign_keys=[session_year_id])


class LeaveBalance(Base):
    """
    Leave Balance tracking for teachers
    """
    __tablename__ = "leave_balance"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    leave_type_id = Column(Integer, ForeignKey("leave_types.id"), nullable=False)
    session_year_id = Column(Integer, ForeignKey("session_years.id"), nullable=False)

    # Balance Details
    allocated_days = Column(Integer, default=0)
    used_days = Column(Integer, default=0)
    pending_days = Column(Integer, default=0)
    available_days = Column(Integer, default=0)

    # Carry Forward
    carried_forward_days = Column(Integer, default=0)
    max_carry_forward = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    teacher = relationship("Teacher", foreign_keys=[teacher_id])
    leave_type = relationship("LeaveType", foreign_keys=[leave_type_id])
    session_year = relationship("SessionYear", foreign_keys=[session_year_id])


class LeavePolicy(Base):
    """
    Leave Policy configuration
    """
    __tablename__ = "leave_policies"

    id = Column(Integer, primary_key=True, index=True)
    policy_name = Column(String(100), unique=True, nullable=False)
    applicant_type = Column(String(10), nullable=False)  # 'student', 'teacher', or 'both'
    leave_type_id = Column(Integer, ForeignKey("leave_types.id"), nullable=False)

    # Policy Rules
    max_days_per_application = Column(Integer, nullable=True)
    max_days_per_year = Column(Integer, nullable=True)
    min_notice_days = Column(Integer, default=1)
    requires_medical_certificate = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=True)

    # Validity
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    leave_type = relationship("LeaveType", foreign_keys=[leave_type_id])


class LeaveApprover(Base):
    """
    Leave Approvers configuration
    """
    __tablename__ = "leave_approvers"

    id = Column(Integer, primary_key=True, index=True)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    leave_type_id = Column(Integer, ForeignKey("leave_types.id"), nullable=False)
    applicant_type = Column(String(10), nullable=False)  # 'student' or 'teacher'

    # Approval Limits
    max_days_can_approve = Column(Integer, nullable=True)

    # Scope
    can_approve_all = Column(Boolean, default=False)
    specific_classes = Column(Text, nullable=True)  # JSON array of classes
    specific_departments = Column(Text, nullable=True)  # JSON array of departments

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    approver = relationship("User", foreign_keys=[approver_id])
    leave_type = relationship("LeaveType", foreign_keys=[leave_type_id])
