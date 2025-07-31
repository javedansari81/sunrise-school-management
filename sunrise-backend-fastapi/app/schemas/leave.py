from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, date
from enum import Enum


class LeaveTypeEnum(str, Enum):
    """
    Leave Type Enum with metadata-driven values
    These values correspond to the IDs in the leave_types metadata table
    """
    SICK_LEAVE = "Sick Leave"
    CASUAL_LEAVE = "Casual Leave"
    EMERGENCY_LEAVE = "Emergency Leave"
    MEDICAL_LEAVE = "Medical Leave"
    PERSONAL_LEAVE = "Personal Leave"

    # Metadata table ID mappings
    class VALUE:
        SICK_LEAVE = 1
        CASUAL_LEAVE = 2
        EMERGENCY_LEAVE = 3
        MEDICAL_LEAVE = 4
        PERSONAL_LEAVE = 5

    @classmethod
    def get_id_by_name(cls, name: str) -> int:
        """Get metadata table ID by enum name"""
        name_upper = name.upper()
        if hasattr(cls.VALUE, name_upper):
            return getattr(cls.VALUE, name_upper)
        return None


class LeaveStatusEnum(str, Enum):
    """
    Leave Status Enum with metadata-driven values
    These values correspond to the IDs in the leave_statuses metadata table
    """
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    CANCELLED = "Cancelled"

    # Metadata table ID mappings
    class VALUE:
        PENDING = 1
        APPROVED = 2
        REJECTED = 3
        CANCELLED = 4

    @classmethod
    def get_id_by_name(cls, name: str) -> int:
        """Get metadata table ID by enum name"""
        name_upper = name.upper()
        if hasattr(cls.VALUE, name_upper):
            return getattr(cls.VALUE, name_upper)
        return None


class LeaveRequestBase(BaseModel):
    student_id: int
    leave_type: LeaveTypeEnum
    start_date: date
    end_date: date
    total_days: int
    reason: str
    description: Optional[str] = None
    emergency_contact: Optional[str] = None
    attachment_url: Optional[str] = None


class LeaveRequestCreate(LeaveRequestBase):
    pass


class LeaveRequestUpdate(BaseModel):
    student_id: Optional[int] = None
    leave_type: Optional[LeaveTypeEnum] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_days: Optional[int] = None
    reason: Optional[str] = None
    description: Optional[str] = None
    emergency_contact: Optional[str] = None
    attachment_url: Optional[str] = None
    status: Optional[LeaveStatusEnum] = None
    rejection_reason: Optional[str] = None


class LeaveRequestInDBBase(LeaveRequestBase):
    id: int
    status: LeaveStatusEnum
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class LeaveRequest(LeaveRequestInDBBase):
    pass


class LeaveRequestWithStudent(LeaveRequest):
    student_name: str
    student_admission_number: str
    student_class: str
    approver_name: Optional[str] = None


class LeaveApproval(BaseModel):
    status: LeaveStatusEnum
    rejection_reason: Optional[str] = None


class LeaveFilters(BaseModel):
    student_id: Optional[int] = None
    leave_type: Optional[LeaveTypeEnum] = None
    status: Optional[LeaveStatusEnum] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    class_name: Optional[str] = None


class LeaveListResponse(BaseModel):
    leaves: List[LeaveRequestWithStudent]
    total: int
    page: int
    per_page: int
    total_pages: int


class LeaveReport(BaseModel):
    period: str
    total_requests: int
    approved_requests: int
    rejected_requests: int
    pending_requests: int
    approval_rate: float
    leave_type_breakdown: List[dict]
    class_wise_breakdown: List[dict]
