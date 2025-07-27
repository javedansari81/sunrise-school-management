from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from enum import Enum


class GenderEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class ClassEnum(str, Enum):
    PG = "PG"
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


class StudentBase(BaseModel):
    admission_number: str
    first_name: str
    last_name: str
    date_of_birth: date
    gender: GenderEnum
    current_class: ClassEnum
    section: Optional[str] = None
    roll_number: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
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
    admission_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    current_class: Optional[ClassEnum] = None
    section: Optional[str] = None
    roll_number: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
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


class StudentInDBBase(StudentBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Student(StudentInDBBase):
    pass


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
