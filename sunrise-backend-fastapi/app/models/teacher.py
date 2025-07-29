from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Date, Float
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
    BACHELOR = "Bachelor's Degree"
    MASTER = "Master's Degree"
    PHD = "PhD"
    DIPLOMA = "Diploma"
    CERTIFICATE = "Certificate"
    OTHER = "Other"


class EmploymentStatusEnum(str, enum.Enum):
    FULL_TIME = "Full Time"
    PART_TIME = "Part Time"
    CONTRACT = "Contract"
    SUBSTITUTE = "Substitute"


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)

    # Personal Information
    employee_id = Column(String(20), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)

    # Contact Information
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(15), nullable=False)
    address = Column(Text, nullable=True)
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(15), nullable=True)
    emergency_contact_relation = Column(String(50), nullable=True)

    # Professional Information
    position = Column(String(100), nullable=False)
    department = Column(String(100), nullable=True)
    subjects = Column(Text, nullable=True)  # JSON array of subjects
    qualification = Column(Enum(QualificationEnum), nullable=False)
    experience_years = Column(Integer, default=0)
    joining_date = Column(Date, nullable=False)
    employment_status = Column(Enum(EmploymentStatusEnum), default=EmploymentStatusEnum.FULL_TIME)

    # Salary Information
    salary = Column(Float, nullable=True)

    # Additional Information
    bio = Column(Text, nullable=True)
    specializations = Column(Text, nullable=True)  # JSON array of specializations
    certifications = Column(Text, nullable=True)  # JSON array of certifications
    img = Column(Text, nullable=True)  # Base64 encoded image or URL

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    # Note: Class relationships will be added when Class model is implemented

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
