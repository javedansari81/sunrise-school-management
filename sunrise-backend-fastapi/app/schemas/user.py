from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from enum import Enum


class UserTypeEnum(str, Enum):
    """
    User Type Enum with metadata-driven values
    These values correspond to the IDs in the user_types metadata table
    """
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"
    STAFF = "STAFF"
    PARENT = "PARENT"

    # Metadata table ID mappings
    class VALUE:
        ADMIN = 1
        TEACHER = 2
        STUDENT = 3
        STAFF = 4
        PARENT = 5

    @classmethod
    def _missing_(cls, value):
        """Handle case-insensitive enum lookup"""
        if isinstance(value, str):
            for member in cls:
                if member.value.upper() == value.upper():
                    return member
        return None

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


class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    user_type_id: int = Field(..., description="Foreign key to user_types table")


class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=6,
        max_length=72,  # bcrypt maximum byte length (approximate for most characters)
        description="User password (maximum 72 bytes due to bcrypt requirements)"
    )


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    user_type_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserInDBBase(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserInDBBase):
    # Computed fields for API responses
    user_type_name: Optional[str] = Field(None, description="Resolved user type name")

    @classmethod
    def from_orm_with_metadata(cls, db_user):
        """Create User schema with resolved metadata values"""
        user_data = {
            "id": db_user.id,
            "email": db_user.email,
            "first_name": db_user.first_name,
            "last_name": db_user.last_name,
            "phone": db_user.phone,
            "user_type_id": db_user.user_type_id,
            "is_active": db_user.is_active,
            "created_at": db_user.created_at,
            "updated_at": db_user.updated_at,
            "user_type_name": db_user.user_type.name if db_user.user_type else None
        }
        return cls(**user_data)


class UserInDB(UserInDBBase):
    password: str  # Changed from hashed_password to match DB schema


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
