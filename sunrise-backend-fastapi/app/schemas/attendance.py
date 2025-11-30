from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date, time
from enum import Enum


class AttendanceStatusEnum(str, Enum):
    """Attendance status enumeration"""
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"
    HALF_DAY = "HALF_DAY"
    EXCUSED = "EXCUSED"
    HOLIDAY = "HOLIDAY"
    LEAVE = "LEAVE"


class AttendancePeriodEnum(str, Enum):
    """Attendance period enumeration"""
    FULL_DAY = "FULL_DAY"
    MORNING = "MORNING"
    AFTERNOON = "AFTERNOON"


# ============================================
# Metadata Schemas
# ============================================

class AttendanceStatusBase(BaseModel):
    """Base schema for attendance status"""
    name: str
    description: Optional[str] = None
    color_code: Optional[str] = None
    affects_attendance_percentage: bool = True
    is_active: bool = True


class AttendanceStatus(AttendanceStatusBase):
    """Schema for attendance status response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AttendancePeriodBase(BaseModel):
    """Base schema for attendance period"""
    name: str
    description: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_active: bool = True


class AttendancePeriod(AttendancePeriodBase):
    """Schema for attendance period response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# Attendance Record Schemas
# ============================================

class AttendanceRecordBase(BaseModel):
    """Base schema for attendance records"""
    student_id: int = Field(..., description="Student ID")
    class_id: int = Field(..., description="Class ID")
    session_year_id: int = Field(..., description="Session year ID")
    attendance_date: date = Field(..., description="Attendance date")
    attendance_status_id: int = Field(..., description="Attendance status ID")
    attendance_period_id: int = Field(1, description="Attendance period ID (default: Full Day)")
    check_in_time: Optional[time] = Field(None, description="Check-in time")
    check_out_time: Optional[time] = Field(None, description="Check-out time")
    remarks: Optional[str] = Field(None, max_length=500, description="Additional remarks")
    leave_request_id: Optional[int] = Field(None, description="Related leave request ID")


class AttendanceRecordCreate(AttendanceRecordBase):
    """Schema for creating attendance record"""
    pass


class AttendanceRecordUpdate(BaseModel):
    """Schema for updating attendance record"""
    attendance_status_id: Optional[int] = None
    attendance_period_id: Optional[int] = None
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    remarks: Optional[str] = None
    leave_request_id: Optional[int] = None


class AttendanceRecord(AttendanceRecordBase):
    """Schema for attendance record response"""
    id: int
    marked_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Enriched fields (from joins)
    student_name: Optional[str] = None
    student_roll_number: Optional[str] = None
    class_name: Optional[str] = None
    attendance_status_name: Optional[str] = None
    attendance_status_description: Optional[str] = None
    attendance_status_color: Optional[str] = None
    attendance_period_name: Optional[str] = None
    marked_by_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============================================
# Bulk Operations
# ============================================

class BulkAttendanceItem(BaseModel):
    """Schema for individual item in bulk attendance"""
    student_id: int
    attendance_status_id: int
    check_in_time: Optional[time] = None
    remarks: Optional[str] = None


class BulkAttendanceCreate(BaseModel):
    """Schema for bulk attendance creation"""
    class_id: int
    session_year_id: int
    attendance_date: date
    attendance_period_id: int = 1
    records: List[BulkAttendanceItem]

    @field_validator('records')
    @classmethod
    def validate_records(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one attendance record is required')
        return v


# ============================================
# Filters and List Response
# ============================================

class AttendanceFilters(BaseModel):
    """Schema for attendance filtering"""
    attendance_date: Optional[date] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    class_id: Optional[int] = None
    student_id: Optional[int] = None
    attendance_status_id: Optional[int] = None
    session_year_id: int = 4
    search: Optional[str] = None


class AttendanceListResponse(BaseModel):
    """Schema for paginated attendance list response"""
    records: List[AttendanceRecord]
    total: int
    page: int
    per_page: int
    total_pages: int


# ============================================
# Summary and Statistics
# ============================================

class StudentAttendanceSummary(BaseModel):
    """Schema for student attendance summary"""
    student_id: int
    student_name: str
    student_roll_number: Optional[str] = None
    class_name: str
    session_year: str
    total_school_days: int
    days_present: int
    days_absent: int
    days_late: int
    days_half_day: int
    days_excused: int
    attendance_percentage: float
    from_date: date
    to_date: date


class ClassAttendanceSummary(BaseModel):
    """Schema for class attendance summary"""
    class_id: int
    class_name: str
    attendance_date: date
    total_students: int
    students_present: int
    students_absent: int
    students_late: int
    attendance_percentage: float


class AttendanceStatistics(BaseModel):
    """Schema for attendance statistics"""
    total_records: int
    total_present: int
    total_absent: int
    total_late: int
    overall_attendance_percentage: float
    date_range: str

