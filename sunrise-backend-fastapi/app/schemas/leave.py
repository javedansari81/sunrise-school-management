from typing import Optional, List, Union
from pydantic import BaseModel, Field, validator, field_validator
from datetime import datetime, date
from enum import Enum


class ApplicantTypeEnum(str, Enum):
    """Applicant type for leave requests"""
    STUDENT = "student"
    TEACHER = "teacher"


class LeaveRequestBase(BaseModel):
    """Base schema for leave requests supporting both students and teachers"""
    applicant_id: int = Field(..., description="Student ID or Teacher ID")
    applicant_type: ApplicantTypeEnum = Field(..., description="Type of applicant: student or teacher")
    leave_type_id: int = Field(..., description="Leave type ID from metadata")
    start_date: date = Field(..., description="Leave start date")
    end_date: date = Field(..., description="Leave end date")
    total_days: int = Field(..., description="Total number of leave days")
    reason: str = Field(..., min_length=3, max_length=1000, description="Reason for leave")

    # Supporting Documents
    medical_certificate_url: Optional[str] = Field(None, description="URL to medical certificate")
    supporting_document_url: Optional[str] = Field(None, description="URL to supporting document")

    # For Teachers - Substitute Arrangement
    substitute_teacher_id: Optional[int] = Field(None, description="Substitute teacher ID")
    substitute_arranged: bool = Field(False, description="Whether substitute is arranged")

    # For Students - Parent Consent
    parent_consent: bool = Field(False, description="Parent consent for student leave")
    parent_signature_url: Optional[str] = Field(None, description="URL to parent signature")

    # Emergency Contact (for students)
    emergency_contact_name: Optional[str] = Field(None, description="Emergency contact name")
    emergency_contact_phone: Optional[str] = Field(None, description="Emergency contact phone")

    # Additional Information
    is_half_day: bool = Field(False, description="Whether it's a half day leave")
    half_day_session: Optional[str] = Field(None, description="Morning or afternoon session")

    @validator('substitute_teacher_id', pre=True)
    def validate_substitute_teacher_id(cls, v):
        """Convert empty string to None for optional integer field"""
        if v == "" or v is None:
            return None
        return v

    @validator('half_day_session')
    def validate_half_day_session(cls, v, values):
        if values.get('is_half_day') and v not in ['morning', 'afternoon']:
            raise ValueError('half_day_session must be either "morning" or "afternoon" for half day leaves')
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
    """User-friendly schema for creating leave requests using human-readable identifiers"""
    applicant_identifier: str = Field(
        ...,
        description="Human-readable identifier: 'Roll 001 - Class 5A' for students or 'EMP001' for teachers. Also supports legacy formats."
    )
    applicant_type: ApplicantTypeEnum = Field(..., description="Type of applicant: student or teacher")
    leave_type_id: int = Field(..., description="Leave type ID from metadata")
    start_date: date = Field(..., description="Leave start date")
    end_date: date = Field(..., description="Leave end date")
    total_days: int = Field(..., description="Total number of leave days")
    reason: str = Field(..., min_length=3, max_length=1000, description="Reason for leave")

    # Supporting Documents
    medical_certificate_url: Optional[str] = Field(None, description="URL to medical certificate")
    supporting_document_url: Optional[str] = Field(None, description="URL to supporting document")

    # For Teachers - Substitute Arrangement
    substitute_teacher_identifier: Optional[str] = Field(
        None,
        description="Substitute teacher identifier: 'John Smith (EMP001)' or legacy employee ID 'EMP001'"
    )
    substitute_arranged: bool = Field(False, description="Whether substitute is arranged")

    # For Students - Parent Consent
    parent_consent: bool = Field(False, description="Parent consent for student leave")
    parent_signature_url: Optional[str] = Field(None, description="URL to parent signature")

    # Emergency Contact (for students)
    emergency_contact_name: Optional[str] = Field(None, description="Emergency contact name")
    emergency_contact_phone: Optional[str] = Field(None, description="Emergency contact phone")

    # Additional Information
    is_half_day: bool = Field(False, description="Whether it's a half day leave")
    half_day_session: Optional[str] = Field(None, description="Morning or afternoon session")

    # Applied to (optional)
    applied_to_identifier: Optional[str] = Field(None, description="User identifier to whom leave is applied")

    @validator('substitute_teacher_identifier', pre=True)
    def validate_substitute_teacher_identifier(cls, v):
        """Convert empty string to None for optional field"""
        if v == "" or v is None:
            return None
        return v

    @validator('applied_to_identifier', pre=True)
    def validate_applied_to_identifier(cls, v):
        """Convert empty string to None for optional field"""
        if v == "" or v is None:
            return None
        return v

    @validator('half_day_session')
    def validate_half_day_session(cls, v, values):
        if values.get('is_half_day') and v not in ['morning', 'afternoon']:
            raise ValueError('half_day_session must be either "morning" or "afternoon" for half day leaves')
        return v

    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be greater than or equal to start_date')
        return v


class LeaveRequestUpdate(BaseModel):
    """Schema for updating leave requests"""
    applicant_id: Optional[int] = None
    applicant_type: Optional[ApplicantTypeEnum] = None
    leave_type_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_days: Optional[int] = None
    reason: Optional[str] = None
    medical_certificate_url: Optional[str] = None
    supporting_document_url: Optional[str] = None
    substitute_teacher_id: Optional[int] = None
    substitute_arranged: Optional[bool] = None
    parent_consent: Optional[bool] = None
    parent_signature_url: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    is_half_day: Optional[bool] = None
    half_day_session: Optional[str] = None
    applied_to: Optional[int] = None


class LeaveRequestInDBBase(LeaveRequestBase):
    """Base schema for leave requests in database"""
    id: int
    leave_status_id: int = Field(..., description="Leave status ID from metadata")
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    review_comments: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class LeaveRequest(LeaveRequestInDBBase):
    """Complete leave request schema"""
    pass


class LeaveRequestWithDetails(LeaveRequest):
    """Leave request with additional details"""
    applicant_name: str
    applicant_details: Optional[str] = None  # Class for students, Department for teachers
    leave_type_name: str
    leave_status_name: str
    leave_status_color: Optional[str] = None
    reviewer_name: Optional[str] = None


class LeaveApproval(BaseModel):
    """Schema for leave approval/rejection"""
    leave_status_id: int = Field(..., description="New status ID from metadata")
    review_comments: Optional[str] = Field(None, description="Comments from reviewer")


class LeaveFilters(BaseModel):
    """Filters for leave requests"""
    applicant_id: Optional[int] = None
    applicant_type: Optional[ApplicantTypeEnum] = None
    leave_type_id: Optional[int] = None
    leave_status_id: Optional[int] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    class_name: Optional[str] = None
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
