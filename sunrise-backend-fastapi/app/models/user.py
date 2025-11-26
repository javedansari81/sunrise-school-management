from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date, Text, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


# Import metadata models
# UserType is defined in metadata.py


class UserTypeEnum(str, enum.Enum):
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"
    STAFF = "STAFF"
    PARENT = "PARENT"

    @classmethod
    def _missing_(cls, value):
        """Handle case-insensitive enum lookup"""
        if isinstance(value, str):
            for member in cls:
                if member.value.upper() == value.upper():
                    return member
        return None


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # Changed from hashed_password to match DB schema
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)

    # Foreign key to metadata table
    user_type_id = Column(Integer, ForeignKey("user_types.id"), nullable=False)

    # Status and metadata
    is_active = Column(Boolean, default=True)

    # Soft Delete
    is_deleted = Column(Boolean, default=False, nullable=True)
    deleted_date = Column(DateTime(timezone=True), nullable=True)

    # Password tracking
    password_last_changed = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships to metadata
    user_type = relationship("UserType", back_populates="users")

    # Profile relationships (optional - for linking to student/teacher profiles)
    student_profile = relationship("Student", back_populates="user", uselist=False)
    teacher_profile = relationship("Teacher", back_populates="user", uselist=False)

    @property
    def user_type_enum(self) -> UserTypeEnum:
        """Convert user_type_id to UserTypeEnum for application logic"""
        try:
            # Use fallback logic based on user_type_id (avoid relationship access)
            if self.user_type_id == 1:
                user_type_name = "ADMIN"
            elif self.user_type_id == 2:
                user_type_name = "TEACHER"
            elif self.user_type_id == 3:
                user_type_name = "STUDENT"
            else:
                user_type_name = "ADMIN"

            # Handle case-insensitive conversion
            for member in UserTypeEnum:
                if member.value.upper() == user_type_name.upper():
                    return member
            # Fallback to admin if not found
            return UserTypeEnum.ADMIN
        except (AttributeError, TypeError):
            return UserTypeEnum.ADMIN
