from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum


class UserTypeEnum(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"
    STAFF = "staff"
    PARENT = "parent"

    @classmethod
    def _missing_(cls, value):
        """Handle case-insensitive enum lookup"""
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return None


class UserBase(BaseModel):
    first_name: str
    last_name: str
    mobile: str
    email: EmailStr
    user_type: UserTypeEnum = UserTypeEnum.ADMIN


class UserCreate(UserBase):
    password: str
    student_id: Optional[int] = None
    teacher_id: Optional[int] = None


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[EmailStr] = None
    user_type: Optional[UserTypeEnum] = None
    student_id: Optional[int] = None
    teacher_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserInDBBase(UserBase):
    id: int
    student_id: Optional[int] = None
    teacher_id: Optional[int] = None
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    password: str


class UserProfile(User):
    """Extended user profile with linked student/teacher data"""
    student_profile: Optional[dict] = None
    teacher_profile: Optional[dict] = None


class UserLoginResponse(BaseModel):
    user: User
    access_token: str
    token_type: str
    permissions: list
    profile_data: Optional[dict] = None
