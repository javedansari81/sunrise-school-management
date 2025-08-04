from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from enum import Enum


class GenderEnum(str, Enum):
    """
    Gender Enum with metadata-driven values
    These values correspond to the IDs in the genders metadata table
    """
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

    # Metadata table ID mappings
    class VALUE:
        MALE = 1
        FEMALE = 2
        OTHER = 3

    @classmethod
    def get_id_by_name(cls, name: str) -> int:
        """Get metadata table ID by enum name"""
        name_upper = name.upper()
        if hasattr(cls.VALUE, name_upper):
            return getattr(cls.VALUE, name_upper)
        return None

    @classmethod
    def get_name_by_id(cls, id: int) -> str:
        """Get enum name by metadata table ID"""
        for attr_name in dir(cls.VALUE):
            if not attr_name.startswith('_') and getattr(cls.VALUE, attr_name) == id:
                return attr_name
        return None


class ClassEnum(str, Enum):
    """
    Class Enum with metadata-driven values
    These values correspond to the IDs in the classes metadata table
    """
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

    # Metadata table ID mappings
    class VALUE:
        PG = 1
        NURSERY = 2
        LKG = 3
        UKG = 4
        CLASS_1 = 5
        CLASS_2 = 6
        CLASS_3 = 7
        CLASS_4 = 8
        CLASS_5 = 9
        CLASS_6 = 10
        CLASS_7 = 11
        CLASS_8 = 12
        CLASS_9 = 13
        CLASS_10 = 14
        CLASS_11 = 15
        CLASS_12 = 16

    @classmethod
    def get_id_by_name(cls, name: str) -> int:
        """Get metadata table ID by enum name"""
        name_upper = name.upper()
        if hasattr(cls.VALUE, name_upper):
            return getattr(cls.VALUE, name_upper)
        return None

    @classmethod
    def get_name_by_id(cls, id: int) -> str:
        """Get enum name by metadata table ID"""
        for attr_name in dir(cls.VALUE):
            if not attr_name.startswith('_') and getattr(cls.VALUE, attr_name) == id:
                return attr_name
        return None


class StudentBase(BaseModel):
    admission_number: str = Field(..., min_length=1, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    gender_id: int = Field(..., description="Foreign key to genders table")
    class_id: int = Field(..., description="Foreign key to classes table")
    session_year_id: int = Field(..., description="Foreign key to session_years table")
    section: Optional[str] = Field(None, max_length=10)
    roll_number: Optional[str] = Field(None, max_length=20)
    blood_group: Optional[str] = Field(None, max_length=5)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    aadhar_no: Optional[str] = Field(None, max_length=12, pattern=r'^\d{12}$', description="12-digit Aadhar number")
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(default="India", max_length=100)
    father_name: str
    father_phone: Optional[str] = None
    father_email: Optional[EmailStr] = None
    father_occupation: Optional[str] = None
    mother_name: str
    mother_phone: Optional[str] = None
    mother_email: Optional[EmailStr] = None
    mother_occupation: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    admission_date: date
    previous_school: Optional[str] = None


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    admission_number: Optional[str] = Field(None, max_length=50)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[date] = None
    gender_id: Optional[int] = None
    class_id: Optional[int] = None
    session_year_id: Optional[int] = None
    section: Optional[str] = Field(None, max_length=10)
    roll_number: Optional[str] = Field(None, max_length=20)
    blood_group: Optional[str] = Field(None, max_length=5)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    aadhar_no: Optional[str] = Field(None, max_length=12, pattern=r'^\d{12}$', description="12-digit Aadhar number")
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    father_name: Optional[str] = None
    father_phone: Optional[str] = None
    father_email: Optional[EmailStr] = None
    father_occupation: Optional[str] = None
    mother_name: Optional[str] = None
    mother_phone: Optional[str] = None
    mother_email: Optional[EmailStr] = None
    mother_occupation: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    admission_date: Optional[date] = None
    previous_school: Optional[str] = None
    is_active: Optional[bool] = None


class StudentProfileUpdate(BaseModel):
    """
    Schema for student profile updates (limited fields that students can edit themselves)
    """
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    aadhar_no: Optional[str] = Field(None, max_length=12, pattern=r'^\d{12}$', description="12-digit Aadhar number")
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    previous_school: Optional[str] = None


class StudentInDBBase(StudentBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Student(StudentInDBBase):
    # Computed fields for API responses
    gender_name: Optional[str] = Field(None, description="Resolved gender name")
    class_name: Optional[str] = Field(None, description="Resolved class name")
    session_year_name: Optional[str] = Field(None, description="Resolved session year name")

    @classmethod
    def from_orm_with_metadata(cls, db_student):
        """Create Student schema with resolved metadata values"""
        student_data = {
            "id": db_student.id,
            "admission_number": db_student.admission_number,
            "first_name": db_student.first_name,
            "last_name": db_student.last_name,
            "date_of_birth": db_student.date_of_birth,
            "gender_id": db_student.gender_id,
            "class_id": db_student.class_id,
            "session_year_id": db_student.session_year_id,
            "section": db_student.section,
            "roll_number": db_student.roll_number,
            "blood_group": db_student.blood_group,
            "phone": db_student.phone,
            "email": db_student.email,
            "aadhar_no": db_student.aadhar_no,
            "address": db_student.address,
            "city": db_student.city,
            "state": db_student.state,
            "postal_code": db_student.postal_code,
            "country": db_student.country,
            "admission_date": db_student.admission_date,
            "father_name": db_student.father_name,
            "father_phone": db_student.father_phone,
            "father_email": db_student.father_email,
            "father_occupation": db_student.father_occupation,
            "mother_name": db_student.mother_name,
            "mother_phone": db_student.mother_phone,
            "mother_email": db_student.mother_email,
            "mother_occupation": db_student.mother_occupation,
            "emergency_contact_name": db_student.emergency_contact_name,
            "emergency_contact_phone": db_student.emergency_contact_phone,
            "emergency_contact_relation": db_student.emergency_contact_relation,
            "is_active": db_student.is_active,
            "created_at": db_student.created_at,
            "updated_at": db_student.updated_at,
            "gender_name": db_student.gender.name if db_student.gender else None,
            "class_name": db_student.class_ref.display_name if db_student.class_ref else None,
            "session_year_name": db_student.session_year.name if db_student.session_year else None
        }
        return cls(**student_data)


class StudentWithFees(Student):
    total_fees_due: Optional[float] = 0.0
    total_fees_paid: Optional[float] = 0.0
    fee_status: Optional[str] = "Unknown"


class StudentListResponse(BaseModel):
    students: List[Student]
    total: int
    page: int
    per_page: int
    total_pages: int
