from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
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


class ClassEnum(str, enum.Enum):
    PG = "PG"
    NURSERY = "NURSERY"
    LKG = "LKG"
    UKG = "UKG"
    CLASS_1 = "CLASS_1"
    CLASS_2 = "CLASS_2"
    CLASS_3 = "CLASS_3"
    CLASS_4 = "CLASS_4"
    CLASS_5 = "CLASS_5"
    CLASS_6 = "CLASS_6"
    CLASS_7 = "CLASS_7"
    CLASS_8 = "CLASS_8"
    CLASS_9 = "CLASS_9"
    CLASS_10 = "CLASS_10"
    CLASS_11 = "CLASS_11"
    CLASS_12 = "CLASS_12"

    @classmethod
    def _missing_(cls, value):
        """Handle case-insensitive enum lookup"""
        if isinstance(value, str):
            for member in cls:
                if member.value.upper() == value.upper():
                    return member
        return None


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)
    admission_number = Column(String(50), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)

    # Foreign keys to metadata tables
    gender_id = Column(Integer, ForeignKey("genders.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    session_year_id = Column(Integer, ForeignKey("session_years.id"), nullable=False)

    section = Column(String(10), nullable=True)
    roll_number = Column(String(20), nullable=True)
    blood_group = Column(String(5), nullable=True)

    # Contact Information
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), default='India')
    
    # Parent Information
    father_name = Column(String(100), nullable=False)
    father_phone = Column(String(15), nullable=True)
    father_email = Column(String(100), nullable=True)
    father_occupation = Column(String(100), nullable=True)
    
    mother_name = Column(String(100), nullable=False)
    mother_phone = Column(String(15), nullable=True)
    mother_email = Column(String(100), nullable=True)
    mother_occupation = Column(String(100), nullable=True)
    
    # Emergency Contact
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(15), nullable=True)
    emergency_contact_relation = Column(String(50), nullable=True)
    
    # Academic Information
    admission_date = Column(Date, nullable=False)
    previous_school = Column(String(200), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="student_profile")
    gender = relationship("Gender", back_populates="students")
    class_ref = relationship("Class", back_populates="students")
    session_year = relationship("SessionYear", back_populates="students")
    fee_records = relationship("FeeRecord", back_populates="student")
    # leave_requests = relationship("LeaveRequest", back_populates="student")

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
    def current_class_enum(self) -> ClassEnum:
        """Convert string current_class to ClassEnum for application logic"""
        try:
            # Handle case-insensitive conversion
            if isinstance(self.current_class, str):
                for member in ClassEnum:
                    if member.value.upper() == self.current_class.upper():
                        return member
            # Fallback to CLASS_1 if not found
            return ClassEnum.CLASS_1
        except (AttributeError, TypeError):
            return ClassEnum.CLASS_1
