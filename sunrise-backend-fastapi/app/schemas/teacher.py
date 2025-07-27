from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from enum import Enum


class GenderEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class QualificationEnum(str, Enum):
    BACHELOR = "Bachelor's Degree"
    MASTER = "Master's Degree"
    PHD = "PhD"
    DIPLOMA = "Diploma"
    CERTIFICATE = "Certificate"
    OTHER = "Other"


class EmploymentStatusEnum(str, Enum):
    FULL_TIME = "Full Time"
    PART_TIME = "Part Time"
    CONTRACT = "Contract"
    SUBSTITUTE = "Substitute"


class TeacherBase(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    date_of_birth: date
    gender: GenderEnum
    email: EmailStr
    phone: str
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    position: str
    department: Optional[str] = None
    subjects: Optional[str] = None  # JSON string
    qualification: QualificationEnum
    experience_years: int = 0
    joining_date: date
    employment_status: EmploymentStatusEnum = EmploymentStatusEnum.FULL_TIME
    salary: Optional[float] = None
    bio: Optional[str] = None
    specializations: Optional[str] = None  # JSON string
    certifications: Optional[str] = None  # JSON string
    img: Optional[str] = None


class TeacherCreate(TeacherBase):
    pass


class TeacherUpdate(BaseModel):
    employee_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    subjects: Optional[str] = None
    qualification: Optional[QualificationEnum] = None
    experience_years: Optional[int] = None
    joining_date: Optional[date] = None
    employment_status: Optional[EmploymentStatusEnum] = None
    salary: Optional[float] = None
    bio: Optional[str] = None
    specializations: Optional[str] = None
    certifications: Optional[str] = None
    img: Optional[str] = None
    is_active: Optional[bool] = None


class TeacherInDBBase(TeacherBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Teacher(TeacherInDBBase):
    pass


class TeacherProfile(Teacher):
    subjects_list: Optional[List[str]] = []
    specializations_list: Optional[List[str]] = []
    certifications_list: Optional[List[str]] = []


class TeacherListResponse(BaseModel):
    teachers: List[Teacher]
    total: int
    page: int
    per_page: int
    total_pages: int


class TeacherDashboard(BaseModel):
    total_teachers: int
    active_teachers: int
    departments: List[dict]
    qualification_breakdown: List[dict]
    experience_breakdown: List[dict]
    recent_joinings: List[Teacher]
