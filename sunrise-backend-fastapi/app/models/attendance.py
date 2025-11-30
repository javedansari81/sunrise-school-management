from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AttendanceStatus(Base):
    """
    Attendance Status metadata model
    Stores status definitions like Present, Absent, Late, etc.
    Matches database schema in T290_attendance_statuses.sql
    """
    __tablename__ = "attendance_statuses"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    color_code = Column(String(10), nullable=True)
    affects_attendance_percentage = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AttendancePeriod(Base):
    """
    Attendance Period metadata model
    Stores period definitions like Full Day, Morning, Afternoon
    Matches database schema in T295_attendance_periods.sql
    """
    __tablename__ = "attendance_periods"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AttendanceRecord(Base):
    """
    Attendance Record model for daily student attendance
    Aligned with metadata-driven architecture using attendance_statuses and attendance_periods tables
    Matches database schema in T800_attendance_records.sql
    """
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    
    # Student Information
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    session_year_id = Column(Integer, ForeignKey("session_years.id"), nullable=False)
    
    # Attendance Details
    attendance_date = Column(Date, nullable=False)
    attendance_status_id = Column(Integer, ForeignKey("attendance_statuses.id"), nullable=False)
    attendance_period_id = Column(Integer, ForeignKey("attendance_periods.id"), default=1)
    
    # Time Tracking
    check_in_time = Column(Time, nullable=True)
    check_out_time = Column(Time, nullable=True)
    
    # Additional Information
    remarks = Column(Text, nullable=True)
    marked_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Leave Integration (Optional)
    leave_request_id = Column(Integer, ForeignKey("leave_requests.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", foreign_keys=[student_id])
    class_ref = relationship("Class", foreign_keys=[class_id])
    session_year = relationship("SessionYear", foreign_keys=[session_year_id])
    attendance_status = relationship("AttendanceStatus", foreign_keys=[attendance_status_id])
    attendance_period = relationship("AttendancePeriod", foreign_keys=[attendance_period_id])
    marker = relationship("User", foreign_keys=[marked_by])
    leave_request = relationship("LeaveRequest", foreign_keys=[leave_request_id])

