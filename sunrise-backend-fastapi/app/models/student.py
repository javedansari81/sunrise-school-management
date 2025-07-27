from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class GenderEnum(str, enum.Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class ClassEnum(str, enum.Enum):
    PG = "PG"
    NURSERY = "Nursery"
    LKG = "LKG"
    UKG = "UKG"
    CLASS_1 = "Class 1"
    CLASS_2 = "Class 2"
    CLASS_3 = "Class 3"
    CLASS_4 = "Class 4"
    CLASS_5 = "Class 5"
    CLASS_6 = "Class 6"
    CLASS_7 = "Class 7"
    CLASS_8 = "Class 8"


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    admission_number = Column(String(20), unique=True, index=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    current_class = Column(Enum(ClassEnum), nullable=False)
    section = Column(String(10), nullable=True)
    roll_number = Column(String(20), nullable=True)
    
    # Contact Information
    email = Column(String(100), nullable=True)
    phone = Column(String(15), nullable=True)
    address = Column(Text, nullable=True)
    
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
    fee_records = relationship("FeeRecord", back_populates="student")
    leave_requests = relationship("LeaveRequest", back_populates="student")
