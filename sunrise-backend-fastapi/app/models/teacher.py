from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Date, Float, ForeignKey, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class GenderEnum(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

    @classmethod
    def _missing_(cls, value):
        """Handle case-insensitive enum lookup"""
        if isinstance(value, str):
            for member in cls:
                if member.value.upper() == value.upper():
                    return member
        return None


class QualificationEnum(str, enum.Enum):
    BACHELOR = "BACHELOR"
    MASTER = "MASTER"
    PHD = "PHD"
    DIPLOMA = "DIPLOMA"
    CERTIFICATE = "CERTIFICATE"
    OTHER = "OTHER"

    @classmethod
    def _missing_(cls, value):
        """Handle case-insensitive enum lookup"""
        if isinstance(value, str):
            for member in cls:
                if member.value.upper() == value.upper():
                    return member
        return None


class EmploymentStatusEnum(str, enum.Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    SUBSTITUTE = "SUBSTITUTE"

    @classmethod
    def _missing_(cls, value):
        """Handle case-insensitive enum lookup"""
        if isinstance(value, str):
            for member in cls:
                if member.value.upper() == value.upper():
                    return member
        return None


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)

    # Personal Information
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=True)

    # Foreign key to metadata table
    gender_id = Column(Integer, ForeignKey("genders.id"), nullable=True)

    # Contact Information
    phone = Column(String(20), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    aadhar_no = Column(String(12), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), default='India')

    # Emergency Contact
    emergency_contact_name = Column(String(200), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    emergency_contact_relation = Column(String(50), nullable=True)

    # Professional Information
    position = Column(String(100), nullable=False)
    department = Column(String(100), nullable=True)
    subjects = Column(Text, nullable=True)  # JSON array of subjects

    # Foreign keys to metadata tables
    qualification_id = Column(Integer, ForeignKey("qualifications.id"), nullable=True)
    employment_status_id = Column(Integer, ForeignKey("employment_statuses.id"), default=1)

    experience_years = Column(Integer, default=0)
    joining_date = Column(Date, nullable=False)

    # Class Assignments
    class_teacher_of_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    classes_assigned = Column(Text, nullable=True)  # JSON array of class IDs

    # Salary Information
    salary = Column(Float, nullable=True)

    # Additional Information (commented out until database schema is updated)
    # bio = Column(Text, nullable=True)
    # specializations = Column(Text, nullable=True)  # JSON array of specializations
    # certifications = Column(Text, nullable=True)  # JSON array of certifications
    # img = Column(Text, nullable=True)  # Base64 encoded image or URL

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="teacher_profile")
    gender = relationship("Gender", back_populates="teachers")
    qualification = relationship("Qualification", back_populates="teachers")
    employment_status = relationship("EmploymentStatus", back_populates="teachers")
    class_teacher_of_ref = relationship("Class", back_populates="teachers")
    # leave_requests = relationship("LeaveRequest", back_populates="teacher")

    @property
    def full_name(self) -> str:
        """Get full name of teacher"""
        return f"{self.first_name} {self.last_name}"

    @property
    def gender_name(self) -> str:
        """Get gender name from relationship"""
        return self.gender.name if self.gender else ""

    @property
    def qualification_name(self) -> str:
        """Get qualification name from relationship"""
        return self.qualification.name if self.qualification else ""

    @property
    def employment_status_name(self) -> str:
        """Get employment status name from relationship"""
        return self.employment_status.name if self.employment_status else ""

    @property
    def gender_enum(self) -> GenderEnum:
        """Convert string gender to GenderEnum for application logic"""
        try:
            # Handle case-insensitive conversion
            if isinstance(self.gender, str):
                for member in GenderEnum:
                    if member.value.upper() == self.gender.upper():
                        return member
            # Fallback to MALE if not found
            return GenderEnum.MALE
        except (AttributeError, TypeError):
            return GenderEnum.MALE

    @property
    def qualification_enum(self) -> QualificationEnum:
        """Convert string qualification to QualificationEnum for application logic"""
        try:
            # Handle case-insensitive conversion
            if isinstance(self.qualification, str):
                for member in QualificationEnum:
                    if member.value.upper() == self.qualification.upper():
                        return member
            # Fallback to BACHELOR if not found
            return QualificationEnum.BACHELOR
        except (AttributeError, TypeError):
            return QualificationEnum.BACHELOR

    @property
    def employment_status_enum(self) -> EmploymentStatusEnum:
        """Convert string employment_status to EmploymentStatusEnum for application logic"""
        try:
            # Handle case-insensitive conversion
            if isinstance(self.employment_status, str):
                for member in EmploymentStatusEnum:
                    if member.value.upper() == self.employment_status.upper():
                        return member
            # Fallback to FULL_TIME if not found
            return EmploymentStatusEnum.FULL_TIME
        except (AttributeError, TypeError):
            return EmploymentStatusEnum.FULL_TIME
