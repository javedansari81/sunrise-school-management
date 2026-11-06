"""
Schemas for the platform admin API (school management).
"""
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.config import settings
from app.core.school_resolver import normalize_school_code


def _validate_code(value: str) -> str:
    code = normalize_school_code(value)
    if code is None or code != value.strip().lower():
        raise ValueError("School code must be 1-63 lowercase letters, digits or hyphens, not starting or ending with a hyphen")
    if code in settings.RESERVED_SUBDOMAINS:
        raise ValueError(f"'{code}' is reserved and cannot be a school code")
    return code


class PlatformLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class PlatformAdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str
    last_name: str


class PlatformAdminCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


class PlatformLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: PlatformAdminOut


class SchoolFields(BaseModel):
    """Editable school details."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    short_name: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    website: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = None
    timezone: Optional[str] = Field(None, max_length=64)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    academic_year_start_month: Optional[int] = Field(None, ge=1, le=12)


class SchoolAdminCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)


class SchoolCreate(SchoolFields):
    code: str = Field(..., description="Subdomain label, for example oakridge for oakridge.<base domain>")
    name: str = Field(..., min_length=1, max_length=255)
    admin: SchoolAdminCreate
    copy_lists_from: Optional[str] = Field(
        None,
        description="Code of the school whose lists (classes, session years, departments, ...) are copied. "
                    "Default: TEMPLATE_SCHOOL_CODE (sunrise)",
    )

    @field_validator("code")
    @classmethod
    def check_code(cls, value: str) -> str:
        return _validate_code(value)


class SchoolUpdate(SchoolFields):
    code: Optional[str] = Field(None, description="Changing the code changes the school's subdomain")

    @field_validator("code")
    @classmethod
    def check_code(cls, value: Optional[str]) -> Optional[str]:
        return None if value is None else _validate_code(value)


class SchoolOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    short_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    timezone: str
    currency: str
    academic_year_start_month: int
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SchoolSummary(SchoolOut):
    users: int = 0
    students: int = 0
    teachers: int = 0


class SchoolCreated(BaseModel):
    school: SchoolOut
    admin: PlatformAdminOut
    copied_from: Optional[str] = None
    copied_lists: Dict[str, int] = Field(default_factory=dict, description="Rows copied per list table")


class SchoolList(BaseModel):
    schools: List[SchoolSummary]
    total: int
