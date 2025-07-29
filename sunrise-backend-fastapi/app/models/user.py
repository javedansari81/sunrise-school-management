from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class UserTypeEnum(str, enum.Enum):
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


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    mobile = Column(String(20), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    user_type = Column(String(20), nullable=False, default="admin")

    # Profile links
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)

    # Status and metadata
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    student_profile = relationship("Student", foreign_keys=[student_id])
    teacher_profile = relationship("Teacher", foreign_keys=[teacher_id])

    @property
    def user_type_enum(self) -> UserTypeEnum:
        """Convert string user_type to UserTypeEnum"""
        try:
            # Try direct enum lookup first
            for member in UserTypeEnum:
                if member.value.lower() == self.user_type.lower():
                    return member
            # Fallback to admin if not found
            return UserTypeEnum.ADMIN
        except (AttributeError, TypeError):
            return UserTypeEnum.ADMIN
