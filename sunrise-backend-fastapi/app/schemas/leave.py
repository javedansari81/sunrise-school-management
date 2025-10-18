from typing import Optional, List, Union
from pydantic import BaseModel, Field, validator, field_validator
from datetime import datetime, date
from enum import Enum


class ApplicantTypeEnum(str, Enum):
    """Applicant type for leave requests"""
    STUDENT = "student"
    TEACHER = "teacher"


class LeaveRequestBase(BaseModel):
    """Base schema for leave requests supporting both students and teachers - matches database schema"""
    applicant_id: int = Field(..., description="Student ID or Teacher ID")
    applicant_type: ApplicantTypeEnum = Field(..., description="Type of applicant: student or teacher")
    leave_type_id: int = Field(..., description="Leave type ID from metadata")
    start_date: date = Field(..., description="Leave start date")
    end_date: date = Field(..., description="Leave end date")
    total_days: int = Field(..., description="Total number of leave days")
    reason: str = Field(..., min_length=3, max_length=1000, description="Reason for leave")

    # Supporting Documents
    medical_certificate_url: Optional[str] = Field(None, description="URL to medical certificate")

    # Emergency Contact
    emergency_contact: Optional[str] = Field(None, max_length=20, description="Emergency contact phone number")

    # Additional Information
    is_half_day: bool = Field(False, description="Whether it's a half day leave")
    half_day_period: Optional[str] = Field(None, description="Morning or Afternoon")

    @validator('half_day_period')
    def validate_half_day_period(cls, v, values):
        if values.get('is_half_day') and v not in ['Morning', 'Afternoon', None]:
            raise ValueError('half_day_period must be either "Morning" or "Afternoon" for half day leaves')
        return v

    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be greater than or equal to start_date')
        return v


class LeaveRequestCreate(LeaveRequestBase):
    """Schema for creating leave requests"""
    applied_to: Optional[int] = Field(None, description="User ID to whom leave is applied")

    @validator('applied_to', pre=True)
    def validate_applied_to(cls, v):
        """Convert empty string to None for optional integer field"""
        if v == "" or v is None:
            return None
        return v


class LeaveRequestCreateFriendly(BaseModel):
    """User-friendly schema for creating leave requests using human-readable identifiers - matches database schema"""
    applicant_identifier: str = Field(
        ...,
        description="Human-readable identifier: 'Roll 001: John Doe' for students or 'John Smith (EMP001)' for teachers"
    )
    applicant_type: ApplicantTypeEnum = Field(..., description="Type of applicant: student or teacher")
    leave_type_id: int = Field(..., description="Leave type ID from metadata")
    start_date: date = Field(..., description="Leave start date")
    end_date: date = Field(..., description="Leave end date")
    total_days: int = Field(..., description="Total number of leave days")
    reason: str = Field(..., min_length=3, max_length=1000, description="Reason for leave")

    # Supporting Documents
    medical_certificate_url: Optional[str] = Field(None, description="URL to medical certificate")

    # Emergency Contact
    emergency_contact: Optional[str] = Field(None, max_length=20, description="Emergency contact phone number")

    # Additional Information
    is_half_day: bool = Field(False, description="Whether it's a half day leave")
    half_day_period: Optional[str] = Field(None, description="Morning or Afternoon")

    @validator('half_day_period')
    def validate_half_day_period(cls, v, values):
        if values.get('is_half_day') and v not in ['Morning', 'Afternoon', None]:
            raise ValueError('half_day_period must be either "Morning" or "Afternoon" for half day leaves')
        return v

    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be greater than or equal to start_date')
        return v


class LeaveRequestUpdate(BaseModel):
    """Schema for updating leave requests - matches database schema"""
    applicant_id: Optional[int] = None
    applicant_type: Optional[ApplicantTypeEnum] = None
    leave_type_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_days: Optional[int] = None
    reason: Optional[str] = None
    medical_certificate_url: Optional[str] = None
    emergency_contact: Optional[str] = None
    is_half_day: Optional[bool] = None
    half_day_period: Optional[str] = None


class LeaveRequestInDBBase(LeaveRequestBase):
    """Base schema for leave requests in database - matches database schema"""
    id: int
    user_id: int
    leave_status_id: int = Field(..., description="Leave status ID from metadata")
    applied_by: int
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    approval_comments: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LeaveRequest(LeaveRequestInDBBase):
    """Complete leave request schema"""
    pass


class LeaveRequestWithDetails(LeaveRequest):
    """Leave request with additional details"""
    applicant_name: str
    applicant_details: Optional[str] = None  # Class for students, Department for teachers
    applicant_employee_id: Optional[str] = None  # Employee ID for teachers
    applicant_roll_number: Optional[int] = None  # Roll number for students
    applicant_class_id: Optional[int] = None  # Class ID for students
    leave_type_name: str
    leave_status_name: str
    leave_status_color: Optional[str] = None
    reviewer_name: Optional[str] = None


class LeaveApproval(BaseModel):
    """Schema for leave approval/rejection"""
    leave_status_id: int = Field(..., description="New status ID from metadata")
    approval_comments: Optional[str] = Field(None, description="Comments from approver")


class LeaveFilters(BaseModel):
    """Filters for leave requests"""
    applicant_id: Optional[int] = None
    applicant_type: Optional[ApplicantTypeEnum] = None
    leave_type_id: Optional[int] = None
    leave_status_id: Optional[int] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    class_id: Optional[int] = None
    department: Optional[str] = None


class LeaveListResponse(BaseModel):
    """Response schema for leave list"""
    leaves: List[LeaveRequestWithDetails]
    total: int
    page: int
    per_page: int
    total_pages: int


class LeaveReport(BaseModel):
    """Leave management report schema"""
    period: str
    total_requests: int
    approved_requests: int
    rejected_requests: int
    pending_requests: int
    approval_rate: float
    leave_type_breakdown: List[dict]
    applicant_type_breakdown: List[dict]
    department_breakdown: List[dict]


class LeaveBalanceResponse(BaseModel):
    """Leave balance response schema"""
    teacher_id: int
    teacher_name: str
    leave_type_id: int
    leave_type_name: str
    allocated_days: int
    used_days: int
    pending_days: int
    available_days: int
    carried_forward_days: int

    class Config:
        orm_mode = True


class LeavePolicyResponse(BaseModel):
    """Leave policy response schema"""
    id: int
    policy_name: str
    applicant_type: str
    leave_type_id: int
    leave_type_name: str
    max_days_per_application: Optional[int]
    max_days_per_year: Optional[int]
    min_notice_days: int
    requires_medical_certificate: bool
    requires_approval: bool
    effective_from: date
    effective_to: Optional[date]
    is_active: bool

    class Config:
        orm_mode = True
