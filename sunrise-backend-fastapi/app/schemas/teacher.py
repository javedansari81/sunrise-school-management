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


class QualificationEnum(str, Enum):
    """
    Qualification Enum with metadata-driven values
    These values correspond to the IDs in the qualifications metadata table
    """
    CERTIFICATE = "Certificate"
    DIPLOMA = "Diploma"
    BACHELOR = "Bachelor's Degree"
    MASTER = "Master's Degree"
    PHD = "PhD"
    OTHER = "Other"

    # Metadata table ID mappings
    class VALUE:
        CERTIFICATE = 1
        DIPLOMA = 2
        BACHELOR = 3
        MASTER = 4
        PHD = 5
        OTHER = 6

    @classmethod
    def get_id_by_name(cls, name: str) -> int:
        """Get metadata table ID by enum name"""
        name_upper = name.upper()
        if hasattr(cls.VALUE, name_upper):
            return getattr(cls.VALUE, name_upper)
        return None


class EmploymentStatusEnum(str, Enum):
    """
    Employment Status Enum with metadata-driven values
    These values correspond to the IDs in the employment_statuses metadata table
    """
    FULL_TIME = "Full Time"
    PART_TIME = "Part Time"
    CONTRACT = "Contract"
    SUBSTITUTE = "Substitute"
    PROBATION = "Probation"

    # Metadata table ID mappings
    class VALUE:
        FULL_TIME = 1
        PART_TIME = 2
        CONTRACT = 3
        SUBSTITUTE = 4
        PROBATION = 5

    @classmethod
    def get_id_by_name(cls, name: str) -> int:
        """Get metadata table ID by enum name"""
        name_upper = name.upper()
        if hasattr(cls.VALUE, name_upper):
            return getattr(cls.VALUE, name_upper)
        return None


class TeacherBase(BaseModel):
    employee_id: str = Field(..., min_length=1, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    gender_id: Optional[int] = Field(None, description="Foreign key to genders table")
    phone: str = Field(..., max_length=20)
    email: EmailStr
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(default="India", max_length=100)
    emergency_contact_name: Optional[str] = Field(None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relation: Optional[str] = Field(None, max_length=50)
    position: str = Field(..., max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    subjects: Optional[str] = None  # JSON string
    qualification_id: Optional[int] = Field(None, description="Foreign key to qualifications table")
    employment_status_id: int = Field(default=1, description="Foreign key to employment_statuses table")
    experience_years: int = Field(default=0, ge=0)
    joining_date: date
    class_teacher_of_id: Optional[int] = Field(None, description="Foreign key to classes table")
    classes_assigned: Optional[str] = None  # JSON string of class IDs
    salary: Optional[float] = Field(None, ge=0)
    bio: Optional[str] = None
    specializations: Optional[str] = None  # JSON string
    certifications: Optional[str] = None  # JSON string
    img: Optional[str] = None


class TeacherCreate(TeacherBase):
    pass


class TeacherUpdate(BaseModel):
    employee_id: Optional[str] = Field(None, max_length=50)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[date] = None
    gender_id: Optional[int] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    emergency_contact_name: Optional[str] = Field(None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relation: Optional[str] = Field(None, max_length=50)
    position: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    subjects: Optional[str] = None
    qualification_id: Optional[int] = None
    employment_status_id: Optional[int] = None
    experience_years: Optional[int] = Field(None, ge=0)
    joining_date: Optional[date] = None
    class_teacher_of_id: Optional[int] = None
    classes_assigned: Optional[str] = None
    salary: Optional[float] = Field(None, ge=0)
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
    # Computed fields for API responses
    gender_name: Optional[str] = Field(None, description="Resolved gender name")
    qualification_name: Optional[str] = Field(None, description="Resolved qualification name")
    employment_status_name: Optional[str] = Field(None, description="Resolved employment status name")
    class_teacher_of_name: Optional[str] = Field(None, description="Resolved class teacher of name")

    @classmethod
    def from_orm_with_metadata(cls, db_teacher):
        """Create Teacher schema with resolved metadata values"""
        teacher_data = {
            "id": db_teacher.id,
            "employee_id": db_teacher.employee_id,
            "first_name": db_teacher.first_name,
            "last_name": db_teacher.last_name,
            "date_of_birth": db_teacher.date_of_birth,
            "gender_id": db_teacher.gender_id,
            "phone": db_teacher.phone,
            "email": db_teacher.email,
            "address": db_teacher.address,
            "city": db_teacher.city,
            "state": db_teacher.state,
            "postal_code": db_teacher.postal_code,
            "country": db_teacher.country,
            "emergency_contact_name": db_teacher.emergency_contact_name,
            "emergency_contact_phone": db_teacher.emergency_contact_phone,
            "emergency_contact_relation": db_teacher.emergency_contact_relation,
            "position": db_teacher.position,
            "department": db_teacher.department,
            "subjects": db_teacher.subjects,
            "qualification_id": db_teacher.qualification_id,
            "employment_status_id": db_teacher.employment_status_id,
            "experience_years": db_teacher.experience_years,
            "joining_date": db_teacher.joining_date,
            "class_teacher_of_id": db_teacher.class_teacher_of_id,
            "classes_assigned": db_teacher.classes_assigned,
            "salary": float(db_teacher.salary) if db_teacher.salary else None,
            "bio": db_teacher.bio,
            "specializations": db_teacher.specializations,
            "certifications": db_teacher.certifications,
            "img": db_teacher.img,
            "is_active": db_teacher.is_active,
            "created_at": db_teacher.created_at,
            "updated_at": db_teacher.updated_at,
            "gender_name": db_teacher.gender.name if db_teacher.gender else None,
            "qualification_name": db_teacher.qualification.name if db_teacher.qualification else None,
            "employment_status_name": db_teacher.employment_status.name if db_teacher.employment_status else None,
            "class_teacher_of_name": db_teacher.class_teacher_of_ref.display_name if db_teacher.class_teacher_of_ref else None
        }
        return cls(**teacher_data)


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
